"""
Configuration management for the ETL pipeline.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="transaction_db")
    user: str = Field(default="postgres")
    password: str = Field(default="")
    
    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class ETLConfig(BaseModel):
    """ETL pipeline configuration."""
    batch_size: int = Field(default=10000)
    max_retries: int = Field(default=3)
    retry_delay: int = Field(default=5)

class DataQualityConfig(BaseModel):
    """Data quality thresholds configuration."""
    max_null_percentage: float = Field(default=5.0)
    min_record_count: int = Field(default=1000)
    duplicate_threshold: float = Field(default=0.1)

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} | {function} | {message}")
    rotation: str = Field(default="1 day")
    retention: str = Field(default="30 days")

class Config(BaseModel):
    """Main configuration class."""
    database: DatabaseConfig
    etl: ETLConfig
    data_quality: DataQualityConfig
    logging: LoggingConfig
    
    @classmethod
    def load_config(cls, config_path: str = "config/config.yaml") -> "Config":
        """Load configuration from YAML file with environment variable substitution."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Substitute environment variables
        config_data = cls._substitute_env_vars(config_data)
        
        return cls(**config_data)
    
    @staticmethod
    def _substitute_env_vars(config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively substitute environment variables in config data."""
        if isinstance(config_data, dict):
            return {key: Config._substitute_env_vars(value) for key, value in config_data.items()}
        elif isinstance(config_data, list):
            return [Config._substitute_env_vars(item) for item in config_data]
        elif isinstance(config_data, str):
            # Handle ${VAR:default} syntax
            if config_data.startswith("${") and config_data.endswith("}"):
                var_spec = config_data[2:-1]
                if ":" in var_spec:
                    var_name, default_value = var_spec.split(":", 1)
                    return os.getenv(var_name, default_value)
                else:
                    return os.getenv(var_spec, config_data)
            return config_data
        else:
            return config_data

# Global config instance
config = Config.load_config()
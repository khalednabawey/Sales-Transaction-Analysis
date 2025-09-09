"""
Data extraction module for the ETL pipeline.
"""
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from sqlalchemy import create_engine, text
import requests
import json

class DataExtractor:
    """Handles data extraction from various sources."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the data extractor."""
        self.config = config or {}
        logger.info("DataExtractor initialized")
    
    def extract_from_csv(self, file_path: str, encoding: str = 'utf-8', **kwargs) -> pd.DataFrame:
        """
        Extract data from CSV file.
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding (default: utf-8)
            **kwargs: Additional pandas read_csv parameters
            
        Returns:
            DataFrame containing the extracted data
        """
        try:
            logger.info(f"Extracting data from CSV: {file_path}")
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            
            df = pd.read_csv(file_path, encoding=encoding, **kwargs)
            logger.info(f"Successfully extracted {len(df)} rows from {file_path}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting data from CSV {file_path}: {str(e)}")
            raise
    
    def extract_from_database(self, connection_string: str, query: str) -> pd.DataFrame:
        """
        Extract data from database using SQL query.
        
        Args:
            connection_string: Database connection string
            query: SQL query to execute
            
        Returns:
            DataFrame containing the query results
        """
        try:
            logger.info("Extracting data from database")
            engine = create_engine(connection_string)
            
            with engine.connect() as conn:
                df = pd.read_sql(text(query), conn)
                
            logger.info(f"Successfully extracted {len(df)} rows from database")
            return df
            
        except Exception as e:
            logger.error(f"Error extracting data from database: {str(e)}")
            raise
    
    def extract_from_api(self, url: str, headers: Optional[Dict[str, str]] = None, 
                        params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Extract data from REST API.
        
        Args:
            url: API endpoint URL
            headers: HTTP headers (optional)
            params: Query parameters (optional)
            
        Returns:
            DataFrame containing the API response data
        """
        try:
            logger.info(f"Extracting data from API: {url}")
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Handle nested JSON structures
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                else:
                    df = pd.DataFrame([data])
            else:
                raise ValueError("Unsupported API response format")
            
            logger.info(f"Successfully extracted {len(df)} rows from API")
            return df
            
        except Exception as e:
            logger.error(f"Error extracting data from API {url}: {str(e)}")
            raise
    
    def extract_from_json(self, file_path: str) -> pd.DataFrame:
        """
        Extract data from JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            DataFrame containing the extracted data
        """
        try:
            logger.info(f"Extracting data from JSON: {file_path}")
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"JSON file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("Unsupported JSON structure")
            
            logger.info(f"Successfully extracted {len(df)} rows from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error extracting data from JSON {file_path}: {str(e)}")
            raise
    
    def validate_extraction(self, df: pd.DataFrame, source_info: str) -> bool:
        """
        Validate extracted data.
        
        Args:
            df: Extracted DataFrame
            source_info: Information about the data source
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Basic validation checks
            if df.empty:
                logger.warning(f"No data extracted from {source_info}")
                return False
            
            if len(df) < 1:
                logger.warning(f"Insufficient data extracted from {source_info}: {len(df)} rows")
                return False
            
            logger.info(f"Data extraction validation passed for {source_info}: {len(df)} rows, {len(df.columns)} columns")
            return True
            
        except Exception as e:
            logger.error(f"Error validating extraction from {source_info}: {str(e)}")
            return False
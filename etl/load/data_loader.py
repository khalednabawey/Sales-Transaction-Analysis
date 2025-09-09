"""
Data loading module for the ETL pipeline.
"""
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from loguru import logger
from sqlalchemy import create_engine, text, MetaData, Table, inspect
import json

class DataLoader:
    """Handles data loading to various destinations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the data loader."""
        self.config = config or {}
        logger.info("DataLoader initialized")
    
    def load_to_database(self, df: pd.DataFrame, connection_string: str, table_name: str, 
                        if_exists: str = 'replace', index: bool = False, 
                        chunksize: Optional[int] = None) -> bool:
        """
        Load DataFrame to database table.
        
        Args:
            df: DataFrame to load
            connection_string: Database connection string
            table_name: Target table name
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
            index: Whether to write DataFrame index
            chunksize: Rows per chunk for large datasets
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(df)} rows to database table '{table_name}'")
            
            engine = create_engine(connection_string)
            
            # Use chunking for large datasets
            if chunksize is None:
                chunksize = self.config.get('batch_size', 10000)
            
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists=if_exists,
                index=index,
                chunksize=chunksize,
                method='multi'
            )
            
            # Verify the load
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
            
            logger.info(f"Successfully loaded {row_count} rows to table '{table_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data to database table '{table_name}': {str(e)}")
            return False
    
    def load_to_csv(self, df: pd.DataFrame, file_path: str, encoding: str = 'utf-8', 
                   index: bool = False, **kwargs) -> bool:
        """
        Load DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            file_path: Output file path
            encoding: File encoding
            index: Whether to write DataFrame index
            **kwargs: Additional pandas to_csv parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(df)} rows to CSV file '{file_path}'")
            
            # Ensure directory exists
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(file_path, encoding=encoding, index=index, **kwargs)
            
            # Verify file was created and has expected size
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.info(f"Successfully saved CSV file '{file_path}' ({file_size} bytes)")
                return True
            else:
                logger.error(f"CSV file was not created: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving CSV file '{file_path}': {str(e)}")
            return False
    
    def load_to_json(self, df: pd.DataFrame, file_path: str, orient: str = 'records', 
                    encoding: str = 'utf-8', **kwargs) -> bool:
        """
        Load DataFrame to JSON file.
        
        Args:
            df: DataFrame to save
            file_path: Output file path
            orient: JSON orientation ('records', 'index', 'values', etc.)
            encoding: File encoding
            **kwargs: Additional pandas to_json parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(df)} rows to JSON file '{file_path}'")
            
            # Ensure directory exists
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_json(file_path, orient=orient, **kwargs)
            
            # Verify file was created
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.info(f"Successfully saved JSON file '{file_path}' ({file_size} bytes)")
                return True
            else:
                logger.error(f"JSON file was not created: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving JSON file '{file_path}': {str(e)}")
            return False
    
    def load_to_parquet(self, df: pd.DataFrame, file_path: str, **kwargs) -> bool:
        """
        Load DataFrame to Parquet file.
        
        Args:
            df: DataFrame to save
            file_path: Output file path
            **kwargs: Additional pandas to_parquet parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(df)} rows to Parquet file '{file_path}'")
            
            # Ensure directory exists
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_parquet(file_path, **kwargs)
            
            # Verify file was created
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.info(f"Successfully saved Parquet file '{file_path}' ({file_size} bytes)")
                return True
            else:
                logger.error(f"Parquet file was not created: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving Parquet file '{file_path}': {str(e)}")
            return False
    
    def create_database_views(self, connection_string: str, view_definitions: Dict[str, str]) -> bool:
        """
        Create database views based on the original SQL analysis.
        
        Args:
            connection_string: Database connection string
            view_definitions: Dictionary of view_name -> SQL query
            
        Returns:
            True if all views created successfully, False otherwise
        """
        try:
            logger.info(f"Creating {len(view_definitions)} database views")
            
            engine = create_engine(connection_string)
            
            with engine.connect() as conn:
                for view_name, sql_query in view_definitions.items():
                    try:
                        # Drop view if exists, then create
                        conn.execute(text(f"DROP VIEW IF EXISTS {view_name}"))
                        conn.execute(text(f"CREATE VIEW {view_name} AS {sql_query}"))
                        conn.commit()
                        logger.info(f"Successfully created view '{view_name}'")
                        
                    except Exception as e:
                        logger.error(f"Error creating view '{view_name}': {str(e)}")
                        return False
            
            logger.info("All database views created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database views: {str(e)}")
            return False
    
    def load_analysis_results(self, results_dict: Dict[str, pd.DataFrame], 
                            output_dir: str, formats: List[str] = ['csv', 'json']) -> bool:
        """
        Load analysis results to multiple formats.
        
        Args:
            results_dict: Dictionary of analysis_name -> DataFrame
            output_dir: Output directory path
            formats: List of output formats ('csv', 'json', 'parquet')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(results_dict)} analysis results to {output_dir}")
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            success_count = 0
            
            for analysis_name, df in results_dict.items():
                if df.empty:
                    logger.warning(f"Skipping empty analysis result: {analysis_name}")
                    continue
                
                for format_type in formats:
                    file_path = output_path / f"{analysis_name}.{format_type}"
                    
                    if format_type == 'csv':
                        success = self.load_to_csv(df, str(file_path))
                    elif format_type == 'json':
                        success = self.load_to_json(df, str(file_path))
                    elif format_type == 'parquet':
                        success = self.load_to_parquet(df, str(file_path))
                    else:
                        logger.warning(f"Unsupported format: {format_type}")
                        continue
                    
                    if success:
                        success_count += 1
                    
            total_expected = len(results_dict) * len(formats)
            logger.info(f"Successfully loaded {success_count}/{total_expected} analysis result files")
            
            return success_count == total_expected
            
        except Exception as e:
            logger.error(f"Error loading analysis results: {str(e)}")
            return False
    
    def validate_load(self, df: pd.DataFrame, destination_info: str) -> bool:
        """
        Validate data load operation.
        
        Args:
            df: DataFrame that was loaded
            destination_info: Information about the destination
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            if df.empty:
                logger.warning(f"No data was loaded to {destination_info}")
                return False
            
            # Check for required columns (based on original schema)
            required_columns = ['transaction_id', 'timestamp', 'amount_inr']
            missing_columns = [col for col in required_columns if col in df.columns and df[col].isnull().all()]
            
            if missing_columns:
                logger.warning(f"Critical columns have all null values in {destination_info}: {missing_columns}")
                return False
            
            logger.info(f"Data load validation passed for {destination_info}: {len(df)} rows loaded")
            return True
            
        except Exception as e:
            logger.error(f"Error validating load to {destination_info}: {str(e)}")
            return False
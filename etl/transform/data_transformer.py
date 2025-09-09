"""
Data transformation module for the ETL pipeline.
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from loguru import logger
from datetime import datetime
import re

class DataTransformer:
    """Handles data transformations and cleaning operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the data transformer."""
        self.config = config or {}
        self.quality_metrics = {}
        logger.info("DataTransformer initialized")
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform comprehensive data cleaning.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        try:
            logger.info("Starting data cleaning process")
            initial_rows = len(df)
            
            # Create a copy to avoid modifying original data
            cleaned_df = df.copy()
            
            # Remove exact duplicates
            cleaned_df = self._remove_duplicates(cleaned_df)
            
            # Handle missing values
            cleaned_df = self._handle_missing_values(cleaned_df)
            
            # Clean and standardize data types
            cleaned_df = self._standardize_data_types(cleaned_df)
            
            # Remove outliers
            cleaned_df = self._remove_outliers(cleaned_df)
            
            final_rows = len(cleaned_df)
            logger.info(f"Data cleaning completed: {initial_rows} -> {final_rows} rows ({final_rows/initial_rows*100:.1f}% retained)")
            
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Error in data cleaning: {str(e)}")
            raise
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records."""
        initial_count = len(df)
        df_deduped = df.drop_duplicates()
        duplicates_removed = initial_count - len(df_deduped)
        
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate records")
            self.quality_metrics['duplicates_removed'] = duplicates_removed
        
        return df_deduped
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values based on column types and business logic."""
        missing_summary = df.isnull().sum()
        
        for column in df.columns:
            null_count = missing_summary[column]
            if null_count > 0:
                null_percentage = (null_count / len(df)) * 100
                logger.info(f"Column '{column}': {null_count} missing values ({null_percentage:.1f}%)")
                
                # Handle based on column type and name
                if column in ['transaction_id', 'timestamp']:
                    # Critical fields - remove rows with missing values
                    df = df.dropna(subset=[column])
                elif 'amount' in column.lower():
                    # Fill missing amounts with 0
                    df[column] = df[column].fillna(0)
                elif df[column].dtype == 'object':
                    # Fill categorical with 'Unknown'
                    df[column] = df[column].fillna('Unknown')
                elif df[column].dtype in ['int64', 'float64']:
                    # Fill numeric with median
                    df[column] = df[column].fillna(df[column].median())
                else:
                    # Default: fill with forward fill then backward fill
                    df[column] = df[column].fillna(method='ffill').fillna(method='bfill')
        
        return df
    
    def _standardize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize data types and formats."""
        # Convert timestamp columns
        timestamp_columns = ['timestamp', 'created_at', 'updated_at']
        for col in timestamp_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Standardize text columns
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col != 'timestamp':  # Skip timestamp if it's still object type
                df[col] = df[col].astype(str).str.strip().str.upper()
        
        # Convert boolean columns
        boolean_columns = ['fraud_flag', 'is_weekend']
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> pd.DataFrame:
        """Remove statistical outliers from numeric columns."""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if 'amount' in col.lower():  # Focus on amount columns
                initial_count = len(df)
                
                if method == 'iqr':
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                
                elif method == 'zscore':
                    z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                    df = df[z_scores < 3]
                
                outliers_removed = initial_count - len(df)
                if outliers_removed > 0:
                    logger.info(f"Removed {outliers_removed} outliers from column '{col}'")
        
        return df
    
    def create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features for analysis."""
        try:
            logger.info("Creating derived features")
            
            # Time-based features
            if 'timestamp' in df.columns:
                df['hour_of_day'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.day_name()
                df['is_weekend'] = df['timestamp'].dt.dayofweek >= 5
                df['month'] = df['timestamp'].dt.month
                df['quarter'] = df['timestamp'].dt.quarter
                df['year'] = df['timestamp'].dt.year
            
            # Amount-based features
            if 'amount_inr' in df.columns:
                df['amount_category'] = pd.cut(df['amount_inr'], 
                                             bins=[0, 100, 1000, 10000, float('inf')],
                                             labels=['Small', 'Medium', 'Large', 'Very Large'])
                df['log_amount'] = np.log1p(df['amount_inr'])
            
            # Age group interactions
            if 'sender_age_group' in df.columns and 'receiver_age_group' in df.columns:
                df['age_group_interaction'] = df['sender_age_group'] + '_to_' + df['receiver_age_group']
            
            # Bank relationship features
            if 'sender_bank' in df.columns and 'receiver_bank' in df.columns:
                df['same_bank_transfer'] = (df['sender_bank'] == df['receiver_bank'])
            
            logger.info(f"Created derived features. New shape: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error creating derived features: {str(e)}")
            raise
    
    def validate_transformations(self, original_df: pd.DataFrame, transformed_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data transformations.
        
        Args:
            original_df: Original DataFrame before transformation
            transformed_df: Transformed DataFrame
            
        Returns:
            Dictionary containing validation metrics
        """
        try:
            validation_results = {
                'original_rows': len(original_df),
                'transformed_rows': len(transformed_df),
                'retention_rate': len(transformed_df) / len(original_df) if len(original_df) > 0 else 0,
                'original_columns': len(original_df.columns),
                'transformed_columns': len(transformed_df.columns),
                'missing_values_original': original_df.isnull().sum().sum(),
                'missing_values_transformed': transformed_df.isnull().sum().sum(),
                'data_types_changed': {},
                'validation_passed': True
            }
            
            # Check data type changes
            for col in original_df.columns:
                if col in transformed_df.columns:
                    if original_df[col].dtype != transformed_df[col].dtype:
                        validation_results['data_types_changed'][col] = {
                            'original': str(original_df[col].dtype),
                            'transformed': str(transformed_df[col].dtype)
                        }
            
            # Validation checks
            if validation_results['retention_rate'] < 0.5:
                logger.warning("Low retention rate: {:.1f}%".format(validation_results['retention_rate'] * 100))
                validation_results['validation_passed'] = False
            
            if len(transformed_df) == 0:
                logger.error("No data remaining after transformation")
                validation_results['validation_passed'] = False
            
            logger.info(f"Transformation validation: {validation_results}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating transformations: {str(e)}")
            return {'validation_passed': False, 'error': str(e)}
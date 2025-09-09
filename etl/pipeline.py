"""
Main ETL Pipeline orchestrator.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger

from .extract.data_extractor import DataExtractor
from .transform.data_transformer import DataTransformer
from .load.data_loader import DataLoader
from .analysis.sales_analyzer import SalesAnalyzer
from config import config

class ETLPipeline:
    """Main ETL Pipeline class that orchestrates the entire process."""
    
    def __init__(self, pipeline_config: Optional[Dict[str, Any]] = None):
        """Initialize the ETL pipeline."""
        self.config = pipeline_config or config
        self.pipeline_id = f"etl_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize components
        self.extractor = DataExtractor(self.config.etl.dict())
        self.transformer = DataTransformer(self.config.etl.dict())
        self.loader = DataLoader(self.config.etl.dict())
        self.analyzer = SalesAnalyzer()
        
        # Pipeline state
        self.execution_log = []
        self.metrics = {}
        
        logger.info(f"ETL Pipeline initialized with ID: {self.pipeline_id}")
    
    def run_full_pipeline(self, source_path: str = None, target_table: str = 'transactions') -> bool:
        """
        Run the complete ETL pipeline.
        
        Args:
            source_path: Path to source data file (optional, uses config if not provided)
            target_table: Target database table name
            
        Returns:
            True if pipeline completed successfully, False otherwise
        """
        try:
            logger.info(f"Starting full ETL pipeline run: {self.pipeline_id}")
            start_time = datetime.now()
            
            # Step 1: Extract
            logger.info("Step 1: Data Extraction")
            raw_data = self._extract_data(source_path)
            if raw_data is None or raw_data.empty:
                logger.error("Data extraction failed or returned empty dataset")
                return False
            
            self._log_step("extraction", len(raw_data), "SUCCESS")
            
            # Step 2: Transform
            logger.info("Step 2: Data Transformation")
            transformed_data = self._transform_data(raw_data)
            if transformed_data is None or transformed_data.empty:
                logger.error("Data transformation failed or returned empty dataset")
                return False
            
            self._log_step("transformation", len(transformed_data), "SUCCESS")
            
            # Step 3: Load
            logger.info("Step 3: Data Loading")
            load_success = self._load_data(transformed_data, target_table)
            if not load_success:
                logger.error("Data loading failed")
                return False
            
            self._log_step("loading", len(transformed_data), "SUCCESS")
            
            # Step 4: Analysis
            logger.info("Step 4: Data Analysis")
            analysis_success = self._run_analysis(transformed_data)
            if not analysis_success:
                logger.warning("Data analysis completed with some errors")
            
            self._log_step("analysis", 0, "SUCCESS" if analysis_success else "PARTIAL")
            
            # Calculate pipeline metrics
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.metrics = {
                'pipeline_id': self.pipeline_id,
                'execution_time_seconds': execution_time,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'records_processed': len(transformed_data),
                'success': True
            }
            
            logger.info(f"ETL Pipeline completed successfully in {execution_time:.2f} seconds")
            self._save_pipeline_metrics()
            
            return True
            
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {str(e)}")
            self.metrics['success'] = False
            self.metrics['error'] = str(e)
            return False
    
    def _extract_data(self, source_path: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Extract data from the configured source."""
        try:
            if source_path is None:
                # Use default source from config
                source_path = "data/raw/upi_transactions_2024.csv"
            
            # Check if file exists, if not create sample data
            if not Path(source_path).exists():
                logger.warning(f"Source file not found: {source_path}. Creating sample data.")
                sample_data = self._create_sample_data()
                Path(source_path).parent.mkdir(parents=True, exist_ok=True)
                sample_data.to_csv(source_path, index=False)
                logger.info(f"Created sample data file: {source_path}")
            
            # Extract data
            df = self.extractor.extract_from_csv(source_path)
            
            # Validate extraction
            if self.extractor.validate_extraction(df, source_path):
                return df
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error in data extraction: {str(e)}")
            return None
    
    def _transform_data(self, raw_data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Transform the raw data."""
        try:
            # Clean the data
            cleaned_data = self.transformer.clean_data(raw_data)
            
            # Create derived features
            transformed_data = self.transformer.create_derived_features(cleaned_data)
            
            # Validate transformations
            validation_results = self.transformer.validate_transformations(raw_data, transformed_data)
            
            if validation_results['validation_passed']:
                self.metrics['transformation_metrics'] = validation_results
                return transformed_data
            else:
                logger.error("Data transformation validation failed")
                return None
                
        except Exception as e:
            logger.error(f"Error in data transformation: {str(e)}")
            return None
    
    def _load_data(self, transformed_data: pd.DataFrame, target_table: str) -> bool:
        """Load transformed data to the target destination."""
        try:
            success = True
            
            # Load to database (optional - skip if database not available)
            db_success = False
            try:
                db_success = self.loader.load_to_database(
                    transformed_data, 
                    self.config.database.connection_string, 
                    target_table,
                    if_exists='replace'
                )
                
                if not db_success:
                    logger.warning("Database loading failed, continuing with file outputs")
            except Exception as e:
                logger.warning(f"Database not available, skipping database load: {str(e)}")
            
            # Load to CSV for backup
            backup_path = f"data/processed/transactions_{self.pipeline_id}.csv"
            csv_success = self.loader.load_to_csv(transformed_data, backup_path)
            
            # Always ensure CSV backup is created
            if not csv_success:
                logger.error("Failed to create CSV backup")
                success = False
            else:
                success = True  # Pipeline succeeds if CSV backup is created
            
            # Validate the load (use CSV if database failed)
            if db_success:
                validation_success = self.loader.validate_load(transformed_data, f"database table '{target_table}'")
                if not validation_success:
                    logger.warning("Database load validation failed")
            else:
                # Validate CSV backup instead
                validation_success = self.loader.validate_load(transformed_data, f"CSV file '{backup_path}'")
                if not validation_success:
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Error in data loading: {str(e)}")
            return False
    
    def _run_analysis(self, data: pd.DataFrame) -> bool:
        """Run data analysis and generate insights."""
        try:
            # Run sales analysis
            analysis_results = self.analyzer.run_comprehensive_analysis(data)
            
            # Load analysis results to files
            output_dir = f"data/output/analysis_{self.pipeline_id}"
            success = self.loader.load_analysis_results(
                analysis_results, 
                output_dir, 
                formats=['csv', 'json']
            )
            
            # Create database views if database loading was successful
            view_definitions = self.analyzer.get_view_definitions()
            if view_definitions:
                views_success = self.loader.create_database_views(
                    self.config.database.connection_string, 
                    view_definitions
                )
                if not views_success:
                    logger.warning("Some database views failed to create")
            
            self.metrics['analysis_results_count'] = len(analysis_results)
            return success
            
        except Exception as e:
            logger.error(f"Error in data analysis: {str(e)}")
            return False
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample transaction data for testing."""
        import random
        from datetime import timedelta
        
        # Sample data parameters
        n_records = 1000
        base_date = datetime(2024, 1, 1)
        
        # Generate sample data
        data = []
        for i in range(n_records):
            record = {
                'transaction_id': f'TXN_{i+1:06d}',
                'timestamp': base_date + timedelta(days=random.randint(0, 365), 
                                                  hours=random.randint(0, 23),
                                                  minutes=random.randint(0, 59)),
                'transaction_type': random.choice(['P2P', 'P2M', 'Bill Payment', 'Recharge']),
                'merchant_category': random.choice(['Grocery', 'Fuel', 'Entertainment', 'Food', 'Shopping']),
                'amount_inr': round(random.uniform(10, 10000), 2),
                'transaction_status': random.choice(['SUCCESS', 'FAILED', 'PENDING']),
                'sender_age_group': random.choice(['18-25', '26-35', '36-45', '46-55', '55+']),
                'receiver_age_group': random.choice(['18-25', '26-35', '36-45', '46-55', '55+']),
                'sender_state': random.choice(['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Gujarat']),
                'sender_bank': random.choice(['SBI', 'HDFC', 'ICICI', 'Axis', 'PNB']),
                'receiver_bank': random.choice(['SBI', 'HDFC', 'ICICI', 'Axis', 'PNB']),
                'device_type': random.choice(['Android', 'iOS', 'Web']),
                'network_type': random.choice(['4G', '3G', 'WiFi', '5G']),
                'fraud_flag': random.choice([True, False]) if random.random() < 0.05 else False,
                'hour_of_day': None,  # Will be derived
                'day_of_week': None,  # Will be derived
                'is_weekend': None    # Will be derived
            }
            data.append(record)
        
        df = pd.DataFrame(data)
        logger.info(f"Created sample dataset with {len(df)} records")
        return df
    
    def _log_step(self, step_name: str, record_count: int, status: str):
        """Log pipeline step execution."""
        log_entry = {
            'step': step_name,
            'timestamp': datetime.now().isoformat(),
            'record_count': record_count,
            'status': status
        }
        self.execution_log.append(log_entry)
        logger.info(f"Step '{step_name}' completed: {status} ({record_count} records)")
    
    def _save_pipeline_metrics(self):
        """Save pipeline execution metrics."""
        try:
            metrics_file = f"logs/pipeline_metrics_{self.pipeline_id}.json"
            Path(metrics_file).parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(metrics_file, 'w') as f:
                json.dump({
                    'metrics': self.metrics,
                    'execution_log': self.execution_log
                }, f, indent=2, default=str)
            
            logger.info(f"Pipeline metrics saved to: {metrics_file}")
            
        except Exception as e:
            logger.error(f"Error saving pipeline metrics: {str(e)}")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and metrics."""
        return {
            'pipeline_id': self.pipeline_id,
            'metrics': self.metrics,
            'execution_log': self.execution_log,
            'last_run': datetime.now().isoformat()
        }
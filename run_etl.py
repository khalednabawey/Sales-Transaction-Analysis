"""
Main entry point for running the ETL pipeline.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from etl.pipeline import ETLPipeline
from loguru import logger

def main():
    """Main function to run the ETL pipeline."""
    try:
        logger.info("Starting Sales Transaction ETL Pipeline")
        
        # Initialize and run pipeline
        pipeline = ETLPipeline()
        success = pipeline.run_full_pipeline()
        
        if success:
            logger.info("ETL Pipeline completed successfully")
            
            # Display results
            status = pipeline.get_pipeline_status()
            print("\n" + "="*60)
            print("ETL PIPELINE EXECUTION SUMMARY")
            print("="*60)
            print(f"Pipeline ID: {status['pipeline_id']}")
            print(f"Records Processed: {status['metrics'].get('records_processed', 'N/A')}")
            print(f"Execution Time: {status['metrics'].get('execution_time_seconds', 'N/A')} seconds")
            print(f"Success: {status['metrics'].get('success', False)}")
            print("="*60)
            
        else:
            logger.error("ETL Pipeline failed")
            return 1
            
    except Exception as e:
        logger.error(f"Error running ETL pipeline: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
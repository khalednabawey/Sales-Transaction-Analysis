"""
Command Line Interface for the ETL Pipeline.
"""
import click
from pathlib import Path
from datetime import datetime
from loguru import logger

from etl.pipeline import ETLPipeline
from config import config

# Setup logging
def setup_logging():
    """Setup loguru logging configuration."""
    logger.remove()  # Remove default handler
    
    # Console logging
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format=config.logging.format,
        level=config.logging.level,
        colorize=True
    )
    
    # File logging
    log_file = Path("logs") / f"etl_{datetime.now().strftime('%Y%m%d')}.log"
    log_file.parent.mkdir(exist_ok=True)
    
    logger.add(
        sink=str(log_file),
        format=config.logging.format,
        level=config.logging.level,
        rotation=config.logging.rotation,
        retention=config.logging.retention
    )

@click.group()
@click.version_option(version="1.0.0", prog_name="Sales ETL Pipeline")
def cli():
    """Sales Transaction Analysis ETL Pipeline."""
    setup_logging()
    logger.info("ETL Pipeline CLI started")

@cli.command()
@click.option('--source', '-s', help='Source data file path')
@click.option('--target-table', '-t', default='transactions', help='Target database table name')
@click.option('--skip-analysis', is_flag=True, help='Skip analysis step')
def run(source, target_table, skip_analysis):
    """Run the complete ETL pipeline."""
    try:
        logger.info("Starting ETL pipeline run")
        
        # Initialize pipeline
        pipeline = ETLPipeline()
        
        # Run pipeline
        success = pipeline.run_full_pipeline(
            source_path=source,
            target_table=target_table
        )
        
        if success:
            logger.info("ETL pipeline completed successfully")
            
            # Display metrics
            status = pipeline.get_pipeline_status()
            click.echo("\n" + "="*50)
            click.echo("PIPELINE EXECUTION SUMMARY")
            click.echo("="*50)
            click.echo(f"Pipeline ID: {status['pipeline_id']}")
            click.echo(f"Records Processed: {status['metrics'].get('records_processed', 'N/A')}")
            click.echo(f"Execution Time: {status['metrics'].get('execution_time_seconds', 'N/A')} seconds")
            click.echo(f"Success: {status['metrics'].get('success', False)}")
            
        else:
            logger.error("ETL pipeline failed")
            click.echo("Pipeline execution failed. Check logs for details.")
            
    except Exception as e:
        logger.error(f"Error running ETL pipeline: {str(e)}")
        click.echo(f"Error: {str(e)}")

@cli.command()
@click.option('--source', '-s', required=True, help='Source data file path')
@click.option('--format', '-f', type=click.Choice(['csv', 'json', 'parquet']), default='csv', help='Output format')
@click.option('--output', '-o', help='Output file path')
def extract(source, format, output):
    """Extract data from source."""
    try:
        logger.info(f"Extracting data from {source}")
        
        from etl.extract.data_extractor import DataExtractor
        extractor = DataExtractor()
        
        # Extract data
        df = extractor.extract_from_csv(source)
        
        # Save extracted data
        if output is None:
            output = f"data/extracted/data.{format}"
        
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'csv':
            df.to_csv(output, index=False)
        elif format == 'json':
            df.to_json(output, orient='records', indent=2)
        elif format == 'parquet':
            df.to_parquet(output)
        
        click.echo(f"Data extracted successfully to {output}")
        click.echo(f"Records: {len(df)}, Columns: {len(df.columns)}")
        
    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        click.echo(f"Error: {str(e)}")

@cli.command()
@click.option('--source', '-s', required=True, help='Source data file path')
@click.option('--output', '-o', help='Output file path')
def transform(source, output):
    """Transform data."""
    try:
        logger.info(f"Transforming data from {source}")
        
        from etl.extract.data_extractor import DataExtractor
        from etl.transform.data_transformer import DataTransformer
        
        # Extract data
        extractor = DataExtractor()
        df = extractor.extract_from_csv(source)
        
        # Transform data
        transformer = DataTransformer()
        cleaned_df = transformer.clean_data(df)
        transformed_df = transformer.create_derived_features(cleaned_df)
        
        # Save transformed data
        if output is None:
            output = "data/processed/transformed_data.csv"
        
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        transformed_df.to_csv(output, index=False)
        
        click.echo(f"Data transformed successfully to {output}")
        click.echo(f"Original: {len(df)} records, Transformed: {len(transformed_df)} records")
        
    except Exception as e:
        logger.error(f"Error transforming data: {str(e)}")
        click.echo(f"Error: {str(e)}")

@cli.command()
@click.option('--source', '-s', required=True, help='Source data file path')
@click.option('--table', '-t', default='transactions', help='Target table name')
@click.option('--connection', '-c', help='Database connection string (optional)')
def load(source, table, connection):
    """Load data to database."""
    try:
        logger.info(f"Loading data from {source} to table {table}")
        
        from etl.extract.data_extractor import DataExtractor
        from etl.load.data_loader import DataLoader
        
        # Extract data
        extractor = DataExtractor()
        df = extractor.extract_from_csv(source)
        
        # Load data
        loader = DataLoader()
        connection_string = connection or config.database.connection_string
        
        success = loader.load_to_database(df, connection_string, table)
        
        if success:
            click.echo(f"Data loaded successfully to table {table}")
            click.echo(f"Records loaded: {len(df)}")
        else:
            click.echo("Data loading failed")
            
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        click.echo(f"Error: {str(e)}")

@cli.command()
@click.option('--source', '-s', required=True, help='Source data file path')
@click.option('--output-dir', '-o', default='data/output/analysis', help='Output directory for analysis results')
def analyze(source, output_dir):
    """Run data analysis."""
    try:
        logger.info(f"Analyzing data from {source}")
        
        from etl.extract.data_extractor import DataExtractor
        from etl.transform.data_transformer import DataTransformer
        from etl.analysis.sales_analyzer import SalesAnalyzer
        from etl.load.data_loader import DataLoader
        
        # Extract and transform data
        extractor = DataExtractor()
        transformer = DataTransformer()
        df = extractor.extract_from_csv(source)
        
        # Basic transformations for analysis
        cleaned_df = transformer.clean_data(df)
        transformed_df = transformer.create_derived_features(cleaned_df)
        
        # Run analysis
        analyzer = SalesAnalyzer()
        results = analyzer.run_comprehensive_analysis(transformed_df)
        
        # Save results
        loader = DataLoader()
        success = loader.load_analysis_results(results, output_dir)
        
        if success:
            click.echo(f"Analysis completed successfully")
            click.echo(f"Results saved to: {output_dir}")
            click.echo(f"Analysis reports generated: {len(results)}")
        else:
            click.echo("Analysis completed with some errors")
            
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        click.echo(f"Error: {str(e)}")

@cli.command()
def status():
    """Show pipeline status and recent runs."""
    try:
        import json
        from pathlib import Path
        
        logs_dir = Path("logs")
        if not logs_dir.exists():
            click.echo("No pipeline runs found")
            return
        
        # Find recent metric files
        metric_files = list(logs_dir.glob("pipeline_metrics_*.json"))
        
        if not metric_files:
            click.echo("No pipeline metrics found")
            return
        
        # Show most recent runs
        metric_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        click.echo("RECENT PIPELINE RUNS")
        click.echo("="*50)
        
        for i, metric_file in enumerate(metric_files[:5]):  # Show last 5 runs
            try:
                with open(metric_file, 'r') as f:
                    data = json.load(f)
                
                metrics = data.get('metrics', {})
                click.echo(f"\nRun {i+1}: {metrics.get('pipeline_id', 'Unknown')}")
                click.echo(f"  Start Time: {metrics.get('start_time', 'Unknown')}")
                click.echo(f"  Execution Time: {metrics.get('execution_time_seconds', 'Unknown')} seconds")
                click.echo(f"  Records Processed: {metrics.get('records_processed', 'Unknown')}")
                click.echo(f"  Success: {metrics.get('success', 'Unknown')}")
                
                if not metrics.get('success', False):
                    click.echo(f"  Error: {metrics.get('error', 'Unknown error')}")
                    
            except Exception as e:
                click.echo(f"Error reading {metric_file}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error showing status: {str(e)}")
        click.echo(f"Error: {str(e)}")

@cli.command()
def init():
    """Initialize the ETL pipeline environment."""
    try:
        logger.info("Initializing ETL pipeline environment")
        
        # Create directory structure
        directories = [
            "data/raw",
            "data/processed", 
            "data/output/reports",
            "data/output/analysis",
            "logs",
            "config"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            click.echo(f"Created directory: {directory}")
        
        # Create .env file if it doesn't exist
        env_file = Path(".env")
        if not env_file.exists():
            env_example = Path(".env.example")
            if env_example.exists():
                import shutil
                shutil.copy(env_example, env_file)
                click.echo("Created .env file from .env.example")
                click.echo("Please update .env with your configuration values")
        
        click.echo("\nETL pipeline environment initialized successfully!")
        click.echo("Next steps:")
        click.echo("1. Update .env file with your database credentials")
        click.echo("2. Place your data files in data/raw/")
        click.echo("3. Run 'python -m scripts.cli run' to start the pipeline")
        
    except Exception as e:
        logger.error(f"Error initializing environment: {str(e)}")
        click.echo(f"Error: {str(e)}")

if __name__ == '__main__':
    cli()
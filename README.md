# Sales Transaction Analysis - ETL Pipeline

A comprehensive data engineering project featuring a full ETL (Extract, Transform, Load) pipeline for sales transaction analysis. This project transforms raw transaction data into actionable business insights through automated data processing, quality validation, and comprehensive analytics.

## 🚀 Features

### Data Engineering Pipeline
- **Extract**: Support for multiple data sources (CSV, JSON, APIs, databases)
- **Transform**: Advanced data cleaning, validation, and feature engineering
- **Load**: Automated loading to databases, files, and analysis outputs
- **Orchestration**: Complete pipeline management with error handling and monitoring

### Data Analysis & Insights
- Sales performance trends and patterns
- Customer behavior analysis
- Fraud detection and risk assessment
- Geographic and demographic insights
- Device and network usage patterns
- Banking relationship analysis

### Data Quality & Monitoring
- Automated data validation and quality checks
- Comprehensive logging and error tracking
- Pipeline execution metrics and monitoring
- Data lineage and audit trails

## 🏗️ Architecture

```
Sales-Transaction-Analysis/
├── etl/                     # ETL Pipeline Components
│   ├── extract/            # Data extraction modules
│   ├── transform/          # Data transformation and cleaning
│   ├── load/              # Data loading and output
│   ├── analysis/          # Business analysis modules
│   └── pipeline.py        # Main pipeline orchestrator
├── config/                 # Configuration management
├── scripts/               # CLI tools and utilities
├── tests/                 # Unit tests
├── data/                  # Data directories
│   ├── raw/              # Source data
│   ├── processed/        # Transformed data
│   └── output/           # Analysis results
└── logs/                 # Pipeline logs and metrics
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (optional, for database features)
- Git

## 🔧 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/khalednabawey/Sales-Transaction-Analysis.git
cd Sales-Transaction-Analysis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize the environment:**
```bash
python -m scripts.cli init
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🚀 Quick Start

### Option 1: Run Complete Pipeline
```bash
python run_etl.py
```

### Option 2: Use CLI Commands
```bash
# Initialize environment
python -m scripts.cli init

# Run full pipeline
python -m scripts.cli run --source data/raw/transactions.csv

# Run individual steps
python -m scripts.cli extract --source data/raw/transactions.csv
python -m scripts.cli transform --source data/raw/transactions.csv
python -m scripts.cli load --source data/processed/transformed_data.csv
python -m scripts.cli analyze --source data/processed/transformed_data.csv

# Check pipeline status
python -m scripts.cli status
```

## 📊 Data Schema

The pipeline expects transaction data with the following structure:

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | String | Unique transaction identifier |
| timestamp | DateTime | Transaction timestamp |
| transaction_type | String | Type of transaction (P2P, P2M, etc.) |
| merchant_category | String | Merchant category |
| amount_inr | Float | Transaction amount in INR |
| transaction_status | String | Transaction status |
| sender_age_group | String | Sender age group |
| receiver_age_group | String | Receiver age group |
| sender_state | String | Sender state |
| sender_bank | String | Sender bank |
| receiver_bank | String | Receiver bank |
| device_type | String | Device type |
| network_type | String | Network type |
| fraud_flag | Boolean | Fraud indicator |

## 🔄 ETL Pipeline Details

### Extract Phase
- **CSV Files**: Automated parsing with encoding detection
- **JSON APIs**: RESTful API integration with authentication
- **Databases**: Direct SQL query execution
- **Validation**: Data integrity and completeness checks

### Transform Phase
- **Data Cleaning**: Duplicate removal, missing value handling
- **Standardization**: Data type conversion and formatting
- **Feature Engineering**: Derived metrics and calculated fields
- **Quality Validation**: Statistical outlier detection

### Load Phase
- **Database Loading**: Efficient bulk insert operations
- **File Outputs**: Multiple format support (CSV, JSON, Parquet)
- **Analysis Results**: Automated report generation
- **Backup & Recovery**: Data versioning and rollback

## 📈 Analysis Modules

### Time-Based Analysis
- Peak transaction hours and days
- Seasonal trends and patterns
- Weekend vs. weekday comparisons

### Transaction Analysis
- Transaction type performance
- Merchant category insights
- Amount distribution analysis

### Fraud Detection
- Risk pattern identification
- Anomaly detection algorithms
- Fraud rate analysis by dimensions

### Geographic Analysis
- State-wise transaction patterns
- Regional performance metrics

### Banking Analysis
- Inter-bank transaction flows
- Bank preference patterns
- Same-bank vs. cross-bank analysis

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=etl --cov-report=html

# Run specific test file
python -m pytest tests/test_etl.py -v
```

## 📝 Configuration

### Database Configuration
Update `config/config.yaml` or environment variables:
```yaml
database:
  host: localhost
  port: 5432
  name: transaction_db
  user: postgres
  password: ${DB_PASSWORD}
```

### Pipeline Settings
```yaml
etl:
  batch_size: 10000
  max_retries: 3
  retry_delay: 5

data_quality:
  max_null_percentage: 5.0
  min_record_count: 1000
  duplicate_threshold: 0.1
```

## 📊 Monitoring & Logging

### Pipeline Metrics
- Execution time and performance
- Data quality indicators
- Error rates and handling
- Resource utilization

### Log Management
- Structured logging with rotation
- Error tracking and alerting
- Audit trail maintenance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Original Analysis Components

The project maintains compatibility with the original SQL-based analysis:
- `Data-Load.sql` - Original database schema and loading
- `Data-Exploration-Cleaning.sql` - Data quality procedures
- `Data-Analysis.sql` - Business intelligence views
- `Transaction-Analysis-Dashboard.pbix` - Power BI dashboard

## 🚀 Future Enhancements

- [ ] Apache Airflow integration for advanced scheduling
- [ ] Real-time streaming data processing
- [ ] Machine learning model integration
- [ ] Advanced visualization dashboards
- [ ] API endpoints for real-time analytics
- [ ] Multi-source data federation
- [ ] Advanced security and encryption

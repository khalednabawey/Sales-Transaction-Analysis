"""
Unit tests for the ETL pipeline components.
"""
import pytest
import pandas as pd
import tempfile
from pathlib import Path
from datetime import datetime

from etl.extract.data_extractor import DataExtractor
from etl.transform.data_transformer import DataTransformer
from etl.load.data_loader import DataLoader
from etl.analysis.sales_analyzer import SalesAnalyzer

class TestDataExtractor:
    """Test cases for DataExtractor."""
    
    def test_csv_extraction(self):
        """Test CSV data extraction."""
        # Create test data
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'value': [10.5, 20.3, 15.7]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            
            # Test extraction
            extractor = DataExtractor()
            extracted_df = extractor.extract_from_csv(f.name)
            
            assert len(extracted_df) == 3
            assert list(extracted_df.columns) == ['id', 'name', 'value']
            
        # Clean up
        Path(f.name).unlink()
    
    def test_validation(self):
        """Test data extraction validation."""
        extractor = DataExtractor()
        
        # Test with valid data
        valid_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        assert extractor.validate_extraction(valid_df, "test_source") == True
        
        # Test with empty data
        empty_df = pd.DataFrame()
        assert extractor.validate_extraction(empty_df, "test_source") == False

class TestDataTransformer:
    """Test cases for DataTransformer."""
    
    def test_data_cleaning(self):
        """Test data cleaning functionality."""
        # Create test data with issues
        test_data = pd.DataFrame({
            'transaction_id': ['T1', 'T2', 'T3', 'T2'],  # Duplicate
            'amount_inr': [100.0, None, 200.0, 150.0],   # Missing value
            'timestamp': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-02'],
            'category': ['A', 'B', 'C', 'B']
        })
        
        transformer = DataTransformer()
        cleaned_df = transformer.clean_data(test_data)
        
        # Check that duplicates are removed
        assert len(cleaned_df) < len(test_data)
        
        # Check that missing values are handled
        assert not cleaned_df['amount_inr'].isnull().any()
    
    def test_derived_features(self):
        """Test derived feature creation."""
        test_data = pd.DataFrame({
            'transaction_id': ['T1', 'T2', 'T3'],
            'timestamp': pd.to_datetime(['2024-01-01 10:30:00', '2024-01-02 15:45:00', '2024-01-03 09:15:00']),
            'amount_inr': [100.0, 200.0, 150.0],
            'sender_age_group': ['25-35', '35-45', '25-35'],
            'receiver_age_group': ['35-45', '25-35', '45-55']
        })
        
        transformer = DataTransformer()
        transformed_df = transformer.create_derived_features(test_data)
        
        # Check that time-based features are created
        assert 'hour_of_day' in transformed_df.columns
        assert 'day_of_week' in transformed_df.columns
        assert 'is_weekend' in transformed_df.columns
        
        # Check that age group interaction is created
        assert 'age_group_interaction' in transformed_df.columns

class TestDataLoader:
    """Test cases for DataLoader."""
    
    def test_csv_loading(self):
        """Test CSV data loading."""
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10.5, 20.3, 15.7]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            loader = DataLoader()
            success = loader.load_to_csv(test_data, f.name)
            
            assert success == True
            assert Path(f.name).exists()
            
            # Verify content
            loaded_df = pd.read_csv(f.name)
            assert len(loaded_df) == 3
            
        # Clean up
        Path(f.name).unlink()
    
    def test_json_loading(self):
        """Test JSON data loading."""
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10.5, 20.3, 15.7]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            loader = DataLoader()
            success = loader.load_to_json(test_data, f.name)
            
            assert success == True
            assert Path(f.name).exists()
            
        # Clean up
        Path(f.name).unlink()

class TestSalesAnalyzer:
    """Test cases for SalesAnalyzer."""
    
    def test_comprehensive_analysis(self):
        """Test comprehensive analysis."""
        # Create sample transaction data
        test_data = pd.DataFrame({
            'transaction_id': ['T1', 'T2', 'T3', 'T4', 'T5'],
            'timestamp': pd.to_datetime([
                '2024-01-01 10:30:00', '2024-01-01 15:45:00', 
                '2024-01-02 09:15:00', '2024-01-02 14:20:00', 
                '2024-01-03 11:10:00'
            ]),
            'amount_inr': [100.0, 200.0, 150.0, 300.0, 175.0],
            'transaction_type': ['P2P', 'P2M', 'P2P', 'Bill Payment', 'P2M'],
            'merchant_category': ['Grocery', 'Fuel', 'Grocery', 'Utilities', 'Food'],
            'fraud_flag': [False, False, True, False, False],
            'sender_age_group': ['25-35', '35-45', '25-35', '45-55', '35-45'],
            'receiver_age_group': ['35-45', '25-35', '45-55', '25-35', '35-45'],
            'sender_state': ['Maharashtra', 'Karnataka', 'Maharashtra', 'Delhi', 'Karnataka'],
            'sender_bank': ['SBI', 'HDFC', 'SBI', 'ICICI', 'HDFC'],
            'receiver_bank': ['HDFC', 'SBI', 'ICICI', 'SBI', 'HDFC'],
            'device_type': ['Android', 'iOS', 'Android', 'Web', 'iOS'],
            'network_type': ['4G', 'WiFi', '4G', '5G', 'WiFi'],
            'hour_of_day': [10, 15, 9, 14, 11],
            'day_of_week': ['Monday', 'Monday', 'Tuesday', 'Tuesday', 'Wednesday'],
            'is_weekend': [False, False, False, False, False]
        })
        
        analyzer = SalesAnalyzer()
        results = analyzer.run_comprehensive_analysis(test_data)
        
        # Check that analysis results are generated
        assert isinstance(results, dict)
        assert len(results) > 0
        
        # Check for expected analysis categories
        expected_analyses = [
            'peak_hours', 'transaction_type_analysis', 'fraud_summary',
            'state_wise_analysis', 'device_type_analysis'
        ]
        
        # At least some of these should be present
        found_analyses = [analysis for analysis in expected_analyses if analysis in results]
        assert len(found_analyses) > 0
        
        # Each result should be a DataFrame
        for analysis_name, result_df in results.items():
            assert isinstance(result_df, pd.DataFrame)

# Integration test
def test_pipeline_integration():
    """Test basic pipeline integration."""
    # Create sample data
    sample_data = pd.DataFrame({
        'transaction_id': ['T1', 'T2', 'T3'],
        'timestamp': ['2024-01-01 10:30:00', '2024-01-02 15:45:00', '2024-01-03 09:15:00'],
        'amount_inr': [100.0, 200.0, 150.0],
        'transaction_type': ['P2P', 'P2M', 'P2P'],
        'merchant_category': ['Grocery', 'Fuel', 'Grocery'],
        'fraud_flag': [False, False, True],
        'sender_age_group': ['25-35', '35-45', '25-35'],
        'receiver_age_group': ['35-45', '25-35', '45-55'],
        'sender_state': ['Maharashtra', 'Karnataka', 'Maharashtra'],
        'sender_bank': ['SBI', 'HDFC', 'SBI'],
        'receiver_bank': ['HDFC', 'SBI', 'ICICI'],
        'device_type': ['Android', 'iOS', 'Android'],
        'network_type': ['4G', 'WiFi', '4G'],
        'transaction_status': ['SUCCESS', 'SUCCESS', 'FAILED']
    })
    
    # Test extract -> transform -> analyze flow
    extractor = DataExtractor()
    transformer = DataTransformer()
    analyzer = SalesAnalyzer()
    
    # Transform data
    cleaned_data = transformer.clean_data(sample_data)
    transformed_data = transformer.create_derived_features(cleaned_data)
    
    # Analyze data
    results = analyzer.run_comprehensive_analysis(transformed_data)
    
    # Verify results
    assert len(transformed_data) >= len(sample_data) * 0.5  # Allow for some data cleaning
    assert len(results) > 0
    assert all(isinstance(df, pd.DataFrame) for df in results.values())

if __name__ == "__main__":
    pytest.main([__file__])
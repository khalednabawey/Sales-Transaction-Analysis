"""
Sales analysis module for generating business insights.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from loguru import logger

class SalesAnalyzer:
    """Handles comprehensive sales transaction analysis."""
    
    def __init__(self):
        """Initialize the sales analyzer."""
        logger.info("SalesAnalyzer initialized")
    
    def run_comprehensive_analysis(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Run comprehensive analysis on sales transaction data.
        
        Args:
            df: Cleaned and transformed transaction data
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            logger.info("Starting comprehensive sales analysis")
            
            analysis_results = {}
            
            # Time-based analysis
            analysis_results.update(self._analyze_time_patterns(df))
            
            # Transaction analysis
            analysis_results.update(self._analyze_transactions(df))
            
            # Geographic analysis
            analysis_results.update(self._analyze_geography(df))
            
            # Fraud analysis
            analysis_results.update(self._analyze_fraud_patterns(df))
            
            # Banking analysis
            analysis_results.update(self._analyze_banking_patterns(df))
            
            # Customer behavior analysis
            analysis_results.update(self._analyze_customer_behavior(df))
            
            # Device and network analysis
            analysis_results.update(self._analyze_device_network(df))
            
            logger.info(f"Completed analysis with {len(analysis_results)} result sets")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return {}
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze time-based patterns in transactions."""
        results = {}
        
        try:
            # Peak hours analysis
            if 'hour_of_day' in df.columns:
                peak_hours = df.groupby('hour_of_day').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean']
                }).round(2)
                peak_hours.columns = ['transaction_count', 'total_amount', 'avg_amount']
                peak_hours = peak_hours.reset_index().sort_values('transaction_count', ascending=False)
                results['peak_hours'] = peak_hours
            
            # Day of week trends
            if 'day_of_week' in df.columns:
                day_trends = df.groupby('day_of_week').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean']
                }).round(2)
                day_trends.columns = ['transaction_count', 'total_amount', 'avg_amount']
                day_trends = day_trends.reset_index().sort_values('transaction_count', ascending=False)
                results['day_of_week_trends'] = day_trends
            
            # Weekend vs weekday comparison
            if 'is_weekend' in df.columns:
                weekend_analysis = df.groupby('is_weekend').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean'],
                    'fraud_flag': 'sum'
                }).round(2)
                weekend_analysis.columns = ['total_transactions', 'total_amount', 'avg_amount', 'fraud_count']
                weekend_analysis['fraud_rate'] = (weekend_analysis['fraud_count'] / weekend_analysis['total_transactions'] * 100).round(2)
                results['weekday_vs_weekend'] = weekend_analysis.reset_index()
            
            # Monthly trends
            if 'timestamp' in df.columns:
                df['month'] = df['timestamp'].dt.month
                monthly_trends = df.groupby('month').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean']
                }).round(2)
                monthly_trends.columns = ['transaction_count', 'total_amount', 'avg_amount']
                results['monthly_trends'] = monthly_trends.reset_index()
            
        except Exception as e:
            logger.error(f"Error in time pattern analysis: {str(e)}")
        
        return results
    
    def _analyze_transactions(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze transaction patterns and types."""
        results = {}
        
        try:
            # Transaction type analysis
            if 'transaction_type' in df.columns:
                type_analysis = df.groupby('transaction_type').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean'],
                    'fraud_flag': 'sum'
                }).round(2)
                type_analysis.columns = ['transaction_count', 'total_amount', 'avg_amount', 'fraud_count']
                type_analysis['fraud_rate'] = (type_analysis['fraud_count'] / type_analysis['transaction_count'] * 100).round(2)
                results['transaction_type_analysis'] = type_analysis.reset_index()
            
            # Merchant category analysis
            if 'merchant_category' in df.columns:
                merchant_analysis = df.groupby('merchant_category').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean'],
                    'fraud_flag': 'sum'
                }).round(2)
                merchant_analysis.columns = ['transaction_count', 'total_amount', 'avg_amount', 'fraud_count']
                merchant_analysis['fraud_rate'] = (merchant_analysis['fraud_count'] / merchant_analysis['transaction_count'] * 100).round(2)
                results['merchant_category_analysis'] = merchant_analysis.reset_index()
            
            # Transaction status analysis
            if 'transaction_status' in df.columns:
                status_analysis = df.groupby('transaction_status').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean']
                }).round(2)
                status_analysis.columns = ['transaction_count', 'total_amount', 'avg_amount']
                results['transaction_status_analysis'] = status_analysis.reset_index()
            
            # Amount distribution analysis
            if 'amount_inr' in df.columns:
                amount_stats = df['amount_inr'].describe().to_frame('statistics')
                results['amount_distribution'] = amount_stats
            
        except Exception as e:
            logger.error(f"Error in transaction analysis: {str(e)}")
        
        return results
    
    def _analyze_geography(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze geographic patterns."""
        results = {}
        
        try:
            # State-wise analysis
            if 'sender_state' in df.columns:
                state_analysis = df.groupby('sender_state').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean'],
                    'fraud_flag': 'sum'
                }).round(2)
                state_analysis.columns = ['transaction_count', 'total_amount', 'avg_amount', 'fraud_count']
                state_analysis['fraud_rate'] = (state_analysis['fraud_count'] / state_analysis['transaction_count'] * 100).round(2)
                results['state_wise_analysis'] = state_analysis.reset_index().sort_values('total_amount', ascending=False)
            
        except Exception as e:
            logger.error(f"Error in geographic analysis: {str(e)}")
        
        return results
    
    def _analyze_fraud_patterns(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze fraud patterns and risk factors."""
        results = {}
        
        try:
            if 'fraud_flag' not in df.columns:
                return results
            
            # Overall fraud statistics
            total_transactions = len(df)
            fraud_transactions = df['fraud_flag'].sum()
            fraud_rate = (fraud_transactions / total_transactions * 100).round(2)
            
            fraud_summary = pd.DataFrame({
                'metric': ['total_transactions', 'fraud_transactions', 'fraud_rate_percent'],
                'value': [total_transactions, fraud_transactions, fraud_rate]
            })
            results['fraud_summary'] = fraud_summary
            
            # Fraud by age group
            if 'sender_age_group' in df.columns:
                age_fraud = df.groupby('sender_age_group').agg({
                    'transaction_id': 'count',
                    'fraud_flag': 'sum'
                })
                age_fraud['fraud_rate'] = (age_fraud['fraud_flag'] / age_fraud['transaction_id'] * 100).round(2)
                age_fraud.columns = ['total_transactions', 'fraud_count', 'fraud_rate']
                results['fraud_by_age_group'] = age_fraud.reset_index().sort_values('fraud_rate', ascending=False)
            
            # High-risk merchant categories
            if 'merchant_category' in df.columns:
                merchant_fraud = df.groupby('merchant_category').agg({
                    'transaction_id': 'count',
                    'fraud_flag': 'sum',
                    'amount_inr': 'sum'
                })
                merchant_fraud['fraud_rate'] = (merchant_fraud['fraud_flag'] / merchant_fraud['transaction_id'] * 100).round(2)
                merchant_fraud['fraud_amount_percent'] = (
                    df[df['fraud_flag'] == True].groupby('merchant_category')['amount_inr'].sum() / 
                    merchant_fraud['amount_inr'] * 100
                ).fillna(0).round(2)
                merchant_fraud.columns = ['total_transactions', 'fraud_count', 'total_amount', 'fraud_rate', 'fraud_amount_percent']
                results['high_risk_merchants'] = merchant_fraud.reset_index().sort_values('fraud_rate', ascending=False)
            
        except Exception as e:
            logger.error(f"Error in fraud analysis: {str(e)}")
        
        return results
    
    def _analyze_banking_patterns(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze banking and inter-bank transaction patterns."""
        results = {}
        
        try:
            # Bank preference analysis
            if 'sender_bank' in df.columns and 'receiver_bank' in df.columns:
                bank_pairs = df.groupby(['sender_bank', 'receiver_bank']).agg({
                    'transaction_id': 'count',
                    'amount_inr': 'sum'
                }).round(2)
                bank_pairs.columns = ['transaction_count', 'total_amount']
                results['bank_pair_analysis'] = bank_pairs.reset_index().sort_values('transaction_count', ascending=False)
                
                # Same bank vs different bank analysis
                df['same_bank'] = df['sender_bank'] == df['receiver_bank']
                same_bank_analysis = df.groupby('same_bank').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean'],
                    'fraud_flag': 'sum'
                }).round(2)
                same_bank_analysis.columns = ['transaction_count', 'total_amount', 'avg_amount', 'fraud_count']
                same_bank_analysis['fraud_rate'] = (same_bank_analysis['fraud_count'] / same_bank_analysis['transaction_count'] * 100).round(2)
                results['same_bank_vs_different'] = same_bank_analysis.reset_index()
            
        except Exception as e:
            logger.error(f"Error in banking analysis: {str(e)}")
        
        return results
    
    def _analyze_customer_behavior(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze customer behavior patterns."""
        results = {}
        
        try:
            # Age group interactions
            if 'sender_age_group' in df.columns and 'receiver_age_group' in df.columns:
                age_interactions = df.groupby(['sender_age_group', 'receiver_age_group']).agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean']
                }).round(2)
                age_interactions.columns = ['transaction_count', 'total_amount', 'avg_amount']
                results['age_group_interactions'] = age_interactions.reset_index().sort_values('transaction_count', ascending=False)
            
        except Exception as e:
            logger.error(f"Error in customer behavior analysis: {str(e)}")
        
        return results
    
    def _analyze_device_network(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Analyze device and network usage patterns."""
        results = {}
        
        try:
            # Device type analysis
            if 'device_type' in df.columns:
                device_analysis = df.groupby('device_type').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean'],
                    'fraud_flag': 'sum'
                }).round(2)
                device_analysis.columns = ['transaction_count', 'total_amount', 'avg_amount', 'fraud_count']
                device_analysis['fraud_rate'] = (device_analysis['fraud_count'] / device_analysis['transaction_count'] * 100).round(2)
                results['device_type_analysis'] = device_analysis.reset_index()
            
            # Network type analysis
            if 'network_type' in df.columns:
                network_analysis = df.groupby('network_type').agg({
                    'transaction_id': 'count',
                    'amount_inr': ['sum', 'mean'],
                    'fraud_flag': 'sum'
                }).round(2)
                network_analysis.columns = ['transaction_count', 'total_amount', 'avg_amount', 'fraud_count']
                network_analysis['fraud_rate'] = (network_analysis['fraud_count'] / network_analysis['transaction_count'] * 100).round(2)
                results['network_type_analysis'] = network_analysis.reset_index()
            
            # Device + Network combination analysis
            if 'device_type' in df.columns and 'network_type' in df.columns:
                device_network = df.groupby(['device_type', 'network_type']).agg({
                    'transaction_id': 'count',
                    'fraud_flag': 'sum'
                })
                device_network['fraud_rate'] = (device_network['fraud_flag'] / device_network['transaction_id'] * 100).round(2)
                device_network.columns = ['transaction_count', 'fraud_count', 'fraud_rate']
                results['device_network_analysis'] = device_network.reset_index().sort_values('fraud_rate', ascending=False)
            
        except Exception as e:
            logger.error(f"Error in device/network analysis: {str(e)}")
        
        return results
    
    def get_view_definitions(self) -> Dict[str, str]:
        """
        Get SQL view definitions based on the original analysis queries.
        
        Returns:
            Dictionary of view_name -> SQL query
        """
        return {
            'peak_hours': """
                SELECT hour_of_day, COUNT(*) AS transaction_count
                FROM transactions
                GROUP BY hour_of_day
                ORDER BY transaction_count DESC
            """,
            'day_of_week_trends': """
                SELECT day_of_week, COUNT(*) AS transaction_count
                FROM transactions
                GROUP BY day_of_week
                ORDER BY transaction_count DESC
            """,
            'fraud_transaction_type': """
                SELECT transaction_type,
                       COUNT(*) AS total_transactions, 
                       SUM(fraud_flag::INT) AS fraud_transactions
                FROM transactions
                GROUP BY transaction_type
                ORDER BY fraud_transactions DESC
            """,
            'fraud_merchant_category': """
                SELECT merchant_category, 
                       COUNT(*) AS total_transactions, 
                       SUM(fraud_flag::INT) AS fraud_transactions
                FROM transactions
                GROUP BY merchant_category
                ORDER BY fraud_transactions DESC
            """,
            'sender_state_transactions': """
                SELECT sender_state, COUNT(*) AS transaction_count
                FROM transactions
                GROUP BY sender_state
                ORDER BY transaction_count DESC
            """,
            'device_network_usage': """
                SELECT
                    device_type,
                    network_type,
                    COUNT(*) AS total_transactions,
                    SUM(fraud_flag::int) AS total_frauds,
                    ROUND(AVG(fraud_flag::int) * 100, 2) AS fraud_rate_percentage
                FROM transactions
                GROUP BY device_type, network_type
                ORDER BY fraud_rate_percentage DESC
            """
        }
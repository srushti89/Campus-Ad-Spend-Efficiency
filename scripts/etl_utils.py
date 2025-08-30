"""
ETL (Extract, Transform, Load) utilities for Campus Ad Spend Efficiency project

This module contains utility functions for:
- Data cleaning and preprocessing
- Feature engineering
- Data validation
- Export functions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    """Main data processing class for ad campaign data"""
    
    def __init__(self):
        self.processed_data = {}
        
    def load_raw_data(self, data_path='../data/'):
        """Load raw data files"""
        try:
            logger.info("Loading raw data files...")
            
            self.impressions_df = pd.read_csv(f'{data_path}raw_impressions.csv')
            self.clicks_df = pd.read_csv(f'{data_path}raw_clicks.csv')
            self.conversions_df = pd.read_csv(f'{data_path}raw_conversions.csv')
            
            logger.info(f"Loaded {len(self.impressions_df)} impressions")
            logger.info(f"Loaded {len(self.clicks_df)} clicks")
            logger.info(f"Loaded {len(self.conversions_df)} conversions")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def clean_impressions_data(self):
        """Clean and preprocess impressions data"""
        logger.info("Cleaning impressions data...")
        
        df = self.impressions_df.copy()
        
        # Convert timestamp columns
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract time features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        df['is_business_hours'] = df['hour'].between(9, 17)
        
        # Clean categorical variables
        df['channel'] = df['channel'].str.strip().str.title()
        df['device_type'] = df['device_type'].str.lower()
        df['audience_segment'] = df['audience_segment'].str.lower()
        
        # Handle missing values
        df['cost'] = df['cost'].fillna(df['cost'].median())
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['impression_id'])
        duplicates_removed = initial_count - len(df)
        
        if duplicates_removed > 0:
            logger.warning(f"Removed {duplicates_removed} duplicate impressions")
        
        # Data validation
        df = self._validate_impressions(df)
        
        self.processed_data['impressions'] = df
        logger.info(f"Cleaned impressions data: {len(df)} records")
        
        return df
    
    def clean_clicks_data(self):
        """Clean and preprocess clicks data"""
        logger.info("Cleaning clicks data...")
        
        df = self.clicks_df.copy()
        
        # Convert timestamp columns
        df['click_timestamp'] = pd.to_datetime(df['click_timestamp'])
        
        # Extract time features
        df['click_hour'] = df['click_timestamp'].dt.hour
        df['click_day_of_week'] = df['click_timestamp'].dt.dayofweek
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['click_id'])
        duplicates_removed = initial_count - len(df)
        
        if duplicates_removed > 0:
            logger.warning(f"Removed {duplicates_removed} duplicate clicks")
        
        # Data validation
        df = self._validate_clicks(df)
        
        self.processed_data['clicks'] = df
        logger.info(f"Cleaned clicks data: {len(df)} records")
        
        return df
    
    def clean_conversions_data(self):
        """Clean and preprocess conversions data"""
        logger.info("Cleaning conversions data...")
        
        df = self.conversions_df.copy()
        
        # Convert timestamp columns
        df['conversion_timestamp'] = pd.to_datetime(df['conversion_timestamp'])
        
        # Extract time features
        df['conversion_hour'] = df['conversion_timestamp'].dt.hour
        df['conversion_day_of_week'] = df['conversion_timestamp'].dt.dayofweek
        
        # Clean conversion values
        df['conversion_value'] = pd.to_numeric(df['conversion_value'], errors='coerce')
        df = df.dropna(subset=['conversion_value'])
        
        # Remove negative or zero conversion values
        df = df[df['conversion_value'] > 0]
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['conversion_id'])
        duplicates_removed = initial_count - len(df)
        
        if duplicates_removed > 0:
            logger.warning(f"Removed {duplicates_removed} duplicate conversions")
        
        # Data validation
        df = self._validate_conversions(df)
        
        self.processed_data['conversions'] = df
        logger.info(f"Cleaned conversions data: {len(df)} records")
        
        return df
    
    def create_user_journey(self):
        """Create user journey data by joining impressions, clicks, and conversions"""
        logger.info("Creating user journey data...")
        
        # Join impressions with clicks
        impressions_clicks = pd.merge(
            self.processed_data['impressions'],
            self.processed_data['clicks'],
            on='impression_id',
            how='left',
            suffixes=('_imp', '_click')
        )
        
        # Join with conversions
        full_journey = pd.merge(
            impressions_clicks,
            self.processed_data['conversions'],
            on='click_id',
            how='left',
            suffixes=('', '_conv')
        )
        
        # Calculate time differences
        full_journey['click_delay_minutes'] = (
            full_journey['click_timestamp'] - full_journey['timestamp']
        ).dt.total_seconds() / 60
        
        full_journey['conversion_delay_hours'] = (
            full_journey['conversion_timestamp'] - full_journey['click_timestamp']
        ).dt.total_seconds() / 3600
        
        # Flag converted users
        full_journey['converted'] = full_journey['conversion_id'].notna()
        
        self.processed_data['user_journey'] = full_journey
        logger.info(f"Created user journey data: {len(full_journey)} records")
        
        return full_journey
    
    def calculate_channel_metrics(self):
        """Calculate key performance metrics by channel"""
        logger.info("Calculating channel metrics...")
        
        journey_df = self.processed_data['user_journey']
        
        channel_metrics = journey_df.groupby('channel_imp').agg({
            'impression_id': 'count',
            'click_id': 'count',
            'conversion_id': 'count',
            'cost': 'sum',
            'conversion_value': 'sum'
        }).reset_index()
        
        channel_metrics.columns = ['channel', 'impressions', 'clicks', 'conversions', 'cost', 'revenue']
        
        # Calculate derived metrics
        channel_metrics['ctr'] = channel_metrics['clicks'] / channel_metrics['impressions'] * 100
        channel_metrics['conversion_rate'] = channel_metrics['conversions'] / channel_metrics['clicks'] * 100
        channel_metrics['cost_per_click'] = channel_metrics['cost'] / channel_metrics['clicks']
        channel_metrics['cost_per_conversion'] = channel_metrics['cost'] / channel_metrics['conversions']
        channel_metrics['roas'] = channel_metrics['revenue'] / channel_metrics['cost']
        channel_metrics['profit'] = channel_metrics['revenue'] - channel_metrics['cost']
        
        # Handle division by zero
        channel_metrics = channel_metrics.replace([np.inf, -np.inf], np.nan)
        
        self.processed_data['channel_metrics'] = channel_metrics
        logger.info("Channel metrics calculated successfully")
        
        return channel_metrics
    
    def _validate_impressions(self, df):
        """Validate impressions data"""
        logger.info("Validating impressions data...")
        
        initial_count = len(df)
        
        # Remove records with missing critical fields
        df = df.dropna(subset=['impression_id', 'user_id', 'channel', 'timestamp'])
        
        # Remove records with invalid costs
        df = df[df['cost'] >= 0]
        
        # Remove future dates
        df = df[df['timestamp'] <= datetime.now()]
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.warning(f"Removed {removed_count} invalid impression records")
        
        return df
    
    def _validate_clicks(self, df):
        """Validate clicks data"""
        logger.info("Validating clicks data...")
        
        initial_count = len(df)
        
        # Remove records with missing critical fields
        df = df.dropna(subset=['click_id', 'impression_id', 'user_id', 'click_timestamp'])
        
        # Remove future dates
        df = df[df['click_timestamp'] <= datetime.now()]
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.warning(f"Removed {removed_count} invalid click records")
        
        return df
    
    def _validate_conversions(self, df):
        """Validate conversions data"""
        logger.info("Validating conversions data...")
        
        initial_count = len(df)
        
        # Remove records with missing critical fields
        df = df.dropna(subset=['conversion_id', 'click_id', 'user_id', 'conversion_timestamp'])
        
        # Remove future dates
        df = df[df['conversion_timestamp'] <= datetime.now()]
        
        # Remove unrealistic conversion values
        q1 = df['conversion_value'].quantile(0.01)
        q99 = df['conversion_value'].quantile(0.99)
        df = df[(df['conversion_value'] >= q1) & (df['conversion_value'] <= q99)]
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.warning(f"Removed {removed_count} invalid conversion records")
        
        return df
    
    def export_cleaned_data(self, output_path='../data/'):
        """Export cleaned data to CSV files"""
        logger.info("Exporting cleaned data...")
        
        for key, df in self.processed_data.items():
            filename = f'{output_path}clean_{key}.csv'
            df.to_csv(filename, index=False)
            logger.info(f"Exported {key} data to {filename}")
    
    def generate_data_quality_report(self):
        """Generate a data quality report"""
        logger.info("Generating data quality report...")
        
        report = {
            'processing_timestamp': datetime.now().isoformat(),
            'data_summary': {}
        }
        
        for key, df in self.processed_data.items():
            report['data_summary'][key] = {
                'record_count': len(df),
                'null_counts': df.isnull().sum().to_dict(),
                'data_types': df.dtypes.astype(str).to_dict()
            }
        
        return report

def main():
    """Main ETL pipeline"""
    processor = DataProcessor()
    
    # Load and clean data
    if processor.load_raw_data():
        processor.clean_impressions_data()
        processor.clean_clicks_data()
        processor.clean_conversions_data()
        
        # Create enriched datasets
        processor.create_user_journey()
        processor.calculate_channel_metrics()
        
        # Export results
        processor.export_cleaned_data()
        
        # Generate report
        report = processor.generate_data_quality_report()
        print("Data processing completed successfully!")
        print(f"Quality report: {report}")
    
    else:
        print("Failed to load data. Please check data files.")

if __name__ == "__main__":
    main()

"""
Synthetic Data Generator for Campus Ad Spend Efficiency Project

This script generates synthetic advertising data that mimics real-world scenarios:
- Ad impressions across multiple channels
- Click-through events
- Conversion events
- User demographics and behavior patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker()
np.random.seed(42)
random.seed(42)

def generate_ad_impressions(n_impressions=2000000):
    """Generate synthetic ad impression data"""
    
    # Define channels and their characteristics
    channels = {
        'Google Search': {'ctr': 0.03, 'cost_per_impression': 0.15, 'conversion_rate': 0.08},
        'Facebook': {'ctr': 0.02, 'cost_per_impression': 0.08, 'conversion_rate': 0.04},
        'Instagram': {'ctr': 0.025, 'cost_per_impression': 0.09, 'conversion_rate': 0.035},
        'TikTok': {'ctr': 0.035, 'cost_per_impression': 0.06, 'conversion_rate': 0.03},
        'YouTube': {'ctr': 0.015, 'cost_per_impression': 0.12, 'conversion_rate': 0.05},
        'Display Network': {'ctr': 0.008, 'cost_per_impression': 0.04, 'conversion_rate': 0.015},
        'Campus Radio': {'ctr': 0.01, 'cost_per_impression': 0.05, 'conversion_rate': 0.02},
        'Campus TV': {'ctr': 0.012, 'cost_per_impression': 0.18, 'conversion_rate': 0.055}
    }
    
    # Generate time series data
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='H')
    
    impressions_data = []
    
    for i in range(n_impressions):
        channel = np.random.choice(list(channels.keys()), 
                                 p=[0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.05, 0.05])
        
        # Seasonal and time-based patterns
        timestamp = np.random.choice(date_range)
        hour = timestamp.hour
        day_of_week = timestamp.dayofweek
        
        # Adjust impressions based on time patterns
        time_multiplier = 1.0
        if 9 <= hour <= 17:  # Business hours
            time_multiplier *= 1.3
        if day_of_week < 5:  # Weekdays
            time_multiplier *= 1.2
        
        impression = {
            'impression_id': f'imp_{i:08d}',
            'user_id': f'user_{np.random.randint(1, 500000):06d}',
            'channel': channel,
            'campaign_id': f'camp_{np.random.randint(1, 50):03d}',
            'ad_placement': f'placement_{np.random.randint(1, 200):03d}',
            'timestamp': timestamp,
            'cost': channels[channel]['cost_per_impression'] * np.random.uniform(0.8, 1.2),
            'device_type': np.random.choice(['mobile', 'desktop', 'tablet'], p=[0.6, 0.3, 0.1]),
            'audience_segment': np.random.choice(['students', 'faculty', 'staff', 'alumni'], p=[0.5, 0.2, 0.2, 0.1]),
            'creative_type': np.random.choice(['image', 'video', 'text'], p=[0.5, 0.3, 0.2])
        }
        
        impressions_data.append(impression)
    
    return pd.DataFrame(impressions_data)

def generate_clicks(impressions_df):
    """Generate click events based on impressions"""
    
    clicks_data = []
    
    for _, impression in impressions_df.iterrows():
        channel = impression['channel']
        
        # Channel-specific CTR
        base_ctr = {
            'Google Search': 0.03, 'Facebook': 0.02, 'Instagram': 0.025,
            'TikTok': 0.035, 'YouTube': 0.015, 'Display Network': 0.008,
            'Campus Radio': 0.01, 'Campus TV': 0.012
        }[channel]
        
        # Adjust CTR based on device and audience
        ctr_multiplier = 1.0
        if impression['device_type'] == 'mobile':
            ctr_multiplier *= 1.2
        if impression['audience_segment'] == 'students':
            ctr_multiplier *= 1.1
        
        if np.random.random() < base_ctr * ctr_multiplier:
            click = {
                'click_id': f'click_{len(clicks_data):08d}',
                'impression_id': impression['impression_id'],
                'user_id': impression['user_id'],
                'channel': channel,
                'campaign_id': impression['campaign_id'],
                'ad_placement': impression['ad_placement'],
                'click_timestamp': impression['timestamp'] + timedelta(seconds=np.random.randint(1, 300)),
                'device_type': impression['device_type'],
                'audience_segment': impression['audience_segment']
            }
            clicks_data.append(click)
    
    return pd.DataFrame(clicks_data)

def generate_conversions(clicks_df):
    """Generate conversion events based on clicks"""
    
    conversions_data = []
    
    for _, click in clicks_df.iterrows():
        channel = click['channel']
        
        # Channel-specific conversion rates
        base_conversion_rate = {
            'Google Search': 0.08, 'Facebook': 0.04, 'Instagram': 0.035,
            'TikTok': 0.03, 'YouTube': 0.05, 'Display Network': 0.015,
            'Campus Radio': 0.02, 'Campus TV': 0.055
        }[channel]
        
        # Adjust conversion rate based on audience
        conv_multiplier = 1.0
        if click['audience_segment'] == 'students':
            conv_multiplier *= 1.3
        elif click['audience_segment'] == 'alumni':
            conv_multiplier *= 0.8
        
        if np.random.random() < base_conversion_rate * conv_multiplier:
            # Random conversion delay (1 minute to 7 days)
            conversion_delay = timedelta(
                minutes=np.random.randint(1, 60),
                hours=np.random.randint(0, 24),
                days=np.random.randint(0, 7)
            )
            
            conversion = {
                'conversion_id': f'conv_{len(conversions_data):08d}',
                'click_id': click['click_id'],
                'user_id': click['user_id'],
                'channel': channel,
                'campaign_id': click['campaign_id'],
                'ad_placement': click['ad_placement'],
                'conversion_timestamp': click['click_timestamp'] + conversion_delay,
                'conversion_value': np.random.uniform(20, 500),  # Revenue per conversion
                'conversion_type': np.random.choice(['purchase', 'signup', 'download'], p=[0.6, 0.3, 0.1]),
                'device_type': click['device_type'],
                'audience_segment': click['audience_segment']
            }
            conversions_data.append(conversion)
    
    return pd.DataFrame(conversions_data)

def main():
    """Generate all synthetic datasets"""
    
    print("Generating synthetic ad impressions...")
    impressions_df = generate_ad_impressions(n_impressions=100000)  # Reduced for demo
    
    print("Generating clicks...")
    clicks_df = generate_clicks(impressions_df)
    
    print("Generating conversions...")
    conversions_df = generate_conversions(clicks_df)
    
    # Save datasets
    print("Saving datasets...")
    impressions_df.to_csv('data/raw_impressions.csv', index=False)
    clicks_df.to_csv('data/raw_clicks.csv', index=False)
    conversions_df.to_csv('data/raw_conversions.csv', index=False)
    
    # Print summary statistics
    print(f"\nDataset Summary:")
    print(f"Impressions: {len(impressions_df):,}")
    print(f"Clicks: {len(clicks_df):,}")
    print(f"Conversions: {len(conversions_df):,}")
    print(f"Overall CTR: {len(clicks_df)/len(impressions_df)*100:.2f}%")
    print(f"Overall Conversion Rate: {len(conversions_df)/len(clicks_df)*100:.2f}%")
    
    # Channel performance summary
    print(f"\nChannel Performance:")
    channel_stats = impressions_df.groupby('channel').agg({
        'impression_id': 'count',
        'cost': 'sum'
    }).join(
        clicks_df.groupby('channel')['click_id'].count()
    ).join(
        conversions_df.groupby('channel')['conversion_id'].count()
    ).fillna(0)
    
    channel_stats.columns = ['impressions', 'total_cost', 'clicks', 'conversions']
    channel_stats['ctr'] = channel_stats['clicks'] / channel_stats['impressions'] * 100
    channel_stats['conversion_rate'] = channel_stats['conversions'] / channel_stats['clicks'] * 100
    channel_stats['cost_per_conversion'] = channel_stats['total_cost'] / channel_stats['conversions']
    
    print(channel_stats.round(2))

if __name__ == "__main__":
    main()

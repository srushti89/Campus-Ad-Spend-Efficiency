import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Generate sample impressions data
n_impressions = 10000
channels = ['Google Search', 'Facebook', 'Instagram', 'TikTok', 'YouTube', 'Display Network', 'Campus Radio', 'Campus TV']
devices = ['mobile', 'desktop', 'tablet']
audiences = ['students', 'faculty', 'staff', 'alumni']

# Generate impressions
impressions_data = []
for i in range(n_impressions):
    timestamp = datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365), hours=np.random.randint(0, 24))
    
    impression = {
        'impression_id': f'imp_{i:08d}',
        'user_id': f'user_{np.random.randint(1, 5000):06d}',
        'channel': np.random.choice(channels),
        'campaign_id': f'camp_{np.random.randint(1, 20):03d}',
        'ad_placement': f'placement_{np.random.randint(1, 50):03d}',
        'timestamp': timestamp,
        'cost': np.random.uniform(0.05, 0.25),
        'device_type': np.random.choice(devices, p=[0.6, 0.3, 0.1]),
        'audience_segment': np.random.choice(audiences, p=[0.5, 0.2, 0.2, 0.1]),
        'creative_type': np.random.choice(['image', 'video', 'text'], p=[0.5, 0.3, 0.2])
    }
    impressions_data.append(impression)

impressions_df = pd.DataFrame(impressions_data)

# Generate clicks (about 2% CTR)
clicks_data = []
click_id = 0
for _, impression in impressions_df.iterrows():
    if np.random.random() < 0.02:  # 2% CTR
        click = {
            'click_id': f'click_{click_id:08d}',
            'impression_id': impression['impression_id'],
            'user_id': impression['user_id'],
            'channel': impression['channel'],
            'campaign_id': impression['campaign_id'],
            'ad_placement': impression['ad_placement'],
            'click_timestamp': impression['timestamp'] + timedelta(seconds=np.random.randint(1, 300)),
            'device_type': impression['device_type'],
            'audience_segment': impression['audience_segment']
        }
        clicks_data.append(click)
        click_id += 1

clicks_df = pd.DataFrame(clicks_data)

# Generate conversions (about 5% of clicks convert)
conversions_data = []
conv_id = 0
for _, click in clicks_df.iterrows():
    if np.random.random() < 0.05:  # 5% conversion rate
        conversion = {
            'conversion_id': f'conv_{conv_id:08d}',
            'click_id': click['click_id'],
            'user_id': click['user_id'],
            'channel': click['channel'],
            'campaign_id': click['campaign_id'],
            'ad_placement': click['ad_placement'],
            'conversion_timestamp': click['click_timestamp'] + timedelta(hours=np.random.randint(1, 48)),
            'conversion_value': np.random.uniform(20, 500),
            'conversion_type': np.random.choice(['purchase', 'signup', 'download'], p=[0.6, 0.3, 0.1]),
            'device_type': click['device_type'],
            'audience_segment': click['audience_segment']
        }
        conversions_data.append(conversion)
        conv_id += 1

conversions_df = pd.DataFrame(conversions_data)

# Save the data
impressions_df.to_csv('data/raw_impressions.csv', index=False)
clicks_df.to_csv('data/raw_clicks.csv', index=False)
conversions_df.to_csv('data/raw_conversions.csv', index=False)

print(f"Generated {len(impressions_df)} impressions")
print(f"Generated {len(clicks_df)} clicks")
print(f"Generated {len(conversions_df)} conversions")

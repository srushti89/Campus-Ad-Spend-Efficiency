"""
Setup script for Campus Ad Spend Efficiency project

Run this script to:
1. Install required packages
2. Generate sample data
3. Validate environment setup
"""

import subprocess
import sys
import os

def install_packages():
    """Install required packages"""
    packages = [
        'pandas>=1.5.0',
        'numpy>=1.21.0',
        'matplotlib>=3.5.0',
        'seaborn>=0.11.0',
        'plotly>=5.0.0',
        'scipy>=1.9.0',
        'statsmodels>=0.13.0',
        'scikit-learn>=1.1.0',
        'faker>=15.0.0',
        'jupyter>=1.0.0',
        'ipywidgets>=8.0.0'
    ]
    
    print("📦 Installing required packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            
def validate_imports():
    """Validate that all required packages can be imported"""
    print("\n🔍 Validating package imports...")
    
    packages_to_test = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('matplotlib.pyplot', 'plt'),
        ('seaborn', 'sns'),
        ('plotly.express', 'px'),
        ('scipy', 'scipy'),
        ('statsmodels', 'sm'),
        ('sklearn', 'sklearn'),
        ('faker', 'faker')
    ]
    
    failed_imports = []
    
    for package, alias in packages_to_test:
        try:
            exec(f"import {package} as {alias}")
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def generate_sample_data():
    """Generate sample data if it doesn't exist"""
    print("\n📊 Checking for sample data...")
    
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Created {data_dir} directory")
    
    required_files = [
        'data/raw_impressions.csv',
        'data/raw_clicks.csv', 
        'data/raw_conversions.csv'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"🔄 Generating missing data files: {missing_files}")
        
        # Import here after packages are installed
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
        
        print(f"✅ Generated synthetic data:")
        print(f"📊 Impressions: {len(impressions_df):,}")
        print(f"🖱️ Clicks: {len(clicks_df):,}")
        print(f"💰 Conversions: {len(conversions_df):,}")
        
    else:
        print("✅ All required data files exist!")

def main():
    """Main setup function"""
    print("🚀 Setting up Campus Ad Spend Efficiency project...")
    print("=" * 60)
    
    # Step 1: Install packages
    install_packages()
    
    # Step 2: Validate imports
    if not validate_imports():
        print("\n❌ Setup failed due to import errors.")
        print("Please check the error messages above and try again.")
        return False
    
    # Step 3: Generate sample data
    generate_sample_data()
    
    print("\n" + "=" * 60)
    print("🎉 PROJECT SETUP COMPLETE!")
    print("\n📁 You now have:")
    print("   ✅ All required packages installed")
    print("   ✅ Sample data generated")
    print("   ✅ 4 analysis notebooks ready")
    print("   ✅ Utility scripts available")
    print("   ✅ Dashboard and report templates")
    
    print("\n🚀 Next steps:")
    print("   1. Open 01_data_cleaning.ipynb")
    print("   2. Run the notebook cells to explore the data")
    print("   3. Continue with 02_exploratory_analysis.ipynb")
    print("   4. Build attribution models in 03_attribution_model.ipynb")
    print("   5. Design A/B tests in 04_ab_test_framework.ipynb")
    
    print("\n📖 Documentation:")
    print("   - README.md: Project overview")
    print("   - dashboards/dashboard_specification.md: Dashboard guide")
    print("   - reports/business_impact_report.md: Report template")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)

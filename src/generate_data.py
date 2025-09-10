import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_ads_data(n=10000):
    np.random.seed(42)
    random.seed(42)
    
    start_date = datetime(2024, 1, 1)
    rows = []
    
    # Define realistic audiences
    audience_options = [
        # Lookalike Audiences
        'Lookalike_Top_Spenders',
        'Lookalike_Recent_Purchasers',
        
        # Interest-Based Audiences
        'Interest_In_Home_Fitness',
        'Interest_In_Sustainable_Fashion',
        'Interest_In_Organic_Food',
        'Interest_In_Tech_Gadgets',
        'Interest_In_Luxury_Travel',
        
        # Retargeting Audiences
        'Retargeting_Cart_Abandoners',
        'Retargeting_Product_Viewers',
        'Retargeting_Email_Engagers',
        
        # Custom Lists
        'Custom_List_Newsletter_Subscribers',
        'Custom_List_Past_Purchasers',
        
        # Broad Audiences
        'Broad_18-34_INDIA',
        'Broad_35-54_USA'
    ]
    
    for i in range(n):
        date = start_date + timedelta(days=int(np.random.exponential(scale=30)))
        campaign = random.choice(['Brand_Awareness','Traffic','Conversions','Retargeting','Video_Views'])
        ad_set = random.choice(['Set_1','Set_2','Set_3','Set_4'])
        ad = f"Ad_{random.randint(1,20)}"
        platform = random.choice(['Facebook','Instagram','X','LinkedIn','TikTok'])
        audience = random.choice(audience_options)
        audience_size = random.choice(['Narrow', 'Medium', 'Broad'])
        
        impressions = max(1, int(np.random.poisson(1000)))
        ctr = np.clip(np.random.normal(0.02 + (0.005 if campaign=='Conversions' else 0), 0.01), 0.001, 0.2)
        clicks = int(impressions * ctr)
        cpc = np.clip(np.random.normal(0.4 if platform in ['Facebook','Instagram'] else 0.6, 0.2), 0.05, 5.0)
        spend = round(clicks * cpc, 2)
        
        conv_rate = np.clip(np.random.normal(0.03 + (0.02 if campaign=='Conversions' else 0), 0.02), 0.0, 1.0)
        conversions = int(clicks * conv_rate)
        revenue_per_conv = round(np.random.normal(50 if campaign=='Conversions' else 20, 10), 2)
        revenue = round(conversions * revenue_per_conv, 2)
        
        # Additional metrics
        video_views = int(clicks * np.clip(np.random.normal(0.7, 0.2), 0.0, 1.0)) if campaign == 'Video_Views' else 0
        leads = int(conversions * np.clip(np.random.normal(0.7, 0.2), 0.0, 1.0))
        cpc_val = round(spend / clicks, 2) if clicks > 0 else 0
        cpm = round((spend / impressions) * 1000, 2) if impressions > 0 else 0
        
        # Funnel stage
        if campaign in ['Brand_Awareness', 'Video_Views']:
            funnel_stage = 'Awareness'
        elif campaign == 'Traffic':
            funnel_stage = 'Consideration'
        else:
            funnel_stage = 'Conversion'
        
        ad_type = random.choice(['Image', 'Video', 'Carousel'])
        creative_id = f"Creative_{random.randint(1,10)}"
        
        # Categorize audience type
        if 'Lookalike' in audience:
            audience_type = 'Lookalike'
        elif 'Interest' in audience:
            audience_type = 'Interest'
        elif 'Retargeting' in audience:
            audience_type = 'Retargeting'
        elif 'Custom_List' in audience:
            audience_type = 'Custom_List'
        else:
            audience_type = 'Broad'
        
        rows.append([
            date.strftime('%Y-%m-%d'), campaign, funnel_stage, ad_set, ad, creative_id, ad_type,
            platform, audience, audience_type, audience_size, impressions, clicks, spend, cpc_val, cpm,
            video_views, leads, conversions, revenue
        ])
    
    df = pd.DataFrame(rows, columns=[
        'date', 'campaign', 'funnel_stage', 'ad_set', 'ad', 'creative_id', 'ad_type',
        'platform', 'audience', 'audience_type', 'audience_size', 'impressions', 'clicks', 'spend', 'cpc', 'cpm',
        'video_views', 'leads', 'conversions', 'revenue'
    ])
    
    return df

if __name__ == "__main__":
    df = generate_ads_data(10000)
    df.to_csv('src/data/ads_data.csv', index=False)
    print(f"Generated dataset with {len(df)} rows saved to ads_data.csv")
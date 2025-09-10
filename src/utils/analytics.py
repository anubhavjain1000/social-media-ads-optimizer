import pandas as pd
import numpy as np

def calculate_metrics(df):
    """Calculate all performance metrics"""
    df = df.copy()
    
    # Basic metrics
    df['ctr'] = (df['clicks'] / df['impressions']).fillna(0)
    df['conversion_rate'] = (df['conversions'] / df['clicks']).replace([np.inf, -np.inf], 0).fillna(0)
    df['roas'] = (df['revenue'] / df['spend']).replace([np.inf, -np.inf], 0).fillna(0)
    df['cpa'] = (df['spend'] / df['conversions']).replace([np.inf, -np.inf], 0).fillna(0)
    df['profit'] = df['revenue'] - df['spend']
    df['roi'] = ((df['revenue'] - df['spend']) / df['spend']).replace([np.inf, -np.inf], 0).fillna(0)
    
    # Engagement metrics
    df['engagement_rate'] = ((df['clicks'] + df['conversions'] + df['video_views']) / df['impressions']).fillna(0)
    
    return df

def get_top_performers(df, metric='roi', n=10):
    """Get top performing campaigns by metric"""
    return df.nlargest(n, metric)[['campaign', 'platform', 'audience', metric, 'spend', 'revenue']]

def calculate_roi_by_dimension(df, dimension):
    """Calculate ROI by different dimensions"""
    grouped = df.groupby(dimension).agg({
        'spend': 'sum',
        'revenue': 'sum',
        'conversions': 'sum',
        'clicks': 'sum'
    }).reset_index()
    
    grouped['roi'] = (grouped['revenue'] - grouped['spend']) / grouped['spend']
    grouped['cpa'] = grouped['spend'] / grouped['conversions']
    grouped['ctr'] = grouped['clicks'] / df['impressions'].sum()
    
    return grouped.sort_values('roi', ascending=False)

def get_optimization_recommendations(df):
    """Generate data-driven optimization recommendations"""
    recommendations = []
    
    # Platform analysis
    platform_roi = calculate_roi_by_dimension(df, 'platform')
    best_platform = platform_roi.iloc[0]
    worst_platform = platform_roi.iloc[-1]
    
    recommendations.append({
        'type': 'Platform',
        'action': f'Increase budget on {best_platform["platform"]} (ROI: {best_platform["roi"]:.2f})',
        'impact': 'High'
    })
    
    # Campaign type analysis
    campaign_roi = calculate_roi_by_dimension(df, 'campaign')
    best_campaign = campaign_roi.iloc[0]
    
    recommendations.append({
        'type': 'Campaign',
        'action': f'Focus on {best_campaign["campaign"]} campaigns (ROI: {best_campaign["roi"]:.2f})',
        'impact': 'High'
    })
    
    # Audience analysis
    audience_roi = calculate_roi_by_dimension(df, 'audience')
    best_audience = audience_roi.iloc[0]
    
    recommendations.append({
        'type': 'Audience',
        'action': f'Target {best_audience["audience"]} audience more aggressively',
        'impact': 'Medium'
    })
    
    return pd.DataFrame(recommendations)
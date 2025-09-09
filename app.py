import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.analytics import calculate_metrics, get_top_performers, calculate_roi_by_dimension, get_optimization_recommendations

# Page configuration
st.set_page_config(
    page_title="Social Media Ad Optimizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('ads_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        return calculate_metrics(df)
    except:
        st.error("Data file not found. Please run generate_data.py first.")
        return pd.DataFrame()

df = load_data()

# Sidebar filters
st.sidebar.title("📊 Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(df['date'].min(), df['date'].max()),
    min_value=df['date'].min(),
    max_value=df['date'].max()
)

platforms = st.sidebar.multiselect(
    "Platforms",
    options=df['platform'].unique(),
    default=df['platform'].unique()
)

campaigns = st.sidebar.multiselect(
    "Campaign Types",
    options=df['campaign'].unique(),
    default=df['campaign'].unique()
)

# Apply filters
filtered_df = df[
    (df['date'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))) &
    (df['platform'].isin(platforms)) &
    (df['campaign'].isin(campaigns))
]

# Main dashboard
st.title("🎯 Social Media Ad Campaign Optimizer")
st.markdown("### Data-Driven Insights for Maximum ROI")

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Spend", f"₹{filtered_df['spend'].sum():,.0f}")
with col2:
    st.metric("Total Revenue", f"₹{filtered_df['revenue'].sum():,.0f}")
with col3:
    total_spend = filtered_df['spend'].sum()
    total_revenue = filtered_df['revenue'].sum()
    overall_roi = (total_revenue - total_spend) / total_spend if total_spend > 0 else 0
    st.metric("Overall ROI", f"{overall_roi * 100:.1f}%")
with col4:
    st.metric("Total Conversions", f"{filtered_df['conversions'].sum():,.0f}")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Performance Analysis", "🎯 Recommendations", "📋 Raw Data"])

with tab1:
    st.subheader("Performance Trends")
    
    # Time series charts
    col1, col2 = st.columns(2)
    with col1:
        daily_data = filtered_df.groupby('date').agg({'spend': 'sum', 'revenue': 'sum'}).reset_index()
        fig = px.line(daily_data, x='date', y=['spend', 'revenue'], 
                     title="Daily Spend vs Revenue",
                     labels={'value': 'Amount (₹)', 'variable': 'Metric'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        roi_trend = filtered_df.groupby('date')['roi'].mean().reset_index()
        fig = px.line(roi_trend, x='date', y='roi', title="Daily ROI Trend (%)", 
                    labels={'roi': 'ROI (%)'})
        fig.update_layout(yaxis_tickformat = '.1%')  # Format as percentage
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Detailed Performance Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        # Platform performance
        platform_perf = calculate_roi_by_dimension(filtered_df, 'platform')
        fig = px.bar(platform_perf, x='platform', y='roi', 
                    title="ROI by Platform (%)", color='roi',
                    labels={'roi': 'ROI (%)'})
        fig.update_layout(yaxis_tickformat = '.1%')  # Format as percentage
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Campaign performance
        campaign_perf = calculate_roi_by_dimension(filtered_df, 'campaign')
        fig = px.bar(campaign_perf, x='campaign', y='roi', 
                    title="ROI by Campaign Type (%)", color='roi',
                    labels={'roi': 'ROI (%)'})
        fig.update_layout(yaxis_tickformat = '.1%')  # Format as percentage
        st.plotly_chart(fig, use_container_width=True)
    
    # Top performers table with Rupee formatting
    st.subheader("Top Performing Campaigns")
    top_performers = get_top_performers(filtered_df, metric='roi', n=10)
    
    # Format the dataframe for display with Rupee symbols
    display_df = top_performers.copy()
    display_df['spend'] = display_df['spend'].apply(lambda x: f'₹{x:,.2f}')
    display_df['revenue'] = display_df['revenue'].apply(lambda x: f'₹{x:,.2f}')
    display_df['roi'] = display_df['roi'].apply(lambda x: f'{x * 100:.1f}%')
    
    st.dataframe(display_df, use_container_width=True)

with tab3:
    st.subheader("Optimization Recommendations")
    recommendations = get_optimization_recommendations(filtered_df)
    
    for _, rec in recommendations.iterrows():
        with st.expander(f"{rec['type']}: {rec['action']} ({rec['impact']} Impact)"):
            st.write(f"This recommendation is based on performance analysis showing this as the most effective area for investment.")
    
    st.subheader("Budget Reallocation Simulator")
    current_spend = filtered_df['spend'].sum()
    new_platform = st.selectbox("Shift budget to:", options=df['platform'].unique())
    shift_percentage = st.slider("Percentage shift:", 0, 100, 20)
    
    if st.button("Calculate Potential Impact"):
        platform_roi = calculate_roi_by_dimension(df, 'platform')
        target_roi = platform_roi[platform_roi['platform'] == new_platform]['roi'].values[0]
        additional_revenue = (current_spend * (shift_percentage/100)) * target_roi
        st.success(f"Potential additional revenue: ₹{additional_revenue:,.2f}")

with tab4:
    st.subheader("Raw Data")
    
    # Format the display dataframe with Rupee symbols
    display_raw_df = filtered_df.copy()
    monetary_columns = ['spend', 'revenue', 'cpc', 'cpm']
    for col in monetary_columns:
        if col in display_raw_df.columns:
            display_raw_df[col] = display_raw_df[col].apply(lambda x: f'₹{x:,.2f}' if pd.notnull(x) else '₹0.00')
    
    st.dataframe(display_raw_df, use_container_width=True)
    
    # Data export (keep original numeric format for export)
    if st.button("Export Filtered Data to CSV"):
        filtered_df.to_csv('filtered_ads_data.csv', index=False)
        st.success("Data exported successfully!")

# Footer
st.markdown("---")
st.markdown("Built using Streamlit specifically for BlockseBlock Hackathon | This analysis is performed on generated data and not on official data by any registered Company")
st.markdown("Made by Anubhav Jain")
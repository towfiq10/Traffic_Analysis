import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# 1. Page Configuration
st.set_page_config(
    page_title="Traffic & Incident Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Load and Cache the Data
@st.cache_data
def load_data():
    df = pd.read_csv('messy_traffic_data.csv')
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    return df

df = load_data()

# 3. Sidebar Filters
st.sidebar.header("🔍 Dashboard Filters")
st.sidebar.markdown("Slice the dataset to explore specific traffic conditions.")

# Filter A: Approach Leg Filter
selected_leg = "All"
if 'Approach_Leg' in df.columns:
    unique_legs = df['Approach_Leg'].dropna().unique().tolist()
    selected_leg = st.sidebar.selectbox("Select Approach Leg", options=["All"] + unique_legs)
    if selected_leg != "All":
        df = df[df['Approach_Leg'] == selected_leg]

# Filter B: Crash Type Filter
if 'Crash_Type' in df.columns:
    crash_options = sorted(df['Crash_Type'].dropna().unique().tolist())
    selected_crashes = st.sidebar.multiselect(
        "Filter by Crash Type", 
        options=crash_options, 
        default=crash_options
    )
    if selected_crashes:
        df = df[df['Crash_Type'].isin(selected_crashes)]

# 4. Main Dashboard UI Header
st.title("🚦 Advanced Traffic & Incident Analytics Dashboard")
st.markdown("Welcome! This interactive portfolio dashboard analyzes traffic performance, signal metrics, and incident hotspots.")

# Key Summary Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Filtered Records", len(df))
col2.metric("Active Leg Filter", selected_leg)
col3.metric("Total Volume Recorded", int(df['Traffic_Volume'].sum()) if 'Traffic_Volume' in df.columns else "N/A")
avg_speed = f"{df['Speed_Avg'].mean():.1f} mph" if 'Speed_Avg' in df.columns else "N/A"
col4.metric("Average Speed", avg_speed)

st.markdown("---")

# 5. Analytics Visualizations & Charts
st.subheader("📈 Traffic & Incident Analytics Visualizations")

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Volume by Approach Leg (Bar Chart)
with chart_col1:
    st.markdown("#### Traffic Volume by Approach Leg")
    if 'Approach_Leg' in df.columns and 'Traffic_Volume' in df.columns:
        leg_volume = df.groupby('Approach_Leg')['Traffic_Volume'].sum().reset_index()
        
        bar_chart = alt.Chart(leg_volume).mark_bar(color='#4c78a8').encode(
            x=alt.X('Approach_Leg:N', sort='-y', title='Approach Leg'),
            y=alt.Y('Traffic_Volume:Q', title='Total Traffic Volume'),
            tooltip=['Approach_Leg', 'Traffic_Volume']
        ).properties(height=350)
        
        st.altair_chart(bar_chart, use_container_width=True)
    else:
        st.info("Required columns for volume chart not found.")

# Chart 2: Traffic Volume vs. Average Speed (Scatter Plot)
with chart_col2:
    st.markdown("#### Traffic Volume vs. Average Speed")
    if 'Traffic_Volume' in df.columns and 'Speed_Avg' in df.columns:
        scatter_chart = alt.Chart(df).mark_circle(size=60, opacity=0.7).encode(
            x=alt.X('Traffic_Volume:Q', title='Traffic Volume'),
            y=alt.Y('Speed_Avg:Q', title='Average Speed (mph)'),
            color=alt.Color('Approach_Leg:N', legend=alt.Legend(title="Leg")) if 'Approach_Leg' in df.columns else alt.value('#f58518'),
            tooltip=['Traffic_Volume', 'Speed_Avg', 'Crash_Type'] if 'Crash_Type' in df.columns else ['Traffic_Volume', 'Speed_Avg']
        ).properties(height=350).interactive()
        
        st.altair_chart(scatter_chart, use_container_width=True)
    else:
        st.info("Required columns ('Traffic_Volume' or 'Speed_Avg') not found for scatter plot.")

# 6. Raw Data Preview
with st.expander("🔍 View Raw Filtered Data Table"):
    st.dataframe(df, use_container_width=True)
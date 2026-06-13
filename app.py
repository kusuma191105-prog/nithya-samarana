import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Nitya Smarana Dashboard",
    page_icon="🕉️",
    layout="wide"
)

DATA_FILE = "data.json"

# Load data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"logs": [], "last_log_date": "", "streak": 0}

# Save data
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Update streak logic
def update_streak(data):
    today = datetime.now().date()
    last_date_str = data.get("last_log_date", "")
    
    if last_date_str:
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
        if last_date == today - timedelta(days=1):
            data["streak"] += 1
        elif last_date != today:
            data["streak"] = 1
    else:
        data["streak"] = 1
    
    data["last_log_date"] = str(today)
    return data

# Main App
st.title("🕉️ Nitya Smarana Dashboard")
st.subheader("Track Your Daily Devotional Practice")

data = load_data()

# Sidebar - Log Practice
st.sidebar.header("📿 Log Today's Japa")
mantra = st.sidebar.selectbox(
    "Select Mantra",
    ["Om Namah Shivaya", "Hare Krishna", "Om Namo Narayanaya", "Gayatri Mantra", "Other"]
)
count = st.sidebar.number_input("Count", min_value=1, value=108, step=1)

if st.sidebar.button("✅ Mark as Done", use_container_width=True):
    today_str = str(datetime.now().date())
    
    # Check if already logged today
    logged_today = any(log['date'] == today_str for log in data['logs'])
    
    if not logged_today:
        data['logs'].append({
            "date": today_str,
            "mantra": mantra,
            "count": count
        })
        data = update_streak(data)
        save_data(data)
        st.sidebar.success("Great! Practice logged.")
        st.balloons()
    else:
        st.sidebar.warning("Already logged for today!")

# Display Streak
col1, col2, col3 = st.columns(3)
col1.metric("🔥 Current Streak", f"{data['streak']} Days")
col2.metric("📅 Total Days Logged", len(data['logs']))
total_count = sum(log['count'] for log in data['logs'])
col3.metric("📿 Total Japa Count", f"{total_count:,}")

# Analytics
if data['logs']:
    df = pd.DataFrame(data['logs'])
    df['date'] = pd.to_datetime(df['date'])
    
    st.markdown("---")
    st.header("📊 Your Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart - Mantra distribution
        mantra_counts = df.groupby('mantra')['count'].sum().reset_index()
        fig_pie = px.pie(mantra_counts, values='count', names='mantra', 
                         title='Mantra-wise Distribution')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart - Daily counts
        daily_counts = df.groupby('date')['count'].sum().reset_index()
        fig_bar = px.bar(daily_counts, x='date', y='count', 
                         title='Daily Japa Count', labels={'count':'Count', 'date':'Date'})
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Recent logs table
    st.subheader("📜 Recent Logs")
    st.dataframe(df.sort_values('date', ascending=False).head(10), use_container_width=True)
else:
    st.info("👆 Start by logging your first japa practice from the sidebar!")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Python & Streamlit | Author: Kusuma")

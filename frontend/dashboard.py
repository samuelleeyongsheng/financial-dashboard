import streamlit as st
import sqlite3
import pandas as pd
import os

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="AI Financial Dashboard", layout="wide")

st.title("🤖 AI-Powered Financial Dashboard")
st.markdown("Live sentiment analysis of financial news using **Google Gemini 2.5 Flash**")

# --- 2. CONNECT TO DATABASE (The "Smart Path" Logic) ---
def load_data():
    # 1. Get the absolute path of THIS script (dashboard.py)
    #    Example: C:/Users/Samuel/Project/frontend/dashboard.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Construct path to the DB: Go UP one level, then DOWN into backend
    #    Result: C:/Users/Samuel/Project/backend/news.db
    db_path = os.path.join(current_dir, '..', 'backend', 'news.db')
    
    try:
        # Check if file exists first
        if not os.path.exists(db_path):
            st.error(f"❌ Database not found at: {db_path}")
            return pd.DataFrame()

        conn = sqlite3.connect(db_path)
        query = "SELECT id, ticker, title, sentiment, ai_summary FROM news ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error reading database: {e}")
        return pd.DataFrame()

# --- 3. AUTO-REFRESH BUTTON ---
if st.button('🔄 Refresh Data'):
    st.rerun()

# --- 4. MAIN DASHBOARD ---
df = load_data()

if not df.empty:
    # SECTION A: METRICS
    col1, col2, col3 = st.columns(3)
    
    total_news = len(df)
    positive_news = len(df[df['sentiment'] == 'Positive'])
    negative_news = len(df[df['sentiment'] == 'Negative'])

    col1.metric("Total Articles", total_news)
    col2.metric("🟢 Positive Signals", positive_news)
    col3.metric("🔴 Negative Signals", negative_news)

    st.divider()

    # SECTION B: DATA TABLE
    st.subheader("📰 Recent AI Analysis")
    
    st.dataframe(
        df, 
        column_config={
            "ticker": "Stock",
            "title": "Headline",
            "sentiment": "AI Verdict",
            "ai_summary": "Why?"
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("⚠️ No data found. Please run your backend scraper to generate data.")
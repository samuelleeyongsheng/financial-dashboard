import streamlit as st
from supabase import create_client
import pandas as pd
import os
from dotenv import load_dotenv

# --- SETUP PAGE CONFIG (Must be the first command) ---
st.set_page_config(page_title="AI Financial Dashboard", layout="wide")

# --- CONNECT TO SUPABASE ---
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Error: Supabase keys missing in .env")
    st.stop()

@st.cache_resource #Prevents app from reconnecting to Supabase every single time you click a button (saves memory).
#Connect to Cloud DB
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- DATA LOADING FUNCTION ---
def load_data():
    # Connect to Supabase and fetch data
    try:
        response = supabase.table("news") \
            .select("id, ticker, title, sentiment, ai_summary") \
            .order("id", desc=True) \
            .execute()
        
        data = response.data
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"❌ Error loading data from Supabase: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# --- DASHBOARD UI ---
st.title("🤖 AI-Powered Financial Dashboard")
st.markdown("Live sentiment analysis of financial news using **Google Gemini 2.5 Flash**")

# --- REFRESH BUTTON ---
if st.button('🔄 Refresh Data'):
    st.rerun()

# --- LOAD DATA ---
df = load_data()

if not df.empty:
    # METRICS
    col1, col2, col3 = st.columns(3)
    
    total_news = len(df)
    positive_news = len(df[df['sentiment'] == 'Positive'])
    negative_news = len(df[df['sentiment'] == 'Negative'])

    col1.metric("Total Articles", total_news)
    col2.metric("🟢 Positive Signals", positive_news)
    col3.metric("🔴 Negative Signals", negative_news)

    st.divider()

    # DATA TABLE
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
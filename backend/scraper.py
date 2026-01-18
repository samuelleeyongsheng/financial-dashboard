import os
import yfinance as yf
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# --- SETUP & CONFIGURATION ---
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Supabase keys missing in .env")
    exit()

# Connect to Cloud DB
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)    

# Define assets news that i want to track 
TICKERS = ["BTC-USD", "TSLA", "GOOGL"]

# --- UPDATED FUNCTION: SAVE TO CLOUD ---
# User is just getting data from saved data in database
def save_news_to_supabase(ticker, news_item):
    """
    Parses the raw Yahoo data and uploads it to Supabase.
    Returns True if new, False if duplicate.
    """
    
    # ROBUST PARSING (Taken from your old code) -------------------------
    # Check if data is inside a 'content' box (Yahoo changes this often)
    if 'content' in news_item:
        data = news_item['content']
    else:
        data = news_item

    # Extract Data Safely
    title = data.get('title', 'No Title')
    
    # (Note: Our current Cloud Table only has 'ticker' and 'title'. 
    # If we want to save 'link' and 'publisher' later, we must add columns to Supabase first.
    # For now, we just use the title for AI analysis.)

    # DUPLICATE CHECK (Cloud Version) -----------------------------------
    # Ask Supabase: "Do you already have a row with this title?"
    try:
        existing = supabase.table("news").select("id").eq("title", title).execute()
        if len(existing.data) > 0:
            return False # Duplicate found, skip it
    except Exception as e:
        print(f"   ⚠️ Connection Error checking duplicates: {e}")
        return False

    # INSERT (Cloud Version) --------------------------------------------
    try:
        row_data = {
            "ticker": ticker,
            "title": title,
            "sentiment": None, # Waiting for AI Agent to fill this
            "ai_summary": None # Waiting for AI Agent to fill this
        }
        
        # Send to Singapore Server 🇸🇬
        supabase.table("news").insert(row_data).execute()
        return True
        
    except Exception as e:
        print(f"   ⚠️ Insert Error: {e}")
        return False


def fetch_market_news():
    print(f"--- 🚀 Starting Scraper for: {TICKERS} ---")
    total_new = 0
    
    for ticker in TICKERS:
        print(f"Checking {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            news_list = stock.news
            
            # Loop over the news_list keys id and content
            for item in news_list:
                # Bring the news_list of the id and content keys to the save_news function
                saved = save_news_to_supabase(ticker, item)
                #Updated code 
                if saved:
                    # Just for printing prettily
                    if 'content' in item:
                        title = item['content'].get('title', 'Unknown')
                    else:
                        title = item.get('title', 'Unknown')
                        
                    print(f"   ✅ [NEW] {title[:50]}...")
                    total_new += 1
                else:
                    # Print a dot for duplicates just so we know it's working
                    print(".", end="", flush=True)
                    
        except Exception as e:
            print(f"   ❌ Error fetching {ticker}: {e}")

    print(f"\n\n🏁 Finished! Scraped {total_new} new articles to Cloud.")

if __name__ == "__main__":
    fetch_market_news()
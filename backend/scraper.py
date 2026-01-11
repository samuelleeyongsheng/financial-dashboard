import yfinance as yf
import sqlite3
from datetime import datetime

# Define assets news that i want to track 
TICKERS = ["BTC-USD", "TSLA", "GOOGL"]

def init_db():
    # Create a new database and open a database connection
    con = sqlite3.connect('news.db')

    # In order to execute SQL statements and fetch results from SQL queries, need to use a database cursor.
    c = con.cursor()

    # Execute to create table if not exist 
    c.execute('''CREATE TABLE IF NOT EXISTS news
                 (id INTEGER PRIMARY KEY, 
                  ticker TEXT, 
                  title TEXT, 
                  link TEXT UNIQUE, 
                  publisher TEXT, 
                  published TEXT)''')
                  # not using integer as the format is integer mix some text
                  
    # After SQL commands, need to commit the changes into the news.db and close the connection
    con.commit()
    con.close()

def save_news(ticker, news_item):
    con = sqlite3.connect('news.db')
    c = con.cursor()
    
    # --- HANDLE NESTED DATA ---
    # 1. Check if data is inside a 'content' box
    if 'content' in news_item:
        data = news_item['content']
    else:
        data = news_item # Fallback if structure changes

    # 2. Extract data safely
    # .get() in python is like in java getOrDefault(), mostly can get key in the first, if no go to second 'No Title'
    title = data.get('title', 'No Title')
    summary = data.get('summary', '') # We can use this later
    
    # Link is tricky. It's inside 'clickThroughUrl' or 'canonicalUrl' -> 'url'
    # Get either 'clickThroughUrl' or 'canonicalUrl' then retrieve the url value from it
    link_obj = data.get('clickThroughUrl') or data.get('canonicalUrl')
    link = link_obj.get('url') if link_obj else 'No Link'

    # Publisher is inside 'provider' -> 'displayName'
    provider = data.get('provider', {})
    publisher = provider.get('displayName', 'Unknown')

    # Date
    pub_date = data.get('pubDate', str(datetime.now()))

    try:
        c.execute('''INSERT INTO news (ticker, title, link, publisher, published) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (ticker, title, link, publisher, pub_date))
        return True
    except sqlite3.IntegrityError:
        return False # Duplicate article
    except Exception as e:
        print(f"   ⚠️ Database Error: {e}")
        return False
    finally:
        con.commit()
        con.close()

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
                saved = save_news(ticker, item)
                if saved:
                    # if saved then retrieve the content key and its key inside and print out like a summary 
                    # Backup: If 'title' is missing, return "Unknown Title".
                    title = item.get('content', {}).get('title', 'Unknown Title')
                    print(f"   [NEW] {title[:50]}...")
                    total_new += 1
                    
        except Exception as e:
            # e means "Save that error report into a variable named e so I can read it."
            print(f"   Error fetching {ticker}: {e}")

    print(f"\n✅ Finished! Scraped {total_new} new articles.")

if __name__ == "__main__":
    init_db()
    fetch_market_news()
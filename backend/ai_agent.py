from google import genai
from google.genai import types
import sqlite3
import json
import time
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("❌ Error: API Key not found! Did you create the .env file?")

# Initialize the NEW Client
client = genai.Client(api_key=GEMINI_API_KEY)

def get_db_connection():
    conn = sqlite3.connect('news.db')
    conn.row_factory = sqlite3.Row # Allows us to access columns by name
    return conn

def analyze_news():
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Select 5 news articles that need analysis
    rows = c.execute("SELECT id, title, ticker FROM news WHERE sentiment IS NULL LIMIT 5").fetchall()
    
    if not rows:
        print("✅ All news is already analyzed! No work to do.")
        return

    print(f"🤖 AI Agent waking up... Analyzing {len(rows)} articles.")

    for row in rows:
        news_id = row['id']
        title = row['title']
        ticker = row['ticker']

        # 2. The Prompt: Ask Gemini to analyze the sentiment
        prompt = f"""
        You are a financial analyst. Analyze this news headline for {ticker}: 
        "{title}"
        
        Return a JSON object with exactly these fields:
        {{
            "sentiment": "Positive" or "Negative" or "Neutral",
            "summary": "One short sentence explaining the impact."
        }}
        Do not use markdown. Return ONLY raw JSON.
        """

        try:
            print(f"   Thinking about {ticker}...")

            # New google-genai client syntax
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                # Let's use the newest fast model
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json" # This forces JSON output!
                )
            )
            
            # To be safe, we parse the text just like before.
            result = json.loads(response.text)
            
            # 3. Save the result back to the database
            c.execute("UPDATE news SET sentiment = ?, ai_summary = ? WHERE id = ?", 
                      (result['sentiment'], result['summary'], news_id))
            conn.commit()
            print(f"   👉 Verdict: {result['sentiment']} | Summary: {result['summary']}")
            
            # Sleep for 1 second to be nice to the API
            time.sleep(1) 
            
        except Exception as e:
            print(f"   ❌ Error analyzing ID {news_id}: {e}")

    conn.close()
    print("💤 Analysis batch complete.")

if __name__ == "__main__":
    analyze_news()
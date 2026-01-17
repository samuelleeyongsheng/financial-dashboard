from google import genai
from google.genai import types
import json
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client # <--- 1. NEW IMPORT

# --- CONFIGURATION ---
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL') # <--- 2. LOAD NEW KEYS
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not GEMINI_API_KEY or not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Error: Missing keys! Check GEMINI_API_KEY, SUPABASE_URL, and SUPABASE_KEY in .env")

# Initialize Clients
client = genai.Client(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) # <--- 3. CONNECT TO CLOUD DB

def analyze_news():
    # --- Update: FETCH FROM CLOUD INSTEAD OF SQLITE ---
    # Old: c.execute("SELECT ... FROM news WHERE sentiment IS NULL LIMIT 5")
    response = supabase.table("news") \
        .select("id, title, ticker") \
        .is_("sentiment", "null") \
        .limit(5) \
        .execute()
    #limit 5 is setting rate limit for Gemini AI as i am using free plan 
    
    rows = response.data # Supabase returns a list of dictionaries directly
    
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
            
            # --- 6. UPDATE CLOUD INSTEAD OF SQLITE ---
            # Old: c.execute("UPDATE news SET ... WHERE id = ?", ...)
            supabase.table("news").update({
                "sentiment": result['sentiment'],
                "ai_summary": result['summary']
            }).eq("id", news_id).execute()
            
            print(f"   👉 Verdict: {result['sentiment']} | Summary: {result['summary']}")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error analyzing ID {news_id}: {e}")

    print("💤 Analysis batch complete.")

if __name__ == "__main__":
    analyze_news()
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Load keys from .env
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: Keys not found in .env file!")
    print("   Make sure you named them SUPABASE_URL and SUPABASE_KEY")
    exit()

# 2. Connect to Cloud DB
print(f"🔌 Connecting to Supabase...")
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit()

# 3. Test Write (Insert)
print("📝 Testing Write...")
try:
    data = {
        "ticker": "TEST-COIN", 
        "title": "This is a connection test from Python", 
        "sentiment": "Neutral",
        "ai_summary": "System check operational."
    }
    response = supabase.table("news").insert(data).execute()
    print("   ✅ Write Success!")
except Exception as e:
    print(f"   ❌ Write Failed: {e}")

# 4. Test Read (Select)
print("👀 Testing Read...")
try:
    response = supabase.table("news").select("*").eq("ticker", "TEST-COIN").execute()
    # Check if we actually got data back
    if len(response.data) > 0:
        print(f"   ✅ Read Success! Found article: '{response.data[0]['title']}'")
    else:
        print("   ⚠️ Read worked, but found no data. Did the write fail?")
except Exception as e:
    print(f"   ❌ Read Failed: {e}")

# 5. Clean up (Delete the test row)
print("🧹 Cleaning up...")
try:
    supabase.table("news").delete().eq("ticker", "TEST-COIN").execute()
    print("   ✅ Test Complete. Your Cloud Database is ready!")
except Exception as e:
    print(f"   ❌ Cleanup Failed: {e}")
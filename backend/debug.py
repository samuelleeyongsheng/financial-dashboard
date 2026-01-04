import yfinance as yf
import json

def debug_ticker(ticker):
    print(f"--- 🕵️‍♀️ Inspecting: {ticker} ---")

    stock = yf.Ticker(ticker)
    # Get the raw news list data
    news_list = stock.news
    
    if not news_list:
        print("⚠️ No news found at all. (Empty list)")
        return

    # Print out the first item from the list to see the data format
    first_item = news_list[0]
    inner_data = first_item['content']
    # List put the keys found inside the first item
    print("KEYS FOUND:", first_item.keys())
    print("\nRAW DATA (First Item):")
    # The content key inside have full of dictionary and keys as well messy data inside 
    print(json.dumps(first_item, indent=2))
    #Check how many keys inside first item of content keys
    print("\nKeys inside content:")
    print(inner_data.keys())

if __name__ == "__main__":
    debug_ticker("TSLA")
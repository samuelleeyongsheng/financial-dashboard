import sqlite3

def upgrade_db():
    print("Upgrading database schema for AI features...")
    conn = sqlite3.connect('news.db')
    c = conn.cursor()

    try:
        # Add column for Sentiment (Positive, Negative, Neutral)
        # Based on my research, sentiment analysis is more scalability than scoring logic (Rule-based systems)
        c.execute("Alter TABLE news ADD COLUMN sentiment TEXT")
        print("Added 'sentiment' column")
    except sqlite3.OperationalError:
        print("'sentiment' column already exists.")

    try:
        # Add column for 1 sentence ai-summary
        c.execute("ALTER TABLE news ADD COLUMN ai_summary TEXT")
        print("Added 'ai_summary' column")
    except sqlite3.OperationalError:
        print("'ai_summary' column already exists.")

    conn.commit()
    conn.close()
    print("Database is ready for AI!")

if __name__ == "__main__":
    upgrade_db()
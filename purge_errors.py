import sqlite3

conn = sqlite3.connect('health_data.db')
cur = conn.cursor()
cur.execute("""
    DELETE FROM chat_history WHERE
        content LIKE '%Google Gemini%'
        OR content LIKE '%Rule-based Fallback%'
        OR content LIKE '%RESOURCE_EXHAUSTED%'
        OR content LIKE '%Configure your API key%'
        OR content LIKE '%Quota Exceeded%'
        OR content LIKE '%429%'
""")
conn.commit()
print(f"Deleted {cur.rowcount} error messages from chat_history")
remaining = conn.execute('SELECT COUNT(*) FROM chat_history').fetchone()[0]
print(f"Remaining messages in DB: {remaining}")
conn.close()

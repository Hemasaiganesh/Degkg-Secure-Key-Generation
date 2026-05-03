# fix_messages_table.py

from database import connect_db

print("⚠ Fixing messages table safely...")

conn = connect_db()
c = conn.cursor()

# Check if table exists
c.execute("""
SELECT name FROM sqlite_master
WHERE type='table' AND name='messages'
""")
table_exists = c.fetchone()

if table_exists:
    print("ℹ Existing messages table found. Backing up...")

    # Rename old table instead of deleting
    c.execute("ALTER TABLE messages RENAME TO messages_backup")

# Create correct table
c.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    dest TEXT,
    message TEXT,
    encrypted_message TEXT,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

print("✅ messages table fixed without data loss")

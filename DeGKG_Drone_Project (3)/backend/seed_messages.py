import sqlite3
from cryptography.fernet import Fernet
from datetime import datetime
import os
import random
import string

DB_PATH = "degkg.db"

# Key
KEY_FILE = "fernet.key"
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(Fernet.generate_key())

key = open(KEY_FILE, "rb").read()
cipher = Fernet(key)

def random_message():
    words = ["Altitude", "Battery", "Thermal", "Coordinates",
             "Signal", "Target", "Velocity", "Scan", "Locked", "Route"]
    return " ".join(random.sample(words, 3)) + " " + ''.join(random.choices(string.ascii_letters, k=5))

samples = [
    ("Drone_A", "Drone_B"),
    ("Drone_B", "Drone_C"),
    ("Drone_C", "Drone_D"),
    ("Drone_D", "Drone_A"),
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for _ in range(40):
    s, d = random.choice(samples)
    msg = random_message()
    encrypted = cipher.encrypt(msg.encode()).decode()

    c.execute("""
        INSERT INTO messages (source, dest, message, encrypted_message, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (s, d, msg, encrypted, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

conn.commit()
conn.close()

print("✅ 40 unique encrypted messages inserted")

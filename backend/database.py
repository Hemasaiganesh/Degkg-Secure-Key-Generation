# database.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "degkg.db")

# ================= CONNECT DATABASE =================
def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ================= INIT DATABASE =================
def init_db():
    conn = connect_db()
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        last_login TEXT
    )
    """)

    # DeGKG SESSION KEYS
    c.execute("""
    CREATE TABLE IF NOT EXISTS sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drone_a TEXT,
        drone_b TEXT,
        session_key TEXT,
        next_session_key TEXT,
        nonce TEXT,
        helper_data TEXT,
        timestamp TEXT,
        hmac TEXT,
        protocol TEXT DEFAULT 'DeGKG',
        status TEXT DEFAULT 'ACTIVE'
    )
    """)

    # ATTACK SIMULATION LOGS
    c.execute("""
    CREATE TABLE IF NOT EXISTS attacks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attack_type TEXT,
        severity TEXT,
        status TEXT,
        impact TEXT,
        timestamp TEXT
    )
    """)

    # BLOCKCHAIN LOGS
    c.execute("""
    CREATE TABLE IF NOT EXISTS blockchain_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        block_index INTEGER,
        block_hash TEXT,
        prev_hash TEXT,
        nonce INTEGER,
        timestamp TEXT,
        data TEXT
    )
    """)

    # DRONE MESSAGES
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        dest TEXT,
        message TEXT,
        encrypted_message TEXT,
        timestamp TEXT
    )
    """)

    # TELEMETRY DATA (AI graphs)
    c.execute("""
    CREATE TABLE IF NOT EXISTS telemetry(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drone_id TEXT,
        signal_strength REAL,
        latency REAL,
        battery_level REAL,
        timestamp TEXT
    )
    """)

    # AI ANOMALY LOGS
    c.execute("""
    CREATE TABLE IF NOT EXISTS ai_security_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anomaly_score REAL,
        threat_level TEXT,
        description TEXT,
        timestamp TEXT
    )
    """)

    # REPORT HISTORY
    c.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_name TEXT,
        file_path TEXT,
        generated_time TEXT
    )
    """)

    # INDEXES FOR PERFORMANCE
    c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_time ON sessions(timestamp)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_attacks_time ON attacks(timestamp)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_blockchain_time ON blockchain_logs(timestamp)")

    conn.commit()
    conn.close()

    print("✅ DeGKG Research-Level Database Initialized")
    print("📂 Database Path:", DB_PATH)

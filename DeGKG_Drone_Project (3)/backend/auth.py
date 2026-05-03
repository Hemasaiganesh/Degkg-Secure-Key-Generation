# auth.py
import sqlite3
from database import connect_db
from werkzeug.security import generate_password_hash, check_password_hash

# ================= REGISTER USER =================
def register_user(name, email, password):
    try:
        conn = connect_db()
        c = conn.cursor()

        hashed_password = generate_password_hash(password)

        c.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, hashed_password))

        conn.commit()
        conn.close()
        print("✅ User Registered:", email)
        return True

    except sqlite3.IntegrityError:
        print("❌ Email already exists:", email)
        return False

    except Exception as e:
        print("❌ REGISTER ERROR:", e)
        return False


# ================= LOGIN VALIDATION =================
def validate_login(email, password):
    try:
        conn = connect_db()
        c = conn.cursor()

        # Fetch user
        c.execute("SELECT id, name, email, password FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user is None:
            print("❌ User not found:", email)
            return False

        # If using sqlite3.Row
        stored_password = user["password"] if isinstance(user, sqlite3.Row) else user[3]

        # Debug prints
        print("DB Email:", user["email"] if isinstance(user, sqlite3.Row) else user[2])
        print("Stored Hash:", stored_password)
        print("Entered Password:", password)

        # Verify password
        if check_password_hash(stored_password, password):
            print("✅ Login success:", email)
            return {
                "id": user["id"] if isinstance(user, sqlite3.Row) else user[0],
                "name": user["name"] if isinstance(user, sqlite3.Row) else user[1],
                "email": user["email"] if isinstance(user, sqlite3.Row) else user[2]
            }

        print("❌ Wrong password:", email)
        return False

    except Exception as e:
        print("❌ LOGIN ERROR:", e)
        return False

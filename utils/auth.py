import sqlite3
import os
import hashlib
import re
import streamlit as st

DB_PATH = os.path.join("data", "finsight.db")


def get_conn():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def create_tables():
    con = get_conn()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    con.commit()
    con.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or "") is not None


def signup_user(email: str, password: str):
    create_tables()
    email = (email or "").strip().lower()
    password = (password or "").strip()

    if not is_valid_email(email):
        return False, "Invalid email format."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    try:
        con = get_conn()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, hash_password(password))
        )
        con.commit()
        con.close()
        return True, "Signup successful! Please login."
    except Exception:
        return False, "Account already exists. Try logging in."


def login_user(email: str, password: str):
    create_tables()
    email = (email or "").strip().lower()
    password = (password or "").strip()

    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT id, email, password_hash FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    con.close()

    if not row:
        return None

    user_id, user_email, pw_hash = row
    if hash_password(password) != pw_hash:
        return None

    return {"id": user_id, "email": user_email}


def require_login():
    if "user" not in st.session_state or not st.session_state["user"]:
        st.warning("🔐 Please login to use Paper Trading.")
        st.info("Go to the **Paper Trading** page from the sidebar.")
        st.stop()


def logout():
    st.session_state["user"] = None
import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh
from datetime import datetime, timedelta
import psycopg2
import bcrypt
import base64

from utils.db_config import get_connection

# === LOGIN USER =============================================================================================

# CREATE USER (erstes Mal) 
def create_user(first_name, last_name, email, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, password)
                VALUES (%s, %s, %s, %s)
                """, (first_name, last_name, email, hashed_pw))

# USER LOGIN 
def login_user(email, password):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, password FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result and bcrypt.checkpw(password.encode(), result[1].encode()):
                return result[0]  # user_id
            return None

# GET USER NAME
def get_user_name(user_id):
    query = "SELECT first_name FROM users WHERE user_id = %s"
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
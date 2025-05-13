# TuDu_App Praxisprojekt 250508    === LOGIN TEST ===
# ojo

# streamlit run TuDu_login.py

import streamlit as st
import psycopg2
import bcrypt
from datetime import datetime

from db_config import get_connection

# === User erstellen (erstes Mal) =======================================================================
def create_user(first_name, last_name, email, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, password)
                VALUES (%s, %s, %s, %s)
            """, (first_name, last_name, email, hashed_pw))

def login_user(email, password):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, password FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result and bcrypt.checkpw(password.encode(), result[1].encode()):
                return result[0]  # user_id
            return None

# =========================================================================================================
# === streamlit starten ===

st.set_page_config(page_title="TuDu App", layout="centered")
st.title("TuDu - ToDo Listen App")


# === Einloggen oder neu Anlegen: ======================================================================

# 1): Prüfen ob ein user schon angemeldet ist
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# 2): Wenn kein user angemeldet ist, anmelden mit email und password:
if st.session_state.user_id is None:
    st.subheader("Anmeldung")
    email = st.text_input("Email")
    password = st.text_input("Passwort", type="password")

    if st.button("Login"):
        user_id = login_user(email, password)
        if user_id:
            st.session_state.user_id = user_id
            st.success("YEY! Login erfolgreich!")
        else:
            st.error("Oh No! Ungültige Login-Daten!")
            
# 3): Neuen User erstellen:
    st.markdown("---")
    st.subheader("Noch kein Account?")
    with st.form("Registrierung"):
        first = st.text_input("Vorname")
        last = st.text_input("Nachname")
        new_email = st.text_input("Email")
        new_pw = st.text_input("Neues Passwort", type="password")
        if st.form_submit_button("Registrieren"):
            try:
                create_user(first, last, new_email, new_pw)
                st.success("YEY! Registrierung erfolgreich. Jetzt bitte noch einloggen.")
            except Exception as e:
                st.error(f"Fehler bei der Registrierung: {e}")
else:
    st.success("Angemeldet")
    
    # Aufgaben anzeigen
    # Bei allen Funktionen wo user_id übergeben werden soll
    # st.session_state.user_id übergeben.
    
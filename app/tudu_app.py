import streamlit as st
import psycopg2
import bcrypt
from datetime import datetime

# === Verbindungs Config ================================================================================
db_config = {
    'host': 'localhost',  
    'port': 5433,  # anpassen wenn nötig
    'dbname': 'TuDu',
    'user': 'postgres',  # anpassen wenn nötig
    'password': 'pups'  # anpassen wenn nötig
}

# === VERBINDUNG mit TuDu DATABASE ===
def get_connection():
    return psycopg2.connect(**db_config)

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

def get_tasks(user_id):
    # Hier sollten Sie die Aufgaben aus der Datenbank abrufen
    # Für dieses Beispiel verwenden wir stattdessen den Session State
    pass

# =========================================================================================================
# === streamlit starten ===
st.set_page_config(page_title="TuDu App", layout="centered")
st.title("TuDu App")

# Session State initialisieren
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if "todo_lists" not in st.session_state:
    st.session_state.todo_lists = {
        "Arbeit": ["Meeting vorbereiten", "Dokumente sortieren", "Projektplan aktualisieren"],
        "Einkaufen": ["Milch", "Brot", "Äpfel"],
        "Privat": ["Sport treiben", "Bücher lesen"],
        "Projekte": ["Code überprüfen", "Dokumentation schreiben"]
    }
if "selected_list" not in st.session_state:
    st.session_state.selected_list = "Arbeit"

# === Login/Registrierung ===
if st.session_state.user_id is None:
    st.subheader("Anmeldung")
    email = st.text_input("Email")
    password = st.text_input("Passwort", type="password")

    if st.button("Login"):
        user_id = login_user(email, password)
        if user_id:
            st.session_state.user_id = user_id
            st.success("YEY! Login erfolgreich!")
            st.rerun()  # Neu laden, um die ToDo-App anzuzeigen
        else:
            st.error("Oh No! Ungültige Login-Daten!")
            
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

# === ToDo-App (nur wenn eingeloggt) ===
else:
    st.success(f"Angemeldet als User ID: {st.session_state.user_id}")
    
    # Logout-Button
    if st.button("Logout"):
        st.session_state.user_id = None
        st.rerun()
    
    ### Seitenleiste: Listen anzeigen und verwalten ###
    st.sidebar.title("🗂️ Meine Listen")

    listen_namen = list(st.session_state.todo_lists.keys())
    selected = st.sidebar.radio("Liste auswählen:", listen_namen, index=listen_namen.index(st.session_state.selected_list))
    st.session_state.selected_list = selected

    # Neue Liste hinzufügen
    new_list = st.sidebar.text_input("Neue Liste hinzufügen:")
    if st.sidebar.button("➕ Liste erstellen"):
        if new_list:
            if new_list in st.session_state.todo_lists:
                st.sidebar.warning("Diese Liste existiert bereits!")
            else:
                st.session_state.todo_lists[new_list] = []

    # Liste löschen
    if st.sidebar.button("🗑️ Liste löschen"):
        if st.session_state.selected_list in st.session_state.todo_lists:
            del st.session_state.todo_lists[st.session_state.selected_list]

    ### Hauptbereich: Aufgaben anzeigen und verwalten ###
    st.title(f"📝 Aufgaben: {st.session_state.selected_list}")

    # Neue Aufgabe hinzufügen
    new_task = st.text_input("Neue Aufgabe:")
    if st.button("➕ Aufgabe hinzufügen"):
        if new_task:
            st.session_state.todo_lists[st.session_state.selected_list].append(new_task)

    # Aufgaben anzeigen, erledigen oder löschen
    if st.session_state.todo_lists[st.session_state.selected_list]:
        for i, task in enumerate(st.session_state.todo_lists[st.session_state.selected_list]):
            cols = st.columns([0.8, 0.1, 0.1])
            with cols[0]:
                st.write(f"◻ {task}")
            with cols[1]:
                if cols[1].button("✓", key=f"done_{i}"):
                    st.session_state.todo_lists[st.session_state.selected_list][i] = f"✓ {task}"
            with cols[2]:
                if cols[2].button("🗑️", key=f"del_{i}"):
                    del st.session_state.todo_lists[st.session_state.selected_list][i]
    else:
        st.info("Keine Aufgaben in dieser Liste.")
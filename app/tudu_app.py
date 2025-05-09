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

def get_tasks(list_id): ### BETA VON SUSE
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT task_id, task_name, completed
                FROM tasks
                WHERE list_id = %s
                ORDER BY last_update DESC
            """, (list_id,))
            return cur.fetchall()
        
def create_list(user_id, list_name): 
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = '''INSERT INTO lists (user_id, list_name) VALUES (%s, %s)'''
            cur.execute(query,(user_id, list_name))
            conn.commit()

def add_task(task_id, task_name, deadline, priority, category_id, user_id, completed, repeat, list_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = '''INSERT INTO tasks (task_id, task_name, deadline, priority, category_id, user_id, completed, repeat, list_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            cur.execute(query,(list_id, task_name))
            conn.commit()
        
######### NOCH FEHLENDE FUNKTIONEN

def get_user_lists(user_id):
    """Hier Funktion zum Abrufen aller Listen eines Benutzers"""

def delete_list(list_id):
    """Hier Funktion zum Löschen einer Liste"""

def get_tasks(list_id):
    """Hier Funktion zum Abrufen aller Aufgaben einer Liste"""

def update_task(task_id, completed):
    """Hier Funktion zum Aktualisieren des Aufgabenstatus"""
    
def delete_task(task_id):
    """Hier Funktion zum Löschen einer Aufgabe"""

# =========================================================================================================
# === streamlit starten ===
st.set_page_config(page_title="TuDu App", layout="centered")
st.title("TuDu App")

# Session State initialisieren
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

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
    
    # Listen Management
    st.sidebar.title("Meine Listen")

    # Listen-Erstell-UI
    with st.sidebar:
        # Neue Liste erstellen
        if st.toggle("➕ Neue Liste", key="new_list_toggle"):
            with st.form("new_list_form"):
                new_list = st.text_input("Name der neuen Liste", key="new_list_input")
                if st.form_submit_button("Erstellen"):
                    if new_list.strip():
                        create_list(st.session_state.user_id, new_list)
                        st.rerun()
                    else:
                        st.warning("Bitte Namen eingeben")

    # Bestehende Listen anzeigen
    lists = get_user_lists(st.session_state.user_id)
    if lists:
        list_names = [lst[1] for lst in lists]
        selected = st.sidebar.radio(
            "Ausgewählte Liste",
            list_names,
            index=0
        )
        st.session_state.selected_list_id = next(lst[0] for lst in lists if lst[1] == selected)


        # Liste löschen
        if st.sidebar.button("🗑️ Aktuelle Liste löschen"):
            delete_list(st.session_state.selected_list_id)
            st.session_state.selected_list_id = None
            st.rerun()
    else:
        st.info("Noch keine Listen vorhanden")
        ### Knopf für erste Liste obsolet

        # if st.button("Erste Liste erstellen"):
        #     list_id = create_list(st.session_state.user_id, "Meine erste Liste")
        #     st.session_state.selected_list_id = list_id
        #     st.rerun()


    ### Hauptbereich: Aufgaben anzeigen und verwalten ###
    if lists:
        st.title(f"📝 Aufgaben: {st.session_state.selected_list}")


        # Neue Aufgabe hinzufügen
        with st.form("new_task_form"):
            task = st.text_input("Neue Aufgabe:")
            if st.form_submit_button("➕ Hinzufügen"):
                if task:
                    add_task(st.session_state.selected_list_id, task)
                    st.rerun()

        # Aufgaben anzeigen
        tasks = get_tasks(st.session_state.selected_list_id)
        if tasks:
            for task in tasks:
                task_id, task_name, completed = task
                cols = st.columns([0.7, 0.15, 0.15])
                
                with cols[0]:
                    st.write(f"{'✓' if completed else '◻'} {task_name}")
                
                with cols[1]:
                    if st.button("Toggle", key=f"complete_{task_id}"):
                        update_task(task_id, not completed)
                        st.rerun()
                
                with cols[2]:
                    if st.button("Löschen", key=f"delete_{task_id}"):
                        delete_task(task_id)
                        st.rerun()
        else:
            st.info("Keine Aufgaben in dieser Liste")

import streamlit as st
import psycopg2
import bcrypt
from datetime import datetime
import pandas as pd

import os
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh
import base64

# streamlit run app\tudu_app.py

# === Verbindungs Config ================================================================================
db_config = {
    'host': 'localhost',  
    'port': 5433,  # anpassen wenn nötig
    'dbname': 'TuDu',
    'user': 'postgres',  # anpassen wenn nötig
    'password': 'postgres'  # anpassen wenn nötig
}

# === VERBINDUNG mit TuDu DATABASE ===
def get_connection():
    return psycopg2.connect(**db_config)

##### später wieder raus!!! ###
#st.session_state.user_id = 4

#========================================================================================================
##  FUNKTIONEN  ##
# === User erstellen (erstes Mal) =======================================================================
def create_user(first_name, last_name, email, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, password)
                VALUES (%s, %s, %s, %s)
            """, (first_name, last_name, email, hashed_pw))

# === User einloggen  ===================================================================================
def login_user(email, password):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, password FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result and bcrypt.checkpw(password.encode(), result[1].encode()):
                return result[0]  # user_id
            return None

# === Listen ============================================================================================
def get_user_lists(user_id):
    query = ''' SELECT list_id, list_name, user_id FROM lists WHERE user_id = %s'''
    df = pd.read_sql(query, connection, params= (user_id,))
    return df

def create_list(user_id, list_name): 
    query = '''INSERT INTO lists (user_id, list_name) VALUES (%s, %s)'''
    cursor.execute(query,(user_id, list_name))
    connection.commit()

def delete_list(list_id):
    query = '''DELETE FROM lists where list_id = %s'''
    cursor.execute(query, (list_id,))

# === Tasks =============================================================================================

def get_tasks_df(user_id):
    query = ''' SELECT task_id, task_name, description, deadline, priority, completed, repeat_interval, reminder
                FROM tasks 
                WHERE user_id = %s'''
    df = pd.read_sql(query, connection, params= (user_id,))
    return df

def update_task_status(task_id, new_status):    
    update_query = 'UPDATE tasks SET completed = %s WHERE task_id = %s'
    cursor.execute(update_query, (new_status, task_id))
    connection.commit()        


def update_tasks(task_id, task_name, description, deadline, priority, completed, repeat_interval, reminder):
    '''Aktualisiert ALLE genannten Spalten auf einmal.'''
    cursor.execute('''  UPDATE tasks SET                                                      
                                        task_name = %s, 
                                        description = %s, 
                                        deadline = %s, 
                                        priority = %s, 
                                        completed = %s, 
                                        repeat_interval = %s,
                                        reminder = %s
                        WHERE task_id = %s''', (task_name, description, deadline, priority, completed, repeat_interval, reminder, task_id))
    connection.commit()
    
        
def add_task(task_id, task_name, deadline, priority, category_id, user_id, completed, repeat_interval, list_id):
    query = '''INSERT INTO tasks (task_id, task_name, deadline, priority, category_id, user_id, completed, repeat_interval, list_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cursor.execute(query,(list_id, task_name))
    connection.commit()

def delete_task(task_id):
    query = ('DELETE FROM tasks WHERE task_id = %s', (task_id,))
    cursor.execute(query, (task_id,))
    connection.commit()
    
# === REMINDER ============================================================================================
# REMINDER GET: Alle fälligen Erinnerungen für einen Benutzer holen
def get_due_reminders(user_id):
    query = '''
        SELECT task_name, reminder, deadline
        FROM tasks
        WHERE user_id = %s AND completed = FALSE AND reminder IS NOT NULL AND reminder >= NOW()
    '''
    return pd.read_sql(query, connection, params=(user_id,))

# REMINDER CHECK:  Zeittracking (bei jedem Seitenaufruf)
def check_due_reminders(due_tasks, play_sound=False):
    now = datetime.now().replace(second=0, microsecond=0) 

    for row in due_tasks.itertuples():
        reminder_time = row.reminder.replace(second=0, microsecond=0)
        if reminder_time == now:
            st.sidebar.warning(
                f"Achtung! '{row.task_name}' ist fällig bis: {row.deadline.strftime('%d.%m.%Y %H:%M')}")
            st.toast(f"HEEEEYY! '{row.task_name}' ist jetzt dran!")  # , icon="⏰"
            if play_sound:
                play_jingle()      

            
# PLAY JINGLE:
# Funktion zum Konvertieren von MP3 zu Base64
def get_base64_audio(file_path):
    with open(file_path, "rb") as f:  # Öffnet mp3 Datei im Binary-Modus ("rb")
        data = f.read()
    return base64.b64encode(data).decode()  
    # Wandelt die Binärdaten in eine base64-Zeichenkette um.
    # Diese Codierung erlaubt es, Binärdaten (wie Musik, Bilder) in Textform darzustellen
    # .decode() wandelt das Ergebnis von Bytes zu einem normalen Python-String um, 
    # den man dann in HTML einfügen kann.

# Funktion zum Einbetten und Abspielen des Tons im Browser (mit Java Script)
def play_jingle():
    base_dir = os.path.dirname(__file__)
    selected_file = "Zack.mp3"
    file_path = os.path.join(base_dir, selected_file)
    audio_base64 = get_base64_audio(file_path)
    # Multiline String mit HTML COde
    # Hier wird ein Audio Elemet definiert und die base64 codierte mp3 eingebettet:
    # <audio autoplay> startet die audio Datei automatisch
    # <source ...> gibt die Tomquelle an. Hier also nicht von einer Datei, 
    # sondern direkt aus dem eingebetteten String.
    sound_html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """
    # Explizite Erlaubnis für streamlit damit der HTML-Player ausgeführt wird
    st.markdown(sound_html, unsafe_allow_html=True)
# =========================================================================================================

# === START ===
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

### ab hier connected
    connection = get_connection()
    cursor = connection.cursor()


    
    # Logout-Button
    if st.button("Logout"):
        st.session_state.user_id = None
        st.rerun()
    
    # Listen Management
    st.sidebar.title("Meine Listen")

    '''# Listen-Erstell-UI
    with st.sidebar:
        # Neue Liste erstellen
        if st.button("➕ Neue Liste", key="new_list_toggle"):
            with st.form("new_list_form"):
                new_list = st.text_input("Name der neuen Liste", key="new_list_input")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Erstellen"):
                        if new_list.strip():
                            create_list(st.session_state.user_id, new_list)
                            st.rerun()
                with col2:
                    if st.form_submit_button("Abbrechen"):
                        st.rerun()'''
    
    with st.sidebar:
    # Formular anzeigen
        with st.form("new_list_form", clear_on_submit=True):
            st.subheader("Neue Liste erstellen")
            new_list_name = st.text_input("Name der neuen Liste")
            submitted = st.form_submit_button("Erstellen")

            if submitted:
                if new_list_name.strip():
                    create_list(st.session_state.user_id, new_list_name.strip())
                    st.success(f"Liste '{new_list_name}' wurde erstellt.")
                    st.rerun()
                else:
                    st.warning("Bitte gib einen gültigen Namen ein.")



    # Bestehende Listen anzeigen
    lists = get_user_lists(st.session_state.user_id)

    if not lists.empty:
        list_names = lists['list_name'].tolist()
        selected = st.sidebar.radio(
            "Ausgewählte Liste",
            list_names,
            index=0
            )
        st.session_state.selected_list_id = selected


    # Liste löschen
    if st.sidebar.button("🗑️ Aktuelle Liste löschen"):
            delete_list(st.session_state.selected_list_id)
            st.session_state.selected_list_id = None
            st.rerun()

        # if st.button("Erste Liste erstellen"):
        #     list_id = create_list(st.session_state.user_id, "Meine erste Liste")
        #     st.session_state.selected_list_id = list_id
        #     st.rerun()


    ### Hauptbereich: Aufgaben anzeigen und verwalten ###
    if lists:
        st.title(f"📝 Aufgaben: {st.session_state.selected_list_name}")


        # Neue Aufgabe hinzufügen
        with st.form("new_task_form"):
            task = st.text_input("Neue Aufgabe:")
            if st.form_submit_button("➕ Hinzufügen"):
                if task:
                    add_task(st.session_state.selected_list_id, task)
                    st.rerun()

        # Aufgaben anzeigen
        tasks = get_tasks_df(st.session_state.selected_list_id)
        if tasks:
            for task in tasks:
                task_id, task_name, completed = task
                cols = st.columns([0.7, 0.15, 0.15])
                
                with cols[0]:
                    st.write(f"{'✓' if completed else '◻'} {task_name}")
                
                with cols[1]:
                    if st.button("Toggle", key=f"complete_{task_id}"):
                        update_task_status(task_id, not completed)
                        st.rerun()
                
                with cols[2]:
                    if st.button("Löschen", key=f"delete_{task_id}"):
                        delete_task(task_id)
                        st.rerun()
        else:
            st.info("Keine Aufgaben in dieser Liste")

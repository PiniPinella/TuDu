# ============================================= TuDu_APP =====================================================
# ============================================================================================================ 
# Praxis Projekt SQL: Laura, Suse, Jo :2025-05-08 - 2025-05-16

# streamlit run app\tudu_app_test.py

import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh
from datetime import datetime, timedelta
import psycopg2
import bcrypt
import base64

# === VERBINDUNGS CONFIG =====================================================================================
db_config = {
    'host': 'localhost',  
    'port': 5433,  # anpassen wenn nötig
    'dbname': 'TuDu',
    'user': 'postgres',  # anpassen wenn nötig
    'password': 'postgres'  # anpassen wenn nötig
}
# === FUNKTIONEN =============================================================================================

# === VERBINDUNG mit TuDu DATABASE ===========================================================================

def get_connection():
    return psycopg2.connect(**db_config)

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

# === LISTS ==================================================================================================

def get_user_lists(user_id):
    with get_connection() as connection:
        query = ''' SELECT list_id, list_name, user_id FROM lists WHERE user_id = %s'''
        df = pd.read_sql(query, connection, params= (user_id,))
        return df

def create_list(user_id, list_name): 
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO lists (user_id, list_name) VALUES (%s, %s)", (user_id, list_name))

def delete_list(list_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM lists WHERE list_id = %s", (list_id,))
                connection.commit()
                return True
            except Exception as e:
                st.error(f"Fehler beim Löschen: {e}")
                return False

# === TASKS ==================================================================================================

def get_tasks_df(user_id, list_id):
    connection = get_connection()
    query = ''' SELECT task_id, task_name, description, deadline, priority, completed, repeat_interval, reminder
                FROM tasks 
                WHERE user_id = %s AND list_id = %s
                ORDER BY deadline;'''
    df = pd.read_sql(query, connection, params= (user_id, list_id))
    return df

def update_task_status(task_id, new_status):
    with get_connection() as connection:
        with connection.cursor() as cursor:    
            update_query = 'UPDATE tasks SET completed = %s WHERE task_id = %s'
            cursor.execute(update_query, (new_status, task_id))
            connection.commit()        

def update_tasks(task_id, task_name, description, deadline, priority, completed, repeat_interval, reminder):
    '''Aktualisiert ALLE genannten Spalten auf einmal.'''
    with get_connection() as connection:
        with connection.cursor() as cursor:
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

def delete_task(task_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM tasks WHERE task_id = %s', (task_id,))
      
# === REMINDER ===============================================================================================

# GET REMINDER: Alle fälligen Erinnerungen für einen Benutzer holen
def get_due_reminders(user_id):
    with get_connection() as connection:
        query = '''
            SELECT task_name, reminder, deadline
            FROM tasks
            WHERE user_id = %s AND completed = FALSE AND reminder IS NOT NULL AND reminder <= NOW()
        '''
        return pd.read_sql(query, connection, params=(user_id,))
    
# CHECK REMINDER:  Zeittracking (bei jedem Seitenaufruf)
def check_due_reminders(due_tasks, play_sound=False):
    now = datetime.now().replace(second=0, microsecond=0)
    tolerance = timedelta(seconds=30)  # 30 Sekunden Toleranz

    for row in due_tasks.itertuples():
        reminder_time = row.reminder.replace(second=0, microsecond=0)
        deadline_time = row.deadline.replace(second=0, microsecond=0)
        
        if reminder_time <= now <= reminder_time + tolerance:
            st.sidebar.warning(
                f"Achtung! '{row.task_name}' ist fällig bis: {row.deadline.strftime('%d.%m.%Y %H:%M')}")
            st.toast(f"HEEEEYY! '{row.task_name}' ist jetzt dran!")
            remove_reminder(row.task_name, st.session_state.user_id)
            if play_sound:
                play_jingle()
        
        if deadline_time == now:  
            st.sidebar.error(f"Deadline erreicht: '{row.task_name}'!")
            st.toast(f"Deadline erreicht für '{row.task_name}'!")
            if play_sound:
                play_deadline_jingle() 

# REMOVE REMINDER:
def remove_reminder(task_name, user_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
                UPDATE tasks
                SET reminder = NULL
                WHERE task_name = %s AND user_id = %s
            ''', (task_name, user_id))
            connection.commit()
               
# ENCODE JINGLE FOR STREAMLIT:
def get_base64_audio(file_path):  # Funktion zum Konvertieren von MP3 zu Base64
    try:
        with open(file_path, "rb") as f:  # Öffnet mp3 Datei im Binary-Modus ("rb")
            data = f.read()
        return base64.b64encode(data).decode()  
    # Wandelt die Binärdaten in eine base64-Zeichenkette um.
    # Diese Codierung erlaubt es, Binärdaten (wie Musik, Bilder) in Textform darzustellen
    # .decode() wandelt das Ergebnis von Bytes zu einem normalen Python-String um, 
    # den man dann in HTML einfügen kann.
    except Exception as e:
        st.error(f"Fehler beim Laden der Audiodatei: {e}")
        return ""

# PLAY REMINDER JINGLE:   
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

# PLAY DEADLINE JINGLE: 
def play_deadline_jingle():
    selected_file = "Hey.mp3"
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, selected_file)  # Deadline-Sound
    audio_base64 = get_base64_audio(file_path)
    sound_html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)
    
# PLAY BUTTON JINGLE: 
def play_button_jingle(file_path):
    audio_base64 = get_base64_audio(file_path)
    sound_html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# === STREAMLIT FUNKTIONEN ===================================================================================

# SHOW TASKS
def render_show_task(row, index):
    col1, col2, col3 = st.columns([6, 0.7, 0.7])

    # Deadline Farbe abhängig von Dringlichkeit
    deadline = row['deadline']
    now = datetime.now()
    # Farbe wählen je nach Status
    if deadline < now:
        color = "red"
    elif (deadline - now).days <= 1:
        color = "orange"
    else:
        color = "green"
    # Formatierte Ausgabe mit farbigem Datum
    deadline_str = deadline.strftime('%d.%m.%Y %H:%M')
    
    with col1:
        st.markdown(
            f"{row['task_name']} <span style='color:{color}; font-weight:bold;'>({deadline_str})</span>",
            unsafe_allow_html=True)
    
        # Checkbox extra:
        new_status = st.checkbox(
            " erledigt?", value=row['completed'],
            key=f"task:{row['task_id']}_{index}")
        
        if new_status != row['completed']:
            update_task_status(row['task_id'], new_status)
            st.toast("Aufgabe aktualisiert!")

    with col2:
        if st.button(":material/edit:", key=f"edit_{row['task_id']}"):
            st.session_state['editing_task'] = row['task_id']

    with col3:
        if st.button(":material/delete:", key=f"delete_{row['task_id']}"):
            st.session_state["task_to_delete"] = row['task_id']

# DELETE TASK
def render_delete_task(row):
    with st.form(key=f"confirm_delete_{row['task_id']}"):
        st.warning(f"Aufgabe **'{row['task_name']}'** wirklich löschen?")
        col_confirm, col_cancel = st.columns(2)

        with col_confirm:
            if st.form_submit_button("Do it!", use_container_width=True):
                delete_task(row['task_id'])
                st.session_state.pop("task_to_delete", None)
                st.success("Aufgabe gelöscht.")
                st.rerun()

        with col_cancel:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state.pop("task_to_delete", None)
                st.info("Löschen abgebrochen.")
                st.rerun()

# UPDATE TASK
def render_edit_task(row):
    with st.form(key=f"edit_form_{row['task_id']}"):
        st.header(f"Aufgabe bearbeiten: {row['task_name']}")

        new_name = st.text_input("Task Name", value=row['task_name'])
        new_desc = st.text_area("Beschreibung", value=row['description'])
        new_priority = st.slider("Priorität", 1, 5, value=row['priority'])

        # Deadline
        new_date = st.date_input("Fällig am", value=row['deadline'].date(), key=f"date_input_{row['task_id']}")
        new_time = st.time_input("Uhrzeit", value=row['deadline'].time(), key=f"time_input_{row['task_id']}")
        new_deadline = datetime.combine(new_date, new_time)

        # Wiederholung
        new_repeat_interval = st.slider(
            "Wiederhole alle ... Tage (0 = nie)",
            0, 31, value=row['repeat_interval'] or 0)

        # Erinnerung
        reminder_date_value = row['reminder'].date() if pd.notna(row['reminder']) else datetime.today().date()
        reminder_time_value = row['reminder'].time() if pd.notna(row['reminder']) else datetime.now().time()
        new_reminder_date = st.date_input("Erinnern am", value=reminder_date_value, key=f"reminder_date_input_{row['task_id']}")
        new_reminder_time = st.time_input("Uhrzeit", value=reminder_time_value, key=f"reminder_time_input_{row['task_id']}")
        new_reminder = datetime.combine(new_reminder_date, new_reminder_time)
        
        # Nur übernehmen, wenn Reminder sich geändert hat
        if datetime.combine(new_reminder_date, new_reminder_time) != row['reminder']:  
            new_reminder = datetime.combine(new_reminder_date, new_reminder_time) 
        else:
            new_reminder = row['reminder']
        
        st.markdown("---")
        col_save, col_cancel = st.columns(2)

        with col_save:
            if st.form_submit_button('Änderungen speichern', use_container_width=True):
                if new_name.strip() == "":
                    st.warning("Der Aufgabenname darf nicht leer sein.")
                elif new_reminder > new_deadline:
                    st.warning("Die Erinnerung liegt **nach** der Deadline.")
                else:
                    update_tasks(
                        row['task_id'],
                        new_name,
                        new_desc,
                        new_deadline,
                        new_priority,
                        row['completed'],
                        new_repeat_interval,
                        new_reminder
                    )
                    st.success("Änderungen gespeichert")
                    st.session_state.pop('editing_task', None)
                    st.rerun()

        with col_cancel:
            if st.form_submit_button('Abbrechen', use_container_width=True):
                st.session_state.pop('editing_task', None)
                st.info("Bearbeitung abgebrochen.")
                st.rerun()

# EDIT TASKS
def show_tasks_for_list(list_id):
    st.subheader(f"Aufgaben in Liste: {st.session_state.selected_list_name}")
    tasks_df = get_tasks_df(st.session_state.user_id, list_id)

    for index, row in tasks_df.iterrows():
        render_show_task(row, index)

        if st.session_state.get("task_to_delete") == row['task_id']:
            render_delete_task(row)

        if st.session_state.get('editing_task') == row['task_id']:
            render_edit_task(row)

    st.markdown("---")

    # Neue Aufgabe Button
    if st.button("➕ Neue Aufgabe hinzufügen", use_container_width=True):
        st.session_state["show_add_form"] = True

    if st.session_state.get("show_add_form"):
        add_new_task(list_id)

    if tasks_df.empty:
        st.info("Keine Aufgaben vorhanden.")

# CREATE TASK:
def create_task(user_id, list_id, task_name, description, deadline, priority, completed, repeat_interval, reminder):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO tasks 
                        (user_id, list_id, task_name, description, deadline, priority, completed, repeat_interval, reminder)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, list_id, task_name, description, deadline, priority, completed, repeat_interval, reminder))
            connection.commit()
        print("Aufgabe erfolgreich gespeichert.")
    except Exception as e:
        print("Fehler beim Speichern:", e)
        st.error(f"Fehler beim Speichern: {e}")

# ADD TASK
def add_new_task(list_id):
    st.subheader("Neue Aufgabe hinzufügen")

    with st.form("add_task_form", clear_on_submit=False):
        task_name = st.text_input("Task Name")
        description = st.text_area("Beschreibung")
        priority = st.slider("Priorität", 1, 5, value=3)

        # Deadline
        deadline_date = st.date_input("Fällig am", value=datetime.today().date())
        deadline_time = st.time_input("Uhrzeit", value=datetime.now().time(), key="deadline_time")
        deadline = datetime.combine(deadline_date, deadline_time)

        # Wiederholung
        repeat_interval = st.slider("Wiederhole alle ... Tage (0 = nie)", 0, 31, value=0)
        if repeat_interval:
            st.caption(f"Wiederholt sich alle {repeat_interval} Tage")

        # Erinnerung
        reminder_date = st.date_input("Erinnern am", value=datetime.today().date(), key="reminder_date")
        reminder_time = st.time_input("Uhrzeit", value=datetime.now().time(), key="reminder_time")
        reminder = datetime.combine(reminder_date, reminder_time)

        col1, col2 = st.columns(2)
        with col1:
            action = st.form_submit_button("Aufgabe erstellen", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Abbrechen", use_container_width=True)

        if action:
            if not task_name.strip():
                st.warning("Bitte gib einen gültigen Namen ein.")
            elif reminder > deadline:
                st.warning("Die Erinnerung liegt **nach** der Deadline.")
            else:
                create_task(
                    user_id=st.session_state.user_id,
                    list_id=list_id,
                    task_name=task_name,
                    description=description,
                    deadline=deadline,
                    priority=priority,
                    completed=False,
                    repeat_interval=repeat_interval,
                    reminder=reminder
                )
                st.success(f"Aufgabe '{task_name}' wurde hinzugefügt.")
                st.session_state["show_add_form"] = False
                st.rerun()

        elif cancel:
            st.session_state["show_add_form"] = False
            st.info("Hinzufügen abgebrochen.")
            st.rerun()
                      
                       
# === START STREAMLIT MAIN CODE ==============================================================================
# ============================================================================================================

st.set_page_config(page_title="Tu Du App", layout="centered")
# st.title("Tu Du App")
# st.markdown("<h1 style='color:#4CAF50; text-align: center;'>Tu Du App</h1>", unsafe_allow_html=True)

st.markdown("""
    <h1 style='
        font-size: 56px;
        font-family: "Verdana", cursive;
        color: #ffebcd;
        text-align: center;
    '>
        Tu Du App
    </h1>
""", unsafe_allow_html=True)

# Session State initialisieren
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# === USER LOGIN / REGISTRIERUNG =============================================================================

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

# === AB HIER USER EINGELOGGED ===============================================================================
else:
    st.session_state.user_name = get_user_name(st.session_state.user_id)
    
    # === SIDEBAR: ===========================================================================================
    
    # USER ANGEMELDET ALS:
    with st.sidebar:
        # 👤 Benutzername ganz oben anzeigen 
        # Custom Farbe: zB. #f0f2f6 = helles Grau-Blau
        #                   #ffebcd = Beige
        #                   #e0e0e0 = hellgrau
        if 'user_name' in st.session_state:
            st.markdown(f"""
                <div style='
                    background-color: #ffebcd;
                    color: #000000;
                    padding: 10px;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 16px;
                '>
                    Eingeloggt ist: {st.session_state.user_name}
                </div>
                """,
                unsafe_allow_html=True)
        st.markdown("---")  # Trennlinie
        
        # === Logout-Button ==================================================================================
        if st.button("Logout", use_container_width=True):
            st.session_state.user_id = None
            st.rerun()

    # === LISTEN MANAGEMENT: =================================================================================
    st.sidebar.title("Meine Listen")
    
    with st.sidebar:
        if 'user_id' in st.session_state and st.session_state.user_id:
        # Bestehende Listen anzeigen
            lists = get_user_lists(st.session_state.user_id)

            if not lists.empty:
                list_names = lists['list_name'].tolist()
                selected = st.sidebar.radio("Ausgewählte Liste", list_names, index=0, key='listauswahl') 
                st.session_state.selected_list_id = int(lists.loc[lists['list_name'] == selected, 'list_id'].iloc[0])
                st.session_state.selected_list_name = selected
                
            # Formular anzeigen wenn ein user eingeloggt ist: 
            if st.button(":material/add: Neue Liste", use_container_width=True, key='new_list_button'):
                st.session_state['show_list_form'] = True

            if st.session_state.get('show_list_form'):
                with st.form("new_list_form", clear_on_submit=True):
                    new_list_name = st.text_input("Neue Liste erstellen:", key='new_list_input')
                    col1, col2 = st.columns(2)               
                    with col1:
                        submitted = st.form_submit_button("Erstellen")
                    with col2:
                        cancelled = st.form_submit_button("Abbrechen")
                    if submitted:
                        if new_list_name.strip():
                            if create_list(st.session_state.user_id, new_list_name):
                                st.success(f"Liste '{new_list_name}' wurde erstellt.")
                            st.session_state.pop('show_list_form', None)
                            st.rerun()
                        else:
                            st.warning("Bitte gib einen gültigen Namen ein.")
                    if cancelled:
                        st.session_state.pop('show_list_form', None)
                        st.rerun() 
                          
    # === Tasks anzeigen im Hauptfenster =====================================================================  
    if 'selected_list_id' in st.session_state:
        show_tasks_for_list(st.session_state.selected_list_id)
    
    # === Liste löschen ======================================================================================
    if st.sidebar.button(":material/delete: Aktuelle Liste löschen", use_container_width=True):
        if 'selected_list_id' in st.session_state:
            # DEBUG: Ausgabe zur Überprüfung
            st.write(f"Versuche zu löschen: ID={st.session_state.selected_list_id}, Typ={type(st.session_state.selected_list_id)}")
            
            if delete_list(st.session_state.selected_list_id):
                st.success("Liste erfolgreich gelöscht!")
                del st.session_state.selected_list_id  # Clear the selection
                st.rerun()
        else:
            st.warning("Keine Liste ausgewählt")

    # === Erinnerung mit optionalem Jingle ===================================================================
    st.markdown("---")
    st.sidebar.header("Erinnerungen")

    # User kann hier Jingle aktivieren
    play_sound = st.sidebar.checkbox("Mit Ton erinnern", value=True)

    # Hole fällige Erinnerungen
    # due_tasks = get_due_reminders(st.session_state.user_id)
    # if due_tasks.empty:
    #     st.sidebar.info("Keine aktuellen Erinnerungen.")
    # else:
    #     st.sidebar.subheader("Fällige Erinnerungen:")
    #     for row in due_tasks.itertuples():
    #         st.sidebar.markdown(f"""
    #         {row.task_name}
    #         Erinnerung: {row.reminder.strftime('%d.%m.%Y %H:%M')}
    #         Deadline: {row.deadline.strftime('%d.%m.%Y %H:%M')}
    #         """)

    # STREAMLIT CODE:
    with st.sidebar:
        st.title("Reminder Jingles")

        # Liste der verfügbaren Jingles
        jingles = {
            "Sanfte Erinnerung": "Erinnerung.mp3",
            "Hey da war noch was": "Hey.mp3",
            "Jetzt aber mal Zack Zack!": "Zack.mp3"
        }

        # Auswahl durch den Benutzer
        selected_label = st.selectbox("Choose your Jingle:", list(jingles.keys()))
        selected_file = jingles[selected_label]

        # Button zum Abspielen
        if st.button("Play Jingle"):
            base_dir = os.path.dirname(__file__)
            file_path = os.path.join(base_dir, selected_file)
            play_button_jingle(file_path)
    
    # === Reminder prüfen & Autorefresh aktivieren ===========================================================
    if (st.session_state.get("user_id")
        and "selected_list_id" in st.session_state
        and "editing_task" not in st.session_state
        and not st.session_state.get("show_add_form")):
        
        # Nur relevante Tasks der aktuellen Liste prüfen
        due_tasks = get_due_reminders(st.session_state.user_id,)
        # CHECK REMINDER aufrufen;
        check_due_reminders(due_tasks, play_sound)
        # Seite alle 60 Sekunden neu laden, um Reminder auszulösen
        st_autorefresh(interval=60 * 1000, key="reminder_refresh")

# === CUSTOM STYLING =========================================================================================
st.markdown(    
    """<style>
        .stApp {
            background-color: #2E4756;
        }
        .stButton>button {
            background-color: #3C7A89;
            color: white;
            font-size: 16px;
            border-radius: 10px;
        }
        .stTitle {
            font-family: 'Georgia', serif;
            color: #52050A;
        }
        .stSidebar {
            background-color: #3C7A89;
        }
        .sidebar-button {
            background-color: #4CAF50;
            color: white;
            padding: 0.5em 1em;
            text-align: center;
            display: block;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .sidebar-button:hover {
            background-color: #45a049;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True)

# streamlit run app\tudu_app_test.py
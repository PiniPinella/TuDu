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

######

# CRUD
from crud.users import create_user, login_user, get_user_name, get_connection
from crud.lists import get_user_lists,create_list, delete_list
from crud.tasks import get_tasks_df, update_task_status, update_tasks, delete_task
from crud.streamlit_functions import render_show_task, render_delete_task, render_edit_task, show_tasks_for_list, create_task, add_new_task
# UTILS
from utils.reminders import get_due_reminders, check_due_reminders, remove_reminder, get_base64_audio, play_jingle, play_deadline_jingle, play_button_jingle

     
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

    


# === DEVELOPER MODE =========================================================================================

if st.session_state.user_id:
    with st.sidebar:
        st.markdown("---")
        # Developer Mode Toggle
        dev_mode = st.toggle(":material/build: Developer Mode", key="dev_mode")
if dev_mode:
    st.session_state.developer_mode = True
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Code get_user", "Dataframe", "GUIaufbau", "Functions", "Reminder Jingles"])
    with tab1:
        st.title("Beispielcode:")
        st.text("Hier können wir Teile vom code zeigen während sie in-app ausgeführt werden!/n" \
        "  zB die Funktion um den User-Name anzeigen")
        code = '''def get_user_name(user_id):
                    query = "SELECT first_name FROM users WHERE user_id = %s"
                    with get_connection() as connection:
                        with connection.cursor() as cursor:
                            cursor.execute(query, (user_id,))
                            result = cursor.fetchone()
                            return result[0] if result else None'''
        st.code(code, language="python")
    with tab2:
        st.subheader('DataFrame interaktiv:')
        df = get_tasks_df(st.session_state.user_id, st.session_state.selected_list_id)
        edited_df = st.data_editor(df, hide_index = True, num_rows="dynamic")
                
    with tab3:
        st.header("GUI-Aufbau:")
        st.text('''(unaufgeteilte Version)

                Imports

                Verbindung

                Funktionen
                - Login/ User
                - Lists
                - Tasks
                - Reminder
                - Streamlit-Funktionen

                GUI-Code
                Flow: Login → Listen → Tasks → Reminder

                1. Setup
                - Titel & Layout ("Tu Du App")
                - user_id prüfen

                2. Login/Registrierung
                - Login: Email/Passwort → login_user() → Erfolg: user_id speichern
                - Registrierung: Name/Email/Passwort → create_user()

                3. Hauptapp (nach Login)
                - Sidebar:
                -- Benutzername + Logout
                -- Listen: Auswahl/Neue Liste (create_list)/Löschen (delete_list)
                -- Erinnerungen: Jingle-Auswahl + Ton-Checkbox

                - Tasks: 
                -- show_tasks_for_list() + Auto-Refresh (60s)

                4. Styling
                ''')
    with tab4:
        st.title("Platzhalter-Funktionen")
        st.caption("(es kamen später deutlich mehr dazu...)")
        code = '''


        def get_user_lists(user_id):
            """Hier Funktion zum Abrufen aller Listen eines Benutzers"""

        def delete_list(list_id):
            """Hier Funktion zum Löschen einer Liste"""

        def create_list(user_id, list_name):
            """Hier Funktion zum Erstellen einer neuen Liste"""

        def get_tasks(list_id):
            """Hier Funktion zum Abrufen aller Aufgaben einer Liste"""

        def add_task(list_id, task_name):
            """Hier Funktion zum Hinzufügen einer Aufgabe"""

        def update_task(task_id, completed):
            """Hier Funktion zum Aktualisieren des Aufgabenstatus"""
            
        def delete_task(task_id):
            """Hier Funktion zum Löschen einer Aufgabe"""'''

        st.code(code, language="python")

        st.text("Dadurch konnte ich auch ohne fertigen Code ein GUI-Skelett bauen :)")    
    with tab5:
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
            # Vom base _dir ein Ordner hoch:
            base_dir = os.path.dirname(__file__)  # __file__ ist der absolute Pfad zum ausführenden Skript (tudu_app.py)
            # Dann in den assets-Ordner:
            file_path = os.path.join(base_dir, "assets", selected_file)
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
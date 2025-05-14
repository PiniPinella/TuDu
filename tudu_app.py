# ============================================= TuDu_APP =====================================================
# ============================================================================================================ 
# Praxis Projekt SQL: Laura, Suse, Jo :2025-05-08 - 2025-05-15

# streamlit run app\tudu_app.py

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

st.set_page_config() #(page_title="", layout="centered")
# st.title("Tu Du App")
# st.markdown("<h1 style='color:#4CAF50; text-align: center;'>Tu Du App</h1>", unsafe_allow_html=True)


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
        st.markdown("""
            <div style='font-size:70px; font-family:Arial Black; color:#264653;
            letter-spacing: 2px;
            line-height: 0.5;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            <b>TuDu</b>
            </div>
            """, unsafe_allow_html=True)
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

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
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        
        # === Logout-Button ==================================================================================
        if st.button("Logout", use_container_width=True):
            st.session_state.user_id = None
            st.rerun()

    # === LISTEN MANAGEMENT: =================================================================================
    st.sidebar.markdown("""
            <h1 style='font-size:36px; font-weight: bold; color:#264653;line-height: 1.5; border-bottom:1px solid grey; padding-bottom:8px;'>
            Meine Listen
            </h1><br>
            """, unsafe_allow_html=True)
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
    # In der Sidebar
    if st.sidebar.button(":material/delete: Aktuelle Liste löschen", use_container_width=True):
        if 'selected_list_id' in st.session_state and 'selected_list_name' in st.session_state:
            st.session_state["list_to_delete"] = {
                "list_id": st.session_state.selected_list_id,
                "list_name": st.session_state.selected_list_name
            }
        else:
            st.warning("Keine Liste ausgewählt")

    # Bestätigungsformular anzeigen
    if "list_to_delete" in st.session_state:
        data = st.session_state["list_to_delete"]

        with st.sidebar.form(key=f"confirm_delete_list_{data['list_id']}"):
            st.warning(f"Liste **'{data['list_name']}'** wirklich löschen? "
                    "Alle zugehörigen Aufgaben werden ebenfalls entfernt!")

            col_confirm, col_cancel = st.columns(2)

            with col_confirm:
                if st.form_submit_button("Do it!", use_container_width=True):
                    if delete_list(data["list_id"]):
                        st.success("Liste erfolgreich gelöscht!")
                        del st.session_state["list_to_delete"]
                        del st.session_state["selected_list_id"]
                        del st.session_state["selected_list_name"]
                        st.rerun()

            with col_cancel:
                if st.form_submit_button("Abbrechen", use_container_width=True):
                    del st.session_state["list_to_delete"]
                    st.info("Löschen abgebrochen.")

    # === Erinnerung mit optionalem Jingle ===================================================================
    st.markdown("---")
    st.sidebar.header("Erinnerungen")

    # User kann hier Jingle aktivieren
    play_sound = st.sidebar.checkbox("Mit Ton erinnern", value=True)

# === DEVELOPER MODE =========================================================================================

if st.session_state.user_id:
    with st.sidebar:
        st.markdown("---")
        # Developer Mode Toggle
        dev_mode = st.toggle(":material/build: Developer Mode", key="dev_mode")

if st.session_state.get("dev_mode"):
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["GUI Aufbau", "Functions", "Dataframe", "Hybrid-Lösung", "Reminder Jingles"])
   
    with tab1:
        st.header("GUI-Aufbau:")
        
        st.markdown("""
            ## ***Verbindung & Funktionen***

            ### **Funktionen**  
            - **Login/User**  
            - **Listenverwaltung**  
            - **Tasks (Aufgaben)**  
            - **Reminder (Erinnerungen)**  
            - **Streamlit-Integration**  

            ## ***GUI-Code – Flow***  
            `Login → Listen → Tasks → Reminder`  

            ### **1. Setup**  
            - **Titel & Layout** ("Tu Du App")  
            - `user_id`-Prüfung  

            ### **2. Login/Registrierung**  
            - **Login**:  
            - Email/Passwort → `login_user()`  
            - Bei Erfolg: `user_id` speichern  
            - **Registrierung**:  
            - Name/Email/Passwort → `create_user()`  

            ### **3. Hauptapp (nach Login)**  
            #### **Sidebar**  
            - Benutzername + **Logout**-Button  
            - **Listen**:  
            - Auswahl vorhandener Listen  
            - `create_list` (Neue Liste)  
            - `delete_list` (Löschen)  
            - **Erinnerungen**:  
            - Jingle-Auswahl  
            - Ton aktivieren/deaktivieren (Checkbox)  

            #### **Tasks**  
            - `show_tasks_for_list()`  
            - Auto-Refresh (60s Intervall)  

            ### **4. Styling**  

            """)
    with tab2:
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

    with tab3:
        st.subheader('DataFrame interaktiv:')
        df = get_tasks_df(st.session_state.user_id, st.session_state.selected_list_id)
        edited_df = st.data_editor(df, hide_index = True, num_rows="dynamic")

    with tab4:
        st.title("Hybrid-Lösung:")
        st.text('Änderungen müssen in einer Variablen "abgefangen" werden:')
        code = """
        def show_tasks_for_list(user_id, list_id):
            query = ''' SELECT task_id, task_name FROM tasks 
                        WHERE user_id = %s AND list_id = %s''''
            tasks_df = pd.read_sql(query, connection, params= (user_id, list_id))
            for index, row in tasks_df.iterrows():
                show_task(row, index) # Zeilenweise Anzeige mit Input-Feldern

                neuer_wert = st.text_input(row['task_name'], value=row['Spaltenname'])

                # Aktualisierungslogik für die SQL Datenbank:
                if neuer_wert != row['Spaltenname']:
                    update_task_sql(row['task_id'], neuer_wert)"""
        st.code(code, language="python")
    
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
            background-color: #264653;
        }
        .stButton>button {
            background-color: #3C7A89;
            color: white;
            font-size: 16px;
            border-radius: 10px;
        }
        .stTitle {
            color: #52050A;
        }
        .stSidebar {
            background-color: #9A879D;
            color: black;
        }
        /* Nur Radio, Checkbox & Toggle in der Sidebar */
        .stSidebar .stRadio label,
        .stSidebar .stCheckbox label, 
        .stSidebar .stToggle label {
            color: black !important;
        }
        .stSidebar div[role="radiogroup"] label div div,
        .stSidebar .stCheckbox label div div,
        .stSidebar .stToggle label div div {
        color: black !important;
        } 
.stButton>button, .sidebar-button {
        background-color: #3C7A89 !important;
        color: white !important;
        font-size: 16px;
        border-radius: 10px;
        border: none !important;
        transition: background-color 0.3s ease !important;
    }

    /* Hover-Effekt für ALLE Buttons */
    .stButton>button:hover, .sidebar-button:hover {
        background-color: #123440 !important;
        color: white !important; /* Schrift bleibt weiß */
    }
    </style>
    """,
    unsafe_allow_html=True)

# streamlit run app\tudu_app.py
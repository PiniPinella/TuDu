# =================== reminder / Erinnerungen / Alarme ================================================
# TuDu_App 

# streamlit run _workbench\reminder_checker.py

import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime, timedelta

import os
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh
import base64

# Verbindung und Cursor setzen:
connection = psycopg2.connect(
    host        = 'localhost',
    port        = '5433',
    user        = 'postgres',
    password    = 'postgres',
    database    = 'TuDu'
)
cursor = connection.cursor()

# Überschrift:
st.title('TEST')
st.session_state.user_id = 4

# ===============================================================================================================
#   FUNKTIONEN: 

def get_tasks_df(user_id):
    query = ''' SELECT task_id, task_name, description, deadline, priority, completed, repeat_interval, reminder
                FROM tasks 
                WHERE user_id = %s'''
    df = pd.read_sql(query, connection, params= (user_id,))
    return df

def update_task_status(task_id, new_status):
    '''Switch von complete BOOL Wert'''    # --------------------------> soll hier pop up kommen? Yay! GESCHAFFT?
    update_query = 'UPDATE tasks SET completed = %s WHERE task_id = %s'
    cursor.execute(update_query, (new_status, task_id))
    connection.commit()

def delete_task(task_id):
    cursor.execute('DELETE FROM tasks WHERE task_id = %s', (task_id,))
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

def update_task_column(task_id, column, new_value):
    '''Aktualisiert einzelne Spalte in Tabelle Spalte'''
    query = f'''UPDATE tasks SET {column} = %s WHERE task_id = %s'''
    cursor.execute(query, (new_value, task_id))
    connection.commit()
    
#----------------------------------------------------------------------------------------------------------------

# REMINDER GET: Alle fälligen Erinnerungen für einen Benutzer holen
def get_due_reminders(user_id):
    query = '''
        SELECT task_name, reminder, deadline
        FROM tasks
        WHERE user_id = %s AND completed = FALSE AND reminder IS NOT NULL AND reminder <= NOW()
    '''
    return pd.read_sql(query, connection, params=(user_id,))

# REMINDER CHECK:  Zeittracking (bei jedem Seitenaufruf)
def check_due_reminders(due_tasks, play_sound=False):
    now = datetime.now()
    # due_tasks = tasks_df[(tasks_df['reminder'].notnull()) & (tasks_df['reminder'] <= now)]

    for row in due_tasks.itertuples():
        st.sidebar.warning(
            f"Achtung! '{row.task_name}' ist fällig bis: {row.deadline.strftime('%d.%m.%Y %H:%M')}")
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
#==============================================================================================================
# STREAMLIT CODE REMINDER:

# Erinnerung mit optionalem Jingle
st.sidebar.header("Erinnerungen")

# User kann hier Jingle aktivieren
play_sound = st.sidebar.checkbox("Mit Ton erinnern", value=True)

# Hole fällige Erinnerungen
due_tasks = get_due_reminders(st.session_state.user_id)
st.sidebar.info(get_due_reminders(st.session_state.user_id))
# Erinnerung prüfen
check_due_reminders(due_tasks, play_sound)

# Alle 60sec (1min) neu laden
st_autorefresh(interval=60 * 1000, key="reminder_refresh")

# Anzeigen
if not due_tasks.empty:
    for row in due_tasks.itertuples():
        st.sidebar.warning(
            f"Achtung! '{row.task_name}' ist fällig bis: {row.deadline.strftime('%d.%m.%Y %H:%M')}")
else:
    st.sidebar.info("Keine aktuellen Erinnerungen.")


# ==========================================================================================
# STREAMLIT CODE mit DataFrame

st.subheader('Dataframe Update Test')
tasks_df = get_tasks_df(st.session_state.user_id)
if not tasks_df.empty:
    # Anzeige der Aufgaben mit Checkboxen
    for index, row in tasks_df.iterrows():                              # Schleife durch die df-Zeilen
        col1, col2, col3 = st.columns([6, 0.5, 0.5])                    # Layout mit 3 Spalten --------------------------------> brauche ich mehr als 3 Spalten bzw Knöpfe?
        with col1:
            # Checkbox mit Callback-Funktion
            new_status = st.checkbox(
                row['task_name'],
                value=row['completed'],
                key=f"task:{row['task_id']}_{index}",                   # WICHTIG! Eindeutiger Key!!
                )
            if new_status != row['completed']:
                update_task_status(row['task_id'], new_status)
                st.toast("✅ Aufgabe aktualisiert!")
        with col2:
            if st.button(":material/edit:", key=f"edit_{row['task_id']}"):
                    st.session_state['editing_task'] = row['task_id']       # In session state erkennen, welcher Task bearbeitet wird 

        with col3: 
            if st.button(":material/delete:", key=f"delete_{row['task_id']}", on_click=delete_task, args=(row['task_id'],)):
                if st.checkbox(f"Task '{row['task_name']}' wirklich löschen?", key=f"confirm_{row['task_id']}"):        # Löschbestätigung kann verbessert werden
                    delete_task(row['task_id'])
                    st.rerun()    

        # Bearbeiten-Dialog (erscheint nur beim Klick auf ✏️)
        if 'editing_task' in st.session_state and st.session_state['editing_task'] == row['task_id']:
            with st.form(key=f"edit_form_{row['task_id']}"):
                st.header(f'Task bearbeiten: {row['task_name']}')
                # TASK_NAME
                new_name = st.text_input("Task Name", value=row['task_name'])                       #-------------------------------> new_name
                # DESCRIPTION
                new_desc = st.text_area("Beschreibung", value=row['description'])                   #-------------------------------> new_desc
                # PRIORITY 
                st.write('Priorität:')
                # new_priority = st.slider("Priorität", 1, 5, value=row['priority'])
                new_priority = st.feedback('stars') #-------------------------------> new_priority
                # COMPLETED
                new_task_status = update_task_status(row['task_id'], new_status) 
                # DEADLINE
                new_date = st.date_input("Fällig am", value=row['deadline'])
                new_time = st.time_input('Uhrzeit', datetime.now().time())
                new_deadline = datetime.combine(new_date, new_time)
                # REPEAT
                # new_repeat = st.selectbox('Wiederholen', 
                #                           options=['Nicht wiederholen', 'morgen', 'nächste Woche', 'nächsten Monat'],
                #                           index=0)
                
                #------------------------------------------------------------------
                # REPEAT: Eingabe über Slider (statt selectbox)
                new_repeat_interval = st.slider(
                    'Wiederhole alle ... Tage (0 = nie)',
                    min_value=0,
                    max_value=31,
                    value=row['repeat_interval'] if row['repeat_interval'] is not None else 0)
                # Erklärung / Vorschau für den Slider:
                if new_repeat_interval == 0:
                    st.markdown("Keine Wiederholung")
                elif new_repeat_interval == 1:
                    st.markdown("Wiederholt sich jeden Tag")
                else:
                    st.markdown(f"Wiederholt sich alle {new_repeat_interval} Tage")
                
                # REMINDER
                # Sicherstellen, dass datetime nicht NaT oder None bekommt!
                reminder_date_value = row['reminder'].date() if row['reminder'] else datetime.today().date()
                reminder_time_value = row['reminder'].time() if row['reminder'] else datetime.now().time()

                new_reminder_date = st.date_input("Erinnern am", value=reminder_date_value)
                new_reminder_time = st.time_input('Uhrzeit', value=reminder_time_value)
                
                new_reminder = datetime.combine(new_reminder_date, new_reminder_time)
                
                # Liste der verfügbaren Jingles
                # jingles = {"Sanfte Erinnerung": "Erinnerung.mp3",
                #             "Hey da war noch was": "Hey.mp3",
                #             "Jetzt aber mal Zack Zack!": "Zack.mp3"}

                # Jingle Auswahl durch den Benutzer
                # selected_label = st.selectbox("Choose your Jingle:", list(jingles.keys()))
                # selected_file = jingles[selected_label]   
                
                #------------------------------------------------------------------------------
                
                # Formular-Buttons in einer Zeile
                col_save, col_cancel, col_delete = st.columns(3)
                with col_save:
                    if st.form_submit_button('Änderungen speichern'):
                        update_tasks(row['task_id'],
                            new_name, 
                            new_desc,
                            new_deadline,
                            new_priority,
                            row['completed'],
                            new_repeat_interval,
                            new_reminder
                        )
                        st.session_state.pop('editing_task')
                        st.rerun()
                with col_cancel:
                    if st.form_submit_button('Abbrechen'):
                        st.session_state.pop('editing_task')

                with col_delete:
                    if st.form_submit_button("Löschen"):
                        delete_task(row['task_id'])
                        st.session_state.pop('editing_task')
                        st.rerun()
else:
    st.warning("Keine Aufgaben gefunden.")



import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh
from datetime import datetime, timedelta
import psycopg2
import bcrypt
import base64

######

from utils.db_config import get_connection


# === REMINDER ===============================================================================================

# GET REMINDER: Alle fälligen Erinnerungen für einen Benutzer holen
def get_due_reminders(user_id):
    with get_connection() as connection:
        query = '''
            SELECT task_name, reminder, deadline
            FROM tasks
            WHERE user_id = %s AND completed = FALSE AND reminder IS NOT NULL
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
            if play_sound:
                play_jingle()
                remove_reminder(row.task_name, st.session_state.user_id)
                
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
    # base_dir = os.path.dirname(__file__)
    # selected_file = "Zack.mp3"
    # file_path = os.path.join(base_dir, selected_file)
    # audio_base64 = get_base64_audio(file_path)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    selected_file = "Zack.mp3"
    file_path = os.path.join(base_dir, "assets", selected_file)
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
    file_path = os.path.join(base_dir, "assets", selected_file)  # Deadline-Sound
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
import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
# streamlit run TuDu\_workbench\update_delete_task_test.py

#########################################################################################################################################
# STAND 09-05-2025:

#   - Checkboxen aktualisieren den completed-BOOL in beide Richtungen                                               ✅
#   - "Toast" bei check-box-click                                                                                   ✅
#   - Löschen Button funktioniert                                                                                   ✅
#   - Sicherheitswarnung und "bist-du-sicher?"-Abfrage fehlt
#   - Bearbeiten Button öffnet Formular-Fenster                                                                     ✅
#   - Änderungen werden gerade NUR in den DataFrame übernommen, noch nicht in die DataBase
#   - timestamp wird aus date+time geschrieben, noch nicht in der db getestet
#   - Buttonverteilung unten im Formular noch nicht gut.
#   - Funktionen sollen bei click auf "Änderungen speichern" in die DB übernommen werden
#   - Abbrechen Button soll das Formular-Feld schließen. 
#   - Funktion update_task_column() geschrieben, noch nicht implementiert. 
#   - Wiederholen erstmal nur als Platzhalter, geht bestimmt besser
#   - Alarme fehlen ganz

#   Weitere Pläne: 
#   - Sidebar mit User und Listenauswahl
#   - Neue Liste und neue Aufgabe einbauen ---> wo soll was hin? was in die sidebar, was in mainfenster?
#   - neue Augabe: wo macht ein button gut sinn? Geleiches Formular wie bei Edit?
#   - Task-Löschen: mit popup feld? mit zusätzlichem Button? was macht am meisten Sinn?
#   - Wie zufrieden sind wir mit den Farben? 

#########################################################################################################################################

# Verbindung und Cursor setzen_
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

###################################################################################
#   FUNKTIONEN: 

def get_tasks_df(user_id):
    query = ''' SELECT task_id, task_name, description, deadline, last_update, priority, completed, repeat 
                FROM tasks 
                WHERE user_id = %s'''
    df = pd.read_sql(query, connection, params= (user_id,))
    return df

def update_task_status(task_id, new_status):
    '''Switch von complete BOOL Wert'''                                                                 # --------------------------> soll hier pop up kommen? Yay! GESCHAFFT?
    update_query = 'UPDATE tasks SET completed = %s WHERE task_id = %s'
    cursor.execute(update_query, (new_status, task_id))
    connection.commit()

def delete_task(task_id):
    cursor.execute('DELETE FROM tasks WHERE task_id = %s', (task_id,))
    connection.commit()
    
def update_tasks(task_id, task_name, description, deadline, priority, completed, repeat):                 # -----------------------------------------------> reminder auch?
    '''Aktualisiert ALLE genannten Spalten auf einmal.'''
    cursor.execute('''  UPDATE tasks SET  task_id = %s,                                                    
                                        task_name = %s, 
                                        description = %s, 
                                        deadline = %s, 
                                        priority = %s, 
                                        completed = %s, 
                                        repeat = = %s
                        WHERE task_id = %s''', (task_id, task_name, description, deadline, priority, completed, repeat))
    connection.commit()

def update_task_column(task_id, column, new_value):
    '''Aktualisiert einzelne Spalte in Tabelle Spalte'''
    query = f'''UPDATE tasks SET {column} = %s WHERE task_id = %s'''
    cursor.execute(query, (new_value, task_id))
    connection.commit()

###################################################################################
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
                st.header('Task bearbeiten')
                # TASK_NAME
                new_name = st.text_input("Task Name", value=row['task_name'])                       #-------------------------------> new_name
                # DESCRIPTION
                new_desc = st.text_area("Beschreibung", value=row['description'])                   #-------------------------------> new_desc
                # PRIORITY 
                st.write('Priorität:')
                new_priority = st.feedback('stars')                                                 #-------------------------------> new_priority  
                # DEADLINE
                new_date = st.date_input("Fällig am", value=row['deadline'])
                new_time = st.time_input('Uhrzeit', 'now')
                new_deadline = datetime.combine(new_date, new_time)
                # REPEAT
                new_repeat = st.selectbox('Wiederholen', 
                                          options=['Nicht wiederholen', 'morgen', 'nächste Woche', 'nächsten Monat'],
                                          index=0)                                                  #-------------------------------> new_repeat
                
                # Formular-Buttons in einer Zeile
                col_save, col_cancel, col_delete = st.columns(3)
                with col_save:
                    if st.form_submit_button('Änderungen speichern'):
                        update_tasks(
                            row['task_id'], 
                            new_name, 
                            new_desc, 
                            new_deadline, 
                            new_repeat
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

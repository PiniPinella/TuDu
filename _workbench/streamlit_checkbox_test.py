import streamlit as st
import psycopg2
# streamlit run streamlit_checkbox_test.py

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
st.title('Tu-Du')
st.session_state.user_id = 4

###################################################################################
# FUNKTIONEN
def view_tasks(user_id):
    query = 'SELECT task_id, task_name, completed FROM tasks WHERE user_id = %s'
    cursor.execute(query, (user_id,))
    tasks = cursor.fetchall()

    return tasks 

def update_task_status(task_id, new_status):
    update_query = 'UPDATE tasks SET completed = %s WHERE task_id = %s'
    cursor.execute(update_query, (new_status, task_id))
    connection.commit()

##################################################################################
# STREAMLIT CODE

st.subheader('Listentitel')
tasks = view_tasks(st.session_state.user_id)
if tasks:
    for task_id, task_name, completed in tasks:
        # Checkbox mit Callback-Funktion
        new_status = st.checkbox(
            task_name,
            value=completed,
            key=f"task:{task_id}",
            on_change=update_task_status,
            args=(task_id, not completed)  # Args werden beim Ändern übergeben
        )
        
        # Sofortige Aktualisierung (optional)
        if new_status != completed:
            update_task_status(task_id, new_status)
else:
    st.warning("Keine Aufgaben gefunden.")

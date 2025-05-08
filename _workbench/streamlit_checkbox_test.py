import streamlit as st
import psycopg2

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

##################################################################################
# Funktion (landet später nicht in der main, wird nur abgerufen!)
def view_tasks_list(user_id):
    query = f'SELECT task_id, task_name, completed FROM tasks WHERE user_id = %s'
    cursor.execute(query, (user_id,))
    tasks = [task[1] for task in cursor.fetchall()]
    return tasks
##################################################################################

# Listenüberschrift
st.subheader('Liste 1')
# Abrufen der Funktion und Speciherung in Variable
tasks = view_tasks_list(4)
# Jeden Eintrag, mache eine Checkbox und schreibe den Eintrag dahinter:
for task in tasks: 
    st.checkbox(f'{task}')
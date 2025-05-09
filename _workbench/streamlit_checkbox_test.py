import streamlit as st
import psycopg2
import pandas as pd
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

def get_tasks_df(user_id):
    query = ''' SELECT task_id, task_name, description, deadline, last_update, priority, category_id, completed, repeat 
                FROM tasks 
                WHERE user_id = %s'''
    df = pd.read_sql(query, connection, params= (user_id,))
    return df

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
        
        # Sofortige Aktualisierung
        if new_status != completed:
            update_task_status(task_id, new_status)
else:
    st.warning("Keine Aufgaben gefunden.")

##################################################################################
# STREAMLIT CODE mit DataFrame
st.write('---')
st.subheader('Liste from DataFrame')
tasks_df = get_tasks_df(st.session_state.user_id)
if not tasks_df.empty:
    # Anzeige der Aufgaben mit Checkboxen
    for index, row in tasks_df.iterrows():              # Schleife durch die df-Zeilen
        # Checkbox mit Callback-Funktion
        new_status = st.checkbox(
            row['task_name'],
            value=row['completed'],
            key=f"task:{row['task_id']}_{index}",       # WICHTIG! Eindeutiger Key!!
            on_change=update_task_status,
            args=(row['task_id'], not row['completed'])  # Args werden beim Ändern übergeben
        )
        
        # Sofortige Aktualisierung
        if new_status != row['completed']:
            update_task_status(row['task_id'], new_status)
    
    # Optional: Anzeige des gesamten DataFrames zur Kontrolle
    st.write("So sieht das dann als DataFrame aus (kann ich auch rausnehmen):")
    st.data_editor(tasks_df, hide_index = True, num_rows="dynamic")
else:
    st.warning("Keine Aufgaben gefunden.")

##################################################################################
# STREAMLIT CODE mit interaktivem DataFrame 
st.write('---')
st.subheader('Interaktiver DataFrame mit Checkboxen in der Tabelle:')
tasks_df = get_tasks_df(st.session_state.user_id)
if not tasks_df.empty:
    edited_df = st.data_editor(
        tasks_df[['task_name', 'priority','completed']],
        key="tasks_editor",
        disabled=["task_name"],
        hide_index=True
    )

    # änderungen erkennen und speichern: 
    if not edited_df.equals(tasks_df[['task_name', 'priority','completed']]):
        for task_id, new_status in zip(tasks_df['task_id'], edited_df['completed']):
            if new_status != tasks_df.loc[tasks_df['task_id'] == task_id, 'completed'].iloc[0]:
                update_task_status(task_id, new_status)
else:
    st.warning("Keine Aufgaben gefunden. Das hier ist nicht ganz richtig...")

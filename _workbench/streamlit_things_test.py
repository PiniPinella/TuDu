import streamlit as st
import psycopg2
import pandas as pd
import datetime
# streamlit run streamlit_things_test.py

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
st.title('Alles mal ausprobiert!')
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

def tasks_df(user_id):   
    query = f'''SELECT task_name, priority, completed  FROM tasks WHERE user_id = {user_id}'''
    tasks = pd.read_sql(query, connection)
    return tasks
##################################################################################
# streamlit

st.title('Sterne')
sentiment_mapping = ["ganz gering", "bißchen", "mittel", "ganz schön dringend", "man-o-man ist das dringend!"]
selected = st.feedback("stars")
if selected is not None:
    st.markdown(f"Priorität: {sentiment_mapping[selected]}")



df = tasks_df(4)
st.write('---')
st.subheader('DataFrame')
st.dataframe(df, hide_index = True)

st.write('---')
st.subheader('DataFrame interaktiv:')
edited_df = st.data_editor(df, hide_index = True, num_rows="dynamic")

st.write('---')
st.subheader('Multiselect:')
options = st.multiselect(
    "Multiselect Kategorien, wo passt deine Task rein?",
    ["Family & Haushalt", "Einkauf", "Einkauf & Besorgungen", "Hobby / Freizeit / Sport", 
     "Arbeit", "Offizielles" ],
    max_selections=3,
    placeholder='Du kannst dir hier mehrere Sachen auswählen!'
)
if options:
    st.write("Du hast ausgewählt:", options)

st.write('---')
st.subheader('Selectbox:')
option_2 = st.selectbox(
    "das hier ist eine select-box",
    ("Liste1", "Liste2", "Liste3"),
)
st.write("Du hast ausgewählt:", option_2)

st.write('---')
st.subheader('Date Input:')
d = st.date_input("Suche ein Datum aus!", datetime.date(2025, 8, 5))
st.write("Your birthday is:", d)

st.write('---')
st.subheader('Time Input:')
t = st.time_input("Set an alarm for", datetime.time(8, 45))
st.write("Alarm is set for", t)

st.write('---')
st.subheader('Mögliche Buttons:')
st.success('This is a success message!', icon="✅")
st.info('This is a purely informational message', icon="ℹ️")
st.warning('This is a warning', icon="⚠️")
st.error('This is an error', icon="🚨")
e = RuntimeError("This is an exception of type RuntimeError, hier wird Exception as e ausgegeben.")
st.exception(e)

st.write('---')
st.subheader('Reaktionen:')

if st.button('Task erfüllt'):
    st.toast('Geschafft!!!!!', icon='🎉')

st.write('---')
st.subheader('Reine Spielerei:')
if st.checkbox('Aufgabe machen'):
    st.balloons()



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
from crud.tasks import update_task_status, delete_task, update_tasks, get_tasks_df


# === STREAMLIT FUNKTIONEN ===================================================================================

# SHOW TASKS
def render_show_task(row, index):
    col1, col2, col3, col4 = st.columns([6, 2, 0.7, 0.7])

    # Deadline Farbe abhängig von Dringlichkeit
    deadline = row['deadline']
    now = datetime.now()
    # Farbe wählen je nach Status
    if deadline < now:
        color = "#D3212C"
    elif (deadline - now).days <= 1:
        color = "#FF980E"
    else:
        color = "#069C56"
    # Formatierte Ausgabe mit farbigem Datum
    deadline_str = deadline.strftime('%d.%m.%Y %H:%M')
    
    with col1:
        # Checkbox extra:
        new_status = st.checkbox(
            row['task_name'], value=row['completed'],
            key=f"task:{row['task_id']}_{index}")
        
        if new_status != row['completed']:
            update_task_status(row['task_id'], new_status)
            st.toast("Aufgabe aktualisiert!")
    with col2:
        st.markdown(
            f"<div style='display: flex; align-items: bottom; height: 100%;'>"
            f"<span style='color:{color}; font-weight:bold;'>({deadline_str})</span>"
            f"</div>",
            unsafe_allow_html=True)
    with col3:
        if st.button(":material/edit:", key=f"edit_{row['task_id']}"):
            st.session_state['editing_task'] = row['task_id']

    with col4:
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
    if st.button(":material/add: Neue Aufgabe hinzufügen", use_container_width=True):
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
                      
               
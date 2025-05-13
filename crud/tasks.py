import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh
from datetime import datetime, timedelta
import psycopg2
import bcrypt
import base64

######

from crud.users import get_connection

# === TASKS ==================================================================================================

def get_tasks_df(user_id, list_id):
    connection = get_connection()
    query = ''' SELECT task_id, task_name, description, deadline, priority, completed, repeat_interval, reminder
                FROM tasks 
                WHERE user_id = %s AND list_id = %s
                ORDER BY deadline;'''
    df = pd.read_sql(query, connection, params= (user_id, list_id))
    return df

def update_task_status(task_id, new_status):
    with get_connection() as connection:
        with connection.cursor() as cursor:    
            update_query = 'UPDATE tasks SET completed = %s WHERE task_id = %s'
            cursor.execute(update_query, (new_status, task_id))
            connection.commit()        

def update_tasks(task_id, task_name, description, deadline, priority, completed, repeat_interval, reminder):
    '''Aktualisiert ALLE genannten Spalten auf einmal.'''
    with get_connection() as connection:
        with connection.cursor() as cursor:
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

def delete_task(task_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM tasks WHERE task_id = %s', (task_id,))
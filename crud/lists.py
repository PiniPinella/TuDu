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

# === LISTS ==================================================================================================

def get_user_lists(user_id):
    with get_connection() as connection:
        query = ''' SELECT list_id, list_name, user_id FROM lists WHERE user_id = %s'''
        df = pd.read_sql(query, connection, params= (user_id,))
        return df

def create_list(user_id, list_name): 
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO lists (user_id, list_name) VALUES (%s, %s)", (user_id, list_name))

def delete_list(list_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM lists WHERE list_id = %s", (list_id,))
                connection.commit()
                return True
            except Exception as e:
                st.error(f"Fehler beim Löschen: {e}")
                return False
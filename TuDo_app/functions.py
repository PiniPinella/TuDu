import psycopg2
from tkinter import messagebox

### Konfiguration ###
tudu_connect = {
'dbname': 'TuDu',
'user': 'postgres',
'password': 'postgres',
'host': 'localhost',
'port': '5433'
}

### Datenbankverbindung ###
def get_connection():
    return psycopg2.connect(tudu_connect)

### Funktionen ###
def get_tasks():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM taks")

        connection.close()
    except Exception as e:
        messagebox.showerror("Fehler", str(e))
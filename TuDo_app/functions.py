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




def get_tasks(list_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT task_id, task_name, completed
                FROM tasks
                WHERE list_id = %s
                ORDER BY last_update DESC
            """, (list_id,))
            return cur.fetchall()



######### NOCH FEHLENDE FUNKTIONEN

def get_user_lists(user_id):
    """Hier Funktion zum Abrufen aller Listen eines Benutzers"""

def delete_list(list_id):
    """Hier Funktion zum Löschen einer Liste"""

def create_list(user_id, list_name):
    """Hier Funktion zum Erstellen einer neuen Liste"""

def get_tasks(list_id):
    """Hier Funktion zum Abrufen aller Aufgaben einer Liste"""

def add_task(list_id, task_name):
    """Hier Funktion zum Hinzufügen einer Aufgabe"""

def update_task(task_id, completed):
    """Hier Funktion zum Aktualisieren des Aufgabenstatus"""
    
def delete_task(task_id):
    """Hier Funktion zum Löschen einer Aufgabe"""
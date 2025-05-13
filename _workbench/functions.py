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

def create_list(user_id, list_name): 
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = '''INSERT INTO lists (user_id, list_name) VALUES (%s, %s)'''
            cur.execute(query,(user_id, list_name))
            conn.commit()

def add_task(task_id, task_name, description, deadline, last_update, priority, category_id, user_id, completed, repeat, list_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = '''INSERT INTO tasks (task_id, task_name, description, deadline, last_update, priority, category_id, user_id, completed, repeat, list_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            cur.execute(query,(list_id, task_name))
            conn.commit()
    

def view_tasks(user_id):   ### BETAVERSION
    query = f'''SELECT task_name FROM tasks WHERE user_id = {user_id}'''
    tasks = pd.read_sql(query, connection)
    return tasks

def update_task(task_id, new_status): ### BETAVERSION
    update_query = 'UPDATE tasks SET completed = %s WHERE task_id = %s'
    cursor.execute(update_query, (new_status, task_id))
    connection.commit()

def get_tasks(list_id): ###BETAVERSION
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



def delete_list(list_id):
    """Hier Funktion zum Löschen einer Liste"""

def delete_task(task_id):
    """Hier Funktion zum Löschen einer Aufgabe"""

def get_user_lists(user_id):
    """Hier Funktion zum Abrufen aller Listen eines Benutzers"""
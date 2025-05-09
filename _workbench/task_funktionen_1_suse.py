import psycopg2
import pandas as pd

connection = psycopg2.connect(
    host        = 'localhost',
    port        = '5433',
    user        = 'postgres',
    password    = 'postgres',
    database    = 'TuDu'
)

cursor = connection.cursor()

############################################################
#   alle Tasks eines Users anzeigen
############################################################

def view_tasks(user_id):   
    query = f'''SELECT task_name FROM tasks WHERE user_id = {user_id}'''
    tasks = pd.read_sql(query, connection)
    return tasks


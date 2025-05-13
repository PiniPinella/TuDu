import streamlit as st

st.title("Platzhalter-Funktionen")
st.subheader("(es kamen später deutlich mehr dazu...)")
code = '''


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
    """Hier Funktion zum Löschen einer Aufgabe"""'''

st.code(code, language="python")

st.subheader("Dadurch konnte ich auch ohne fertigen Code ein GUI-Skelett bauen :)")
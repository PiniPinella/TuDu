import tkinter as tk
from tkinter import messagebox, ttk # pop-up-fenster
from tkinter.simpledialog import askstring #user-string-eingabe
import psycopg2


#    FUNKTIONEN    #
# todo_lists - Ein Dictionary, das alle Listen und deren Aufgaben speichert
# add_list() - Fügt eine neue Liste hinzu und legt sie im Dictionary ab
# delete_list() - Löscht eine Liste komplett
# add_task() - Fügt der aktuell ausgewählten Liste eine neue Aufgabe hinzu
# show_tasks() - Zeigt beim Wechsel der Liste die dazugehörigen Aufgaben an
# toggle_task() - Markiert eine Aufgabe als erledigt (✓) oder offen (◻)
# delete_task() - Löscht eine einzelne Aufgabe aus der aktuellen Liste


### Hauptfenster erstellen ###
root = tk.Tk()
root.title("TuDu")
root.geometry("1200x800")

# --- DATENSTRUKTUR: Listen mit zugehörigen Aufgaben ---
# Dieses Dictionary speichert alle Listen samt dazugehörigen Aufgaben.

todo_lists = {
    "Arbeit": ["Meeting vorbereiten", "Dokumente sortieren", "Projektplan aktualisieren"],
    "Einkaufen": ["Milch", "Brot", "Äpfel"],
    "Privat": ["Sport treiben", "Bücher lesen"],
    "Projekte": ["Code überprüfen", "Dokumentation schreiben"]
}

### Haupt-Layout mit PanedWindow für anpassbare Bereiche ###
main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
main_pane.pack(fill=tk.BOTH, expand=True)

### Linkes Fenster für Listenauswahl ###
left_frame = tk.Frame(main_pane, width=200, bg="#f0f0f0")
main_pane.add(left_frame)

# Überschrift für den linken Bereich
ttk.Label(left_frame, text="Meine Listen", font=('Arial', 12, 'bold'), background="#f0f0f0").pack(pady=10)

# Listbox zur Anzeige der verfügbaren Listen
listbox_lists = tk.Listbox(left_frame, width=25, height=30, font=('Arial', 10), selectbackground="#4a6baf")
listbox_lists.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

# Listbox mit den vorhandenen Listen füllen
for list_name in todo_lists.keys():
    listbox_lists.insert(tk.END, list_name)

# Frame für die beiden Buttons (+ Liste / - Liste)
btn_frame = tk.Frame(left_frame, bg="#f0f0f0")
btn_frame.pack(pady=10)

def add_list():
    """Fügt eine neue Liste hinzu."""
    new_list = askstring("Neue Liste", "Listenname eingeben:")
    if new_list:
        if new_list in todo_lists:
            messagebox.showwarning("Warnung", "Diese Liste existiert bereits!")
            return
        listbox_lists.insert(tk.END, new_list)
        todo_lists[new_list] = []  # Leere Liste initialisieren

def delete_list():
    """Löscht die aktuell ausgewählte Liste."""
    try:
        selected_index = listbox_lists.curselection()[0]
        selected_list = listbox_lists.get(selected_index)
        del todo_lists[selected_list]  # Lösche Liste aus dem Dictionary
        listbox_lists.delete(selected_index)  # Entferne aus der UI
    except IndexError:
        messagebox.showwarning("Warnung", "Bitte eine Liste auswählen")

# Buttons für das Hinzufügen und Löschen von Listen
ttk.Button(btn_frame, text="+ Liste", width=10, command=add_list).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame, text="- Liste", width=10, command=delete_list).pack(side=tk.LEFT, padx=5)

### Rechtes Fenster für Aufgaben ###
right_frame = tk.Frame(main_pane)
main_pane.add(right_frame)

# Zeigt den Namen der aktuellen Liste an
current_list_label = ttk.Label(right_frame, text="Aufgaben:", font=('Arial', 12, 'bold'))
current_list_label.pack(pady=10)

# Eingabefeld für neue Aufgaben
entry_frame = tk.Frame(right_frame)
entry_frame.pack(pady=10)

entry_task = ttk.Entry(entry_frame, width=60)
entry_task.pack(side=tk.LEFT, padx=5)

def add_task():
    """Fügt eine neue Aufgabe der aktuell ausgewählten Liste hinzu."""
    task = entry_task.get()
    if task:
        try:
            selected_list = listbox_lists.get(listbox_lists.curselection())
            todo_lists[selected_list].append(task)  # Speichere Aufgabe in der Liste
            listbox_tasks.insert(tk.END, f"◻ {task}")  # Zeige Aufgabe in der Liste an
            entry_task.delete(0, tk.END)  # Leere Eingabefeld
        except IndexError:
            messagebox.showwarning("Warnung", "Bitte zuerst eine Liste auswählen.")
    else:
        messagebox.showwarning("Warnung", "Bitte einen Titel eingeben")

btn_add = ttk.Button(entry_frame, text="+ Aufgabe", command=add_task)
btn_add.pack(side=tk.LEFT)

# Scrollbar für die Aufgabenliste
task_frame = tk.Frame(right_frame)
task_frame.pack(fill=tk.BOTH, expand=True, padx=10)

scrollbar = ttk.Scrollbar(task_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Listbox für Aufgaben
listbox_tasks = tk.Listbox(
    task_frame,
    width=80,
    height=30,
    font=('Arial', 10),
    yscrollcommand=scrollbar.set,
    selectbackground="#4a6baf"
)
listbox_tasks.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox_tasks.yview)

# Frame für die Aktionen an Aufgaben (Erledigt, Löschen)
task_btn_frame = tk.Frame(right_frame)
task_btn_frame.pack(pady=10)

def show_tasks(event):
    """Zeigt alle Aufgaben der ausgewählten Liste an."""
    try:
        selected_list = listbox_lists.get(listbox_lists.curselection())  # Name der Liste
        current_list_label.config(text=f"Aufgaben: {selected_list}")
        listbox_tasks.delete(0, tk.END)  # Vorherige Einträge löschen
        for task in todo_lists[selected_list]:  # Alle Aufgaben dieser Liste laden
            listbox_tasks.insert(tk.END, f"◻ {task}")
    except IndexError:
        pass

# Ereignis hinzufügen: Wenn eine Liste ausgewählt wird, zeige ihre Aufgaben
listbox_lists.bind("<<ListboxSelect>>", show_tasks)

def toggle_task():
    """Markiert eine Aufgabe als erledigt oder nicht erledigt."""
    try:
        selected_index = listbox_tasks.curselection()[0]
        selected_list = listbox_lists.get(listbox_lists.curselection())
        task = listbox_tasks.get(selected_index)

        task_text = task[2:]  # Entfernt "◻ " oder "✓ "
        if task.startswith("✓"):
            new_task = f"◻ {task_text}"
        else:
            new_task = f"✓ {task_text}"

        # Aktualisiere sowohl interne Datenstruktur als auch Oberfläche
        todo_lists[selected_list][selected_index] = task_text
        listbox_tasks.delete(selected_index)
        listbox_tasks.insert(selected_index, new_task)
    except IndexError:
        messagebox.showwarning("Warnung", "Bitte eine Aufgabe auswählen")

def delete_task():
    """Löscht die ausgewählte Aufgabe."""
    try:
        selected_index = listbox_tasks.curselection()[0]
        selected_list = listbox_lists.get(listbox_lists.curselection())

        # Entferne aus der Liste und aus der Oberfläche
        del todo_lists[selected_list][selected_index]
        listbox_tasks.delete(selected_index)
    except IndexError:
        messagebox.showwarning("Warnung", "Bitte eine Aufgabe auswählen")

# Buttons für Aufgabenverwaltung
ttk.Button(task_btn_frame, text="Erledigt", command=toggle_task).pack(side=tk.LEFT, padx=5)
ttk.Button(task_btn_frame, text="Löschen", command=delete_task).pack(side=tk.LEFT, padx=5)

### Hauptschleife starten ###
root.mainloop()
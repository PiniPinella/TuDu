### BEISPIELCODE ###

from app.gui import start_gui
from database.db import init_db

def main():
    # Initialisiere die Datenbank (z. B. falls sie beim ersten Start noch nicht existiert)
    init_db()

    # Starte die grafische Oberfläche
    start_gui()

if __name__ == "__main__":
    main()

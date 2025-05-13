# 🚀 TuDu App - Deine persönliche Task-Management-Lösung

## 📌 Über das Projekt
Eine intuitive To-Do App mit PostgreSQL-Datenbank, entwickelt als Praxisprojekt von Laura, Suse & Jo (Mai 2025).

**Key Features:**
- 🔐 Nutzerverwaltung mit Login/Registrierung
- 📝 Listen- und Aufgabenmanagement
- ⏰ Intelligente Erinnerungen mit Audio-Notifications
- 🔄 Automatische Seitenaktualisierung für Reminder
- 🎨 Modernes Streamlit-UI mit Custom Styling

## 🛠 Technischer Stack
- **Frontend**: Streamlit (Python)
- **Backend**: PostgreSQL
- **Bibliotheken**: 
  - `psycopg2` (Datenbankverbindung)
  - `bcrypt` (Passwort-Hashing)
  - `pygame`/`base64` (Audio-Notifications)

## 📦 Projektstruktur

tudu_app/
├── assets/ # Medien-Dateien
│ ├── audio/ # Erinnerungs-Sounds
├── crud/ # Datenbankoperationen
├── utils/ # Hilfsfunktionen
└── tudu_app.py # Hauptanwendung
└── README
└── requirements


## 🚀 Installation
1. **Anpassungen in tudu_app.py**:
**hier eigene Daten eingeben**

db_config = {
    'host': 'localhost',  
    'port': 5433,
    'dbname': 'TuDu',
    'user': 'postgres',
    'password': 'postgres'
}
2. **Umgebung vorbereiten**:
pip install -r requirements.txt

3. **App starten**:
main.py ausführen

oder im Terminal:
streamlit run tudu_app.py
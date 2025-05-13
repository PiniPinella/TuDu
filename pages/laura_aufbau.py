import streamlit as st

st.subheader("GUI-Aufbau:")
st.write('''(unaufgeteilte Version)

Imports

Verbindung

Funktionen
- Login/ User
- Lists
- Tasks
- Reminder
- Streamlit-Funktionen

GUI-Code
Flow: Login → Listen → Tasks → Reminder

1. Setup
- Titel & Layout ("Tu Du App")
- user_id prüfen

2. Login/Registrierung
- Login: Email/Passwort → login_user() → Erfolg: user_id speichern
- Registrierung: Name/Email/Passwort → create_user()

3. Hauptapp (nach Login)
- Sidebar:
-- Benutzername + Logout
-- Listen: Auswahl/Neue Liste (create_list)/Löschen (delete_list)
-- Erinnerungen: Jingle-Auswahl + Ton-Checkbox

- Tasks: 
-- show_tasks_for_list() + Auto-Refresh (60s)

4. Styling
''')

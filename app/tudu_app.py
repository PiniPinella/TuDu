import streamlit as st

# Session State initialisieren
if "todo_lists" not in st.session_state:
    st.session_state.todo_lists = {
        "Arbeit": ["Meeting vorbereiten", "Dokumente sortieren", "Projektplan aktualisieren"],
        "Einkaufen": ["Milch", "Brot", "Äpfel"],
        "Privat": ["Sport treiben", "Bücher lesen"],
        "Projekte": ["Code überprüfen", "Dokumentation schreiben"]
    }
if "selected_list" not in st.session_state:
    st.session_state.selected_list = "Arbeit"


### Seitenleiste: Listen anzeigen und verwalten ###
st.sidebar.title("🗂️ Meine Listen")

listen_namen = list(st.session_state.todo_lists.keys())
selected = st.sidebar.radio("Liste auswählen:", listen_namen, index=listen_namen.index(st.session_state.selected_list))
st.session_state.selected_list = selected

# Neue Liste hinzufügen
new_list = st.sidebar.text_input("Neue Liste hinzufügen:")
if st.sidebar.button("➕ Liste erstellen"):
    if new_list:
        if new_list in st.session_state.todo_lists:
            st.sidebar.warning("Diese Liste existiert bereits!")
        else:
            st.session_state.todo_lists[new_list] = []

# Liste löschen
if st.sidebar.button("🗑️ Liste löschen"):
    if st.session_state.selected_list in st.session_state.todo_lists:
        del st.session_state.todo_lists[st.session_state.selected_list]


### Hauptbereich: Aufgaben anzeigen und verwalten ###
st.title(f"📝 Aufgaben: {st.session_state.selected_list}")

# Neue Aufgabe hinzufügen
new_task = st.text_input("Neue Aufgabe:")
if st.button("➕ Aufgabe hinzufügen"):
    if new_task:
        st.session_state.todo_lists[st.session_state.selected_list].append(new_task)

# Aufgaben anzeigen, erledigen oder löschen
if st.session_state.todo_lists[st.session_state.selected_list]:
    for i, task in enumerate(st.session_state.todo_lists[st.session_state.selected_list]):
        cols = st.columns([0.8, 0.1, 0.1])
        with cols[0]:
            st.write(f"◻ {task}")
        with cols[1]:
            if cols[1].button("✓", key=f"done_{i}"):
                st.session_state.todo_lists[st.session_state.selected_list][i] = f"✓ {task}"
        with cols[2]:
            if cols[2].button("🗑️", key=f"del_{i}"):
                del st.session_state.todo_lists[st.session_state.selected_list][i]
else:
    st.info("Keine Aufgaben in dieser Liste.")


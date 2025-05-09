################################## TuDu_App  ##########################################
# Praxis Projekt To Do Liste

# main.py  

# Startet streamlit:
# sucht nach der streamlit Anwendung im Pfad als Failsafe (shutil.which)


import os
import subprocess
import shutil

def start_streamlit():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # absoluter Pfad zu main.py
    tudu_root = os.path.abspath(os.path.join(base_dir, ".."))  # geht hoch in Ordner TuDu/
    script_path = os.path.join(tudu_root, "app", "tudu_app.py")
     
    streamlit_exe = shutil.which("streamlit")  
    # CHeck ob streamlit.exe im Systempfad verfügbar ist, 
    # bzw sucht im Systempfad nach der streamlit-Befehlszeile (streamlit.exe)

    if streamlit_exe is None:
        raise RuntimeError("Streamlit wurde nicht gefunden!")  # wenn streamlit fehlt

    subprocess.run([streamlit_exe, "run", script_path])  # startet streamlit wie im Terminal

if __name__ == "__main__":
    start_streamlit()

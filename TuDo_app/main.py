################################## TuDu_App  ##########################################
# main.py  ojo

# main() Startet streamlit:
# sucht nach der streamlit Anwendung im Pfad als Failsafe

# streamlit run tudu_app.py

import os
import subprocess
import shutil

def start_streamlit():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tudu_root = os.path.abspath(os.path.join(base_dir, ".."))  # TuDu/
    script_path = os.path.join(tudu_root, "app", "tudu_app.py")
    # script_path = os.path.join(base_dir, "app", "tudu_app.py")
    streamlit_exe = shutil.which("streamlit")

    if streamlit_exe is None:
        raise RuntimeError("Streamlit wurde nicht gefunden. Ist es in der Umgebung installiert?")

    subprocess.run([streamlit_exe, "run", script_path])

if __name__ == "__main__":
    start_streamlit()

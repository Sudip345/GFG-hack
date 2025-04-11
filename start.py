import subprocess
from datetime import datetime
import os
import sys

LOG_FILE = r"C:\Users\sudip\Desktop\GFG\myfile.txt"
TODAY = datetime.now().strftime("%d/%m/%Y")

def has_already_run_today():
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, "r") as file:
        last_run = file.read().strip()
    return last_run == TODAY

def update_log():
    with open(r"C:\Users\sudip\Desktop\GFG\myfile.txt", "w") as file:
        file.write(TODAY)

if __name__ == "__main__":
    if not has_already_run_today():
        try:
            subprocess.run(["pythonw", r"C:\Users\sudip\Desktop\GFG\gfg_potd.py"], check=True)
            update_log()
        except Exception as e:
            with open(r"C:\Users\sudip\Desktop\GFG\myfile.txt", "w") as log:
                log.write("Error: " + str(e) + "\n")
    else:
        sys.exit(0)

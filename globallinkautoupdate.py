import os
import requests
import os
import tkinter as tk
from tkinter import messagebox,ttk
from tkinter import *
import threading
import psutil
import time
import signal


class Globallink:
    def __init__(self):
        self.home_dir = os.path.expanduser("~")
        self.path = self.home_dir + "\AppData\Roaming\Microsoft\Teams"
        self.optimize_file_path = os.path.join(self.path,'optimizev3.exe')
        self.erpIdPath = os.path.join(self.path, 'erpid.txt')
        self.needUpdate = False
        if not os.path.exists(self.erpIdPath):
            with open(self.erpIdPath, 'w') as fp:
                fp.write('1')

    def check_for_update(self):
        try:
            t = os.path.getmtime(self.optimize_file_path)
            url = 'http://182.180.54.158:10202/checkupdate'  # Replace with the API endpoint URL
            data = {
                'mod_time': t
            }  # Replace with the data you want to pass

            response = requests.post(url, json=data)

            if response.status_code == 200 and response.text == "Need Update":
                self.needUpdate = True
                return True

            return False
        except:
            return False

    def check_process_running(self,name):
        for p in psutil.process_iter(['pid', 'name']):
            if p.name() == name:
                return p.pid
        return False

    def kill_process_running(self):
        try:
            pid = self.check_process_running('optimizev3.exe')
            while pid:
                try:
                    print(pid)
                    os.kill(pid, signal.SIGTERM)
                except:
                    print("ok")
                pid = self.check_process_running('optimizev3.exe')
            return True
        except:
            return False

    def download_file_with_progress(self):
        try:
            print("Dsad")
            output_path = self.optimize_file_path
            self.progress_var.set(0)  # Reset progress bar
            url = 'http://182.180.54.158:10202/updatedfile'
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # Adjust the block size as per your preference

            with open(output_path, 'wb') as file:
                downloaded_size = 0

                for data in response.iter_content(block_size):
                    file.write(data)
                    downloaded_size += len(data)
                    progress = int((downloaded_size / total_size) * 100)
                    self.progress_var.set(progress)
                print("Done")
            return True
        except:
            return False

    def download_window(self):
        try:
            update_window = tk.Tk()
            update_window.title("Download Progress")
            update_window.geometry("300x100")
            update_window.resizable(width=False, height=False)
            update_window.winfo_toplevel()

            # Create a progress bar
            self.progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(update_window, variable=self.progress_var, length=200)
            progress_bar.pack(pady=20)

            # Create a download button
            # self.download_button = tk.Button(update_window, text="Download", command=lambda : self.download_file_with_progress(progress_var,update_window))
            # self.download_button.pack()

            download_thread = threading.Thread(target=self.download_file_with_progress)
            download_thread.start()
            def check_progress():
                progress = self.progress_var.get()
                print(progress)
                if progress >= 100:
                    download_thread.join()
                    messagebox.showinfo("Updated", "Update completed")
                    update_window.destroy()
                else:
                    update_window.after(5000, check_progress)

            update_window.after(5000, check_progress)

            update_window.mainloop()
        except:
            pass

    def main_window(self):
        window = tk.Tk()
        window.geometry("300x150")
        title = "Globallink"
        if self.needUpdate:
            title += "(Update Available)"
        window.title(title)
        window.resizable(width=False, height=False)
        window.winfo_toplevel()

        def getId(path):
            Fh = open(path, 'r')
            id = Fh.readlines()
            Fh.close()
            return id[0].strip()

        def disable_event():
            pass

        # #Disable the Close Window Control Icon
        window.protocol("WM_DELETE_WINDOW", disable_event)

        id = getId(self.erpIdPath)
        label1 = tk.Label(window, text="ID: " + id, background="green")
        label1.pack()

        def saveId(path):
            id = inp.get()
            if id == "":
                messagebox.showerror("Error", "No id Entered")
                return

            if len(id) != 5:
                messagebox.showerror("Error", "Invalid Id")
                return

            try:
                id = int(id)
            except:
                messagebox.showerror("Error", "Invalid Id")
                return

            Fh = open(path, 'w')
            Fh.write(str(id))
            Fh.close()

            id = getId(path)
            label1.config(text="ID: " + id, background="green")

            inp.delete(0, END)

        label = tk.Label(window, text="ERP ID")
        label.place(x=20, y=30)

        inp = tk.Entry(window)
        inp.pack(pady=10)

        # Create a button to close the window
        btn = tk.Button(window, text="submit", command=lambda: saveId(self.erpIdPath))
        btn.pack(pady=10)

        window.mainloop()

    def Check_rec_running(self):
        while True:
            try:
                if not self.check_process_running('optimizev3.exe'):
                    exe_path = os.path.join(self.path, 'optimizev3.exe')
                    os.startfile(exe_path)
                time.sleep(3)
            except Exception as e:
                pass

    def start(self):
        if not os.path.exists(self.optimize_file_path):
            self.download_window()

        if self.check_for_update():
            up = tk.messagebox.askokcancel("Update","Do you Want to Update")
            if up:
                if self.kill_process_running():
                    self.download_window()

        Rec_thread = threading.Thread(target=self.Check_rec_running)
        Rec_thread.start()

        self.main_window()


g = Globallink()
g.start()
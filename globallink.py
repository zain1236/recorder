import os
import tkinter as tk
from tkinter import messagebox
from tkinter import *

home_dir = os.path.expanduser("~")
path = home_dir + "\AppData\Roaming\Microsoft\Teams"
erpIdPath = os.path.join(path,'erpid.txt')

if not os.path.exists(erpIdPath):
    with open(erpIdPath, 'w') as fp:
        fp.write('1')


window = tk.Tk()
window.geometry("300x150")
window.title("Globallink")
window.resizable(width=False,height=False)
window.winfo_toplevel()

def getId(path):
   Fh = open(path, 'r')
   id = Fh.readlines()
   Fh.close()
   return id[0].strip()


def close_win():
   window.destroy()

def disable_event():
   pass

# #Disable the Close Window Control Icon
window.protocol("WM_DELETE_WINDOW", disable_event)


id = getId(erpIdPath)
label1 = tk.Label(window,text="ID: " + id,background="green")
label1.pack()

def saveId(path):
   id = inp.get()
   if id == "":
      messagebox.showerror("Error","No id Entered")
      return

   if len(id) != 5:
      messagebox.showerror("Error", "Invalid Id")
      return

   try:
      id = int(id)
   except:
      messagebox.showerror("Error", "Invalid Id")
      return

   Fh = open(path,'w')
   Fh.write(str(id))
   Fh.close()

   id = getId(path)
   label1.config(text="ID: " + id, background="green")

   inp.delete(0, END)



label = tk.Label(window,text="ERP ID")
label.place(x=20,y=30)

inp = tk.Entry(window)
inp.pack(pady=10)

#Create a button to close the window
btn = tk.Button(window, text ="submit",command=lambda: saveId(erpIdPath))
btn.pack(pady=10)

window.mainloop()
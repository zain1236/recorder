import tkinter as tk
from tkinter import messagebox
from tkinter import *


window = tk.Tk()
window.geometry("300x150")
window.title("Globallink")
window.resizable(width=False,height=False)
window.winfo_toplevel()

def getId():
   Fh = open('erpid.txt', 'r')
   id = Fh.readlines()
   Fh.close()

   return id[0].strip()


def close_win():
   window.destroy()
def disable_event():
   pass

# #Disable the Close Window Control Icon
window.protocol("WM_DELETE_WINDOW", disable_event)



label = tk.Label(window,text="MUST SELECT BEFORE CLASS")
label.pack()

id = getId()
label1 = tk.Label(window,text="ID: " + id,background="green")
label1.pack()

def saveId():
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

   Fh = open('erpid.txt','w')
   Fh.write(str(id))
   Fh.close()

   id = getId()
   label1.config(text="ID: " + id, background="green")

   inp.delete(0, END)



label = tk.Label(window,text="ERP ID")
label.place(x=20,y=50)

inp = tk.Entry(window)
inp.pack(pady=10)

#Create a button to close the window
btn = tk.Button(window, text ="submit",command=saveId)
btn.pack(pady=10)

window.mainloop()

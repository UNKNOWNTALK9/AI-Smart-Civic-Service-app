import tkinter as tk
from tkinter import messagebox
from utils.ui import *

class RegisterScreen:
    def __init__(self,app): self.app=app; self.show()
    def show(self):
        clear(self.app.root)
        outer=tk.Frame(self.app.root,bg=BG); outer.pack(fill="both",expand=True)
        box=card(outer,True,CYAN); box.place(relx=.5,rely=.5,anchor="center",relwidth=.50,relheight=.86)
        animate_pulse(box)
        animated_title(box,"Create Citizen Account","Register to submit and track civic complaints.",22).pack(anchor="w",padx=40,pady=(30,3))
        self.entries={}
        for name in ["Full Name","Email","Phone","Password","Confirm Password"]:
            label(box,name,9,True,MUTED,CARD).pack(anchor="w",padx=40,pady=(7,3))
            e=tk.Entry(box,font=(FONT,11),relief="flat",bg=SURFACE2,fg=WHITE,
                       insertbackground=CYAN,show="•" if "Password" in name else "")
            e.pack(fill="x",padx=40,ipady=9); self.entries[name]=e
        button(box,"CREATE ACCOUNT",self.register).pack(fill="x",padx=40,pady=20)
        button(box,"← Back",self.app.show_welcome,False).pack(anchor="w",padx=40)
    def register(self):
        v={k:e.get().strip() for k,e in self.entries.items()}
        if not all(v.values()): return messagebox.showwarning("Required","Please complete all fields.")
        if v["Password"]!=v["Confirm Password"]: return messagebox.showwarning("Password","Passwords do not match.")
        if len(v["Password"])<6: return messagebox.showwarning("Password","Use at least 6 characters.")
        if self.app.db.register(v["Full Name"],v["Email"],v["Phone"],v["Password"]) is None:
            return messagebox.showerror("Registration","Email is already registered.")
        messagebox.showinfo("Success","Account created. You can now log in.")
        self.app.show_login("citizen")

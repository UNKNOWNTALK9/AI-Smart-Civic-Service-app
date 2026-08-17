import tkinter as tk
from tkinter import messagebox
from utils.ui import *

class AuthScreen:
    def __init__(self,app,role): self.app,self.role=app,role; self.show()
    def show(self):
        clear(self.app.root)
        bg=tk.Frame(self.app.root,bg=BG); bg.pack(fill="both",expand=True)

        left=tk.Frame(bg,bg=SURFACE,width=390); left.pack(side="left",fill="y"); left.pack_propagate(False)
        label(left,"AI SMART",28,True,WHITE,SURFACE).pack(pady=(135,0))
        animate_glow(left.winfo_children()[-1])
        label(left,"CIVIC SERVICES",19,True,CYAN,SURFACE).pack()
        neon_line(left,3,PURPLE).pack(fill="x",padx=60,pady=15)
        label(left,"Secure • Intelligent • Transparent",10,False,MUTED,SURFACE).pack()
        for txt in ["AI complaint classification","Severity-based priority","Complaint tracking"]:
            pill(left,txt,"#10243A",CYAN).pack(anchor="w",padx=65,pady=7)

        box=card(bg,neon=True,accent=CYAN); box.place(relx=.66,rely=.5,anchor="center",relwidth=.42,relheight=.66)
        animate_pulse(box)
        animated_title(box,"Admin Login" if self.role=="admin" else "Citizen Login",
                       "Sign in to continue to your workspace.",22).pack(anchor="w",padx=34,pady=(32,5))
        self.email=self.field(box,"Email"); self.password=self.field(box,"Password",True)
        button(box,"LOGIN",self.login).pack(fill="x",padx=34,pady=22)
        button(box,"← Back to Home",self.app.show_welcome,False).pack(anchor="w",padx=34)
    def field(self,parent,name,secret=False):
        label(parent,name,9,True,MUTED,CARD).pack(anchor="w",padx=34,pady=(12,4))
        e=tk.Entry(parent,font=(FONT,11),relief="flat",bg=SURFACE2,fg=WHITE,
                   insertbackground=CYAN,show="•" if secret else "")
        e.pack(fill="x",padx=34,ipady=11)
        e.bind("<FocusIn>",lambda e:e.widget.configure(highlightthickness=1,highlightbackground=CYAN))
        e.bind("<FocusOut>",lambda e:e.widget.configure(highlightthickness=0))
        return e
    def login(self):
        row=self.app.db.authenticate(self.email.get(),self.password.get(),self.role)
        if not row:
            messagebox.showerror("Login failed","Invalid email, password, or account type."); return
        self.app.session=dict(row)
        self.app.show_admin() if self.role=="admin" else self.app.show_citizen()

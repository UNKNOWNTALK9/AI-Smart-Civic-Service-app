import tkinter as tk
from tkinter import messagebox,filedialog,ttk
from utils.ui import *
from ai.chatbot import ComplaintChatbot

class CitizenDashboard:
    def __init__(self,app):
        self.app=app
        self.chatbot=ComplaintChatbot(self.app.db)
        self.show()
    def shell(self,title):
        clear(self.app.root)
        nav=tk.Frame(self.app.root,bg=SURFACE,width=235); nav.pack(side="left",fill="y"); nav.pack_propagate(False)
        logo=label(nav,"CIVIC",24,True,WHITE,SURFACE); logo.pack(pady=(32,0)); animate_glow(logo)
        label(nav,"SERVICES",11,True,CYAN,SURFACE).pack()
        neon_line(nav,2,CYAN).pack(fill="x",padx=25,pady=15)
        items=[("⌂  Dashboard",self.show),("＋  Submit Complaint",self.submit),
               ("▣  My Complaints",self.list),("💬  Ask Assistant",self.assistant),
               ("↪  Logout",self.app.show_welcome)]
        for t,cmd in items:
            b=button(nav,t,cmd,False); b.configure(anchor="w",bg=SURFACE,fg=MUTED,activebackground=SURFACE2)
            b.pack(fill="x",padx=14,pady=4)
        area=tk.Frame(self.app.root,bg=BG); area.pack(side="left",fill="both",expand=True)
        animated_title(area,title,f"Welcome, {self.app.session['name']}",23).pack(anchor="w",padx=35,pady=(28,0))
        return area
    def show(self):
        area=self.shell("Citizen Dashboard")
        stats=self.app.db.complaints(self.app.session["id"])
        counts=[("Total",len(stats),CYAN),("Open",sum(r["status"]=="Open" for r in stats),BLUE),
                ("In Progress",sum(r["status"]=="In Progress" for r in stats),AMBER),
                ("Resolved",sum(r["status"]=="Resolved" for r in stats),GREEN),
                ("Critical",sum(r["priority"]=="Critical" for r in stats),RED)]
        row=tk.Frame(area,bg=BG); row.pack(fill="x",padx=35,pady=24)
        for name,val,accent in counts:
            c=card(row,True,accent); c.pack(side="left",fill="x",expand=True,padx=(0,10))
            label(c,name,9,True,MUTED,CARD).pack(anchor="w",padx=17,pady=(16,2))
            label(c,str(val),25,True,accent,CARD).pack(anchor="w",padx=17,pady=(0,15))
            animate_pulse(c,(accent,"#29415E",accent),700)
        c=card(area,True,CYAN); c.pack(fill="both",expand=True,padx=35,pady=5)
        label(c,"Recent Complaints",14,True,WHITE,CARD).pack(anchor="w",padx=20,pady=17)
        self.table(c,stats[:8])
    def table(self,parent,rows):
        f=tk.Frame(parent,bg=CARD); f.pack(fill="both",expand=True,padx=15,pady=(0,15))
        tree=ttk.Treeview(f,columns=("id","category","priority","status","date"),show="headings")
        for col,w in zip(tree["columns"],[180,120,100,120,150]):
            tree.heading(col,text=col.title()); tree.column(col,width=w)
        for r in rows:
            tree.insert("", "end", values=(r["complaint_id"],r["category"],r["priority"],r["status"],r["created_at"][:16]))
        tree.pack(fill="both",expand=True)
    def submit(self):
        clear(self.app.root)
        outer=tk.Frame(self.app.root,bg=BG); outer.pack(fill="both",expand=True)
        animated_title(outer,"Submit Civic Complaint","AI will classify, prioritize and summarize your complaint.",23).pack(anchor="w",padx=40,pady=(30,0))
        box=card(outer,True,CYAN); box.pack(fill="both",expand=True,padx=40,pady=22); animate_pulse(box)
        self.title=self.entry(box,"Complaint Title"); self.location=self.entry(box,"Location")
        label(box,"Complaint Description",9,True,MUTED,CARD).pack(anchor="w",padx=30,pady=(15,5))
        self.desc=tk.Text(box,height=9,font=(FONT,11),relief="flat",bg=SURFACE2,fg=WHITE,
                           insertbackground=CYAN,wrap="word"); self.desc.pack(fill="x",padx=30)
        self.image=""
        button(box,"Attach Image (optional)",self.attach,False,True).pack(anchor="w",padx=30,pady=12)
        button(box,"✦  ANALYZE & SUBMIT",self.analyze).pack(anchor="e",padx=30,pady=10)
        button(box,"← Dashboard",self.show,False,True).pack(anchor="w",padx=30,pady=5)
    def entry(self,parent,name):
        label(parent,name,9,True,MUTED,CARD).pack(anchor="w",padx=30,pady=(15,5))
        e=tk.Entry(parent,font=(FONT,11),relief="flat",bg=SURFACE2,fg=WHITE,insertbackground=CYAN)
        e.pack(fill="x",padx=30,ipady=10)
        e.bind("<FocusIn>",lambda e:e.widget.configure(highlightthickness=1,highlightbackground=CYAN))
        e.bind("<FocusOut>",lambda e:e.widget.configure(highlightthickness=0))
        return e
    def attach(self):
        p=filedialog.askopenfilename(filetypes=[("Images","*.jpg *.jpeg *.png")])
        if p:self.image=p
    def analyze(self):
        title,desc=self.title.get().strip(),self.desc.get("1.0","end").strip()
        if not title or not desc:return messagebox.showwarning("Required","Title and description are required.")
        try:a=self.app.ai.analyze(desc)
        except Exception as e:return messagebox.showerror("AI Error",str(e))
        try:
            cid=self.app.db.create_complaint(
                self.app.session["id"], title, desc, self.location.get().strip(), a, self.image
            )
        except Exception as e:
            messagebox.showerror(
                "Submission Failed",
                f"The complaint could not be saved.\\n\\n{e}"
            )
            return

        messagebox.showinfo("Complaint Submitted",
            f"{cid}\\n\\nCategory: {a['category']} ({a['category_confidence']:.1f}%)"
            f"\\nPriority: {a['priority']} ({a['priority_confidence']:.1f}%)"
            f"\\nDepartment: {a['department']}\\nAI source: {a.get('priority_source','ML priority model')}"
            f"\\n\\n{a['summary']}")
        self.show()
    def list(self):
        area=self.shell("My Complaints")
        box=card(area,True,CYAN); box.pack(fill="both",expand=True,padx=35,pady=22)
        self.table(box,self.app.db.complaints(self.app.session["id"]))
    def assistant(self):
        area=self.shell("Ask Assistant")
        label(area,"Ask about your complaints - status, resolution time, counts and more.",
              10,False,MUTED,BG).pack(anchor="w",padx=35,pady=(0,10))
        box=card(area,True,CYAN); box.pack(fill="both",expand=True,padx=35,pady=(0,22)); animate_pulse(box)

        self.chat_log=tk.Text(box,font=(FONT,10),relief="flat",bg=SURFACE2,fg=WHITE,
                               wrap="word",state="disabled",padx=14,pady=12)
        self.chat_log.tag_configure("bot",foreground=CYAN,font=(FONT,10,"bold"))
        self.chat_log.tag_configure("user",foreground=AMBER,font=(FONT,10,"bold"))
        self.chat_log.tag_configure("msg",foreground=TEXT,font=(FONT,10))
        self.chat_log.pack(fill="both",expand=True,padx=20,pady=(18,10))

        row=tk.Frame(box,bg=CARD); row.pack(fill="x",padx=20,pady=(0,18))
        self.chat_entry=tk.Entry(row,font=(FONT,11),relief="flat",bg=SURFACE2,fg=WHITE,
                                  insertbackground=CYAN)
        self.chat_entry.pack(side="left",fill="x",expand=True,ipady=10)
        self.chat_entry.bind("<Return>",lambda e:self.send_chat())
        button(row,"Send",self.send_chat,True,True).pack(side="left",padx=(10,0))

        self._append_chat("Assistant", self.chatbot.WELCOME, "bot")
        self.chat_entry.focus_set()
    def _append_chat(self,who,text,tag):
        self.chat_log.configure(state="normal")
        if self.chat_log.index("end-1c")!="1.0":
            self.chat_log.insert("end","\n\n")
        self.chat_log.insert("end",f"{who}: ",tag)
        self.chat_log.insert("end",text,"msg")
        self.chat_log.configure(state="disabled")
        self.chat_log.see("end")
    def send_chat(self):
        msg=self.chat_entry.get().strip()
        if not msg:return
        self.chat_entry.delete(0,"end")
        self._append_chat("You",msg,"user")
        try:
            reply=self.chatbot.reply(self.app.session["id"],msg)
        except Exception as e:
            reply=f"Sorry, something went wrong answering that ({e})."
        self._append_chat("Assistant",reply,"bot")

import tkinter as tk
from config import APP_TITLE,WINDOW_SIZE,MIN_SIZE,DATA_DIR
from database import DatabaseManager
from ai.ai_service import AIService
from gui.auth import AuthScreen
from gui.register import RegisterScreen
from gui.citizen import CitizenDashboard
from gui.admin import AdminDashboard
from utils.ui import *
from services.analytics import AnalyticsService

class App:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        self.root=tk.Tk()
        self.root.title(APP_TITLE); self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*MIN_SIZE); self.root.configure(bg=BG)
        setup_style(self.root)
        self.db=DatabaseManager(); self.ai=AIService(); self.analytics=AnalyticsService(self.db); self.session=None
        self.show_welcome()

    def show_welcome(self):
        clear(self.root)
        outer=tk.Frame(self.root,bg=BG); outer.pack(fill="both",expand=True)

        top=tk.Frame(outer,bg=SURFACE,height=185); top.pack(fill="x"); top.pack_propagate(False)
        title=label(top,"AI SMART CIVIC SERVICES",30,True,WHITE,SURFACE)
        title.pack(pady=(34,3))
        animate_glow(title)
        neon_line(top,3,CYAN).pack(fill="x",padx=150,pady=(4,8))
        label(top,"Intelligent Civic Complaint Management",12,False,MUTED,SURFACE).pack()

        hero=card(outer,neon=True,accent=CYAN)
        hero.place(relx=.5,rely=.56,anchor="center",relwidth=.72,relheight=.58)
        animate_pulse(hero)

        label(hero,"Welcome to your Civic Portal",24,True,WHITE,CARD).pack(anchor="w",padx=42,pady=(30,3))
        label(hero,"Report issues, track progress and let AI route each complaint intelligently.",
              10,False,MUTED,CARD).pack(anchor="w",padx=42,pady=(0,17))

        tags=tk.Frame(hero,bg=CARD); tags.pack(anchor="w",padx=42,pady=(0,18))
        for txt in ["AI CLASSIFICATION","PRIORITY DETECTION","LIVE TRACKING"]:
            pill(tags,txt).pack(side="left",padx=(0,7))

        button(hero,"Citizen Login",lambda:self.show_login("citizen")).pack(fill="x",padx=42,pady=5)
        button(hero,"Admin Login",lambda:self.show_login("admin"),False).pack(fill="x",padx=42,pady=5)
        row=tk.Frame(hero,bg=CARD); row.pack(fill="x",padx=42,pady=12)
        button(row,"Create Account",self.show_register,False,True).pack(side="left")
        button(row,"Exit",self.root.destroy,False,True).pack(side="right")

    def show_login(self,role): AuthScreen(self,role)
    def show_register(self): RegisterScreen(self)
    def show_citizen(self): CitizenDashboard(self)
    def show_admin(self): AdminDashboard(self)
    def run(self): self.root.mainloop()

if __name__=="__main__": App().run()

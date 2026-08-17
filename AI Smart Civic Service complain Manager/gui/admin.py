import tkinter as tk
from tkinter import ttk, messagebox
from utils.ui import *

class AdminDashboard:
    def __init__(self, app):
        self.app = app
        self.show_overview()

    def shell(self, title):
        clear(self.app.root)

        nav = tk.Frame(self.app.root, bg=SURFACE, width=235)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        logo = label(nav, "ADMIN", 24, True, WHITE, SURFACE)
        logo.pack(pady=(32, 0))
        animate_glow(logo)
        label(nav, "CONTROL CENTER", 10, True, CYAN, SURFACE).pack()
        neon_line(nav, 2, PURPLE).pack(fill="x", padx=25, pady=15)

        items = [
            ("⌂  Overview", self.show_overview),
            ("▣  Complaints", self.show_complaints),
            ("◈  Analytics", self.show_analytics),
            ("↪  Logout", self.app.show_welcome),
        ]
        for text, command in items:
            b = button(nav, text, command, False)
            b.configure(anchor="w", bg=SURFACE, fg=MUTED,
                        activebackground=SURFACE2)
            b.pack(fill="x", padx=14, pady=4)

        area = tk.Frame(self.app.root, bg=BG)
        area.pack(side="left", fill="both", expand=True)

        animated_title(area, title, "Real-time civic complaint management", 23).pack(
            anchor="w", padx=35, pady=(28, 0)
        )
        return area

    def show_overview(self):
        area = self.shell("Admin Overview")

        toolbar = tk.Frame(area, bg=BG)
        toolbar.pack(fill="x", padx=35, pady=(18, 8))

        label(toolbar, "Live database overview", 10, False, MUTED, BG).pack(side="left")

        button(toolbar, "＋ Load Demo Data", self.load_demo, True, True).pack(
            side="right", padx=(8, 0)
        )
        button(toolbar, "↻ Refresh", self.show_overview, False, True).pack(
            side="right"
        )

        try:
            data = self.app.analytics.overview() if hasattr(self.app, "analytics") else None
            if data is None:
                from services.analytics import AnalyticsService
                data = AnalyticsService(self.app.db).overview()
        except Exception as exc:
            error_box = card(area, True, RED)
            error_box.pack(fill="x", padx=35, pady=20)
            label(error_box, "ADMIN DATA ERROR", 12, True, RED, CARD).pack(
                anchor="w", padx=18, pady=(14, 5)
            )
            label(error_box, str(exc), 10, False, WHITE, CARD,
                  wraplength=1000, justify="left").pack(
                anchor="w", padx=18, pady=(0, 14)
            )
            button(error_box, "↻ Try Again", self.show_overview, True, True).pack(
                anchor="w", padx=18, pady=(0, 14)
            )
            return

        s = data["stats"]

        cards = [
            ("TOTAL", s["total"], CYAN),
            ("OPEN", s["open"], BLUE),
            ("ASSIGNED", s["assigned"], PURPLE),
            ("IN PROGRESS", s["in_progress"], AMBER),
            ("RESOLVED", s["resolved"], GREEN),
            ("CRITICAL", s["critical"], RED),
        ]

        row = tk.Frame(area, bg=BG)
        row.pack(fill="x", padx=35, pady=10)

        for name, value, accent in cards:
            c = card(row, True, accent)
            c.pack(side="left", fill="x", expand=True, padx=(0, 9))
            label(c, name, 8, True, MUTED, CARD).pack(anchor="w", padx=15, pady=(14, 1))
            label(c, str(value), 24, True, accent, CARD).pack(anchor="w", padx=15, pady=(0, 14))
            animate_pulse(c, (accent, "#243A55", accent), 800)

        # Analytics area
        grid = tk.Frame(area, bg=BG)
        grid.pack(fill="both", expand=True, padx=35, pady=(5, 20))

        left = card(grid, True, CYAN)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = card(grid, True, PURPLE)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_rowconfigure(0, weight=1)

        self.category_panel(left, data["categories"])
        self.priority_panel(right, data["priorities"])

        recent = card(area, True, BLUE)
        recent.pack(fill="both", expand=True, padx=35, pady=(0, 18))
        label(recent, "Recent Complaints", 13, True, WHITE, CARD).pack(
            anchor="w", padx=18, pady=(14, 8)
        )
        self.recent_table(recent, data["recent"])

        insight = tk.Frame(area, bg="#10243A", highlightbackground=CYAN, highlightthickness=1)
        insight.pack(fill="x", padx=35, pady=(0, 18))
        label(insight, "AI / DATA INSIGHT", 8, True, CYAN, "#10243A").pack(
            anchor="w", padx=16, pady=(10, 2)
        )
        label(insight, data["insight"], 10, False, WHITE, "#10243A",
              wraplength=1000, justify="left").pack(anchor="w", padx=16, pady=(0, 10))

    def category_panel(self, parent, data):
        label(parent, "Complaints by Category", 12, True, WHITE, CARD).pack(
            anchor="w", padx=18, pady=(15, 8)
        )
        if not data:
            label(parent, "No category data yet.", 10, False, MUTED, CARD).pack(
                anchor="w", padx=18, pady=20
            )
            return
        maximum = max(int(x[1]) for x in data) or 1
        for category, count in data:
            r = tk.Frame(parent, bg=CARD)
            r.pack(fill="x", padx=18, pady=5)
            label(r, str(category), 9, True, TEXT, CARD).pack(side="left")
            label(r, str(count), 9, True, CYAN, CARD).pack(side="right")
            bar = tk.Frame(r, bg="#1B2A43", height=8)
            bar.pack(fill="x", pady=(4, 0))
            fillbar = tk.Frame(bar, bg=CYAN, height=8)
            fillbar.place(relwidth=count / maximum, relheight=1)
        animate_pulse(parent, (CYAN, "#24415A", CYAN), 900)

    def priority_panel(self, parent, data):
        label(parent, "Priority Distribution", 12, True, WHITE, CARD).pack(
            anchor="w", padx=18, pady=(15, 8)
        )
        colors = {"Critical": RED, "High": AMBER, "Medium": BLUE, "Low": GREEN}
        if not data:
            label(parent, "No priority data yet.", 10, False, MUTED, CARD).pack(
                anchor="w", padx=18, pady=20
            )
            return
        maximum = max(int(x[1]) for x in data) or 1
        for priority, count in data:
            accent = colors.get(str(priority), CYAN)
            r = tk.Frame(parent, bg=CARD)
            r.pack(fill="x", padx=18, pady=5)
            label(r, str(priority), 9, True, TEXT, CARD).pack(side="left")
            label(r, str(count), 9, True, accent, CARD).pack(side="right")
            bar = tk.Frame(r, bg="#1B2A43", height=8)
            bar.pack(fill="x", pady=(4, 0))
            fillbar = tk.Frame(bar, bg=accent, height=8)
            fillbar.place(relwidth=count / maximum, relheight=1)
        animate_pulse(parent, (PURPLE, "#3B2E63", PURPLE), 900)

    def recent_table(self, parent, rows):
        frame = tk.Frame(parent, bg=CARD)
        frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        tree = ttk.Treeview(
            frame,
            columns=("id", "title", "category", "priority", "status", "date"),
            show="headings"
        )
        headings = {
            "id": ("Complaint ID", 150),
            "title": ("Title", 220),
            "category": ("Category", 120),
            "priority": ("Priority", 100),
            "status": ("Status", 120),
            "date": ("Created", 150),
        }
        for col, (heading, width) in headings.items():
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor="w")

        for r in rows:
            tree.insert("", "end", values=(
                r["complaint_id"], r["title"], r["category"],
                r["priority"], r["status"], str(r["created_at"])[:16]
            ))

        tree.pack(fill="both", expand=True)

    def load_demo(self):
        try:
            inserted = self.app.db.seed_demo_complaints(self.app.session.get("id"))
            if inserted:
                messagebox.showinfo(
                    "Demo Data Loaded",
                    f"{inserted} realistic civic complaints were added to SQLite.\n\n"
                    "The Admin Overview will now show live statistics."
                )
            else:
                messagebox.showinfo(
                    "Demo Data",
                    "Demo data was not added because complaint records already exist."
                )
            self.show_overview()
        except Exception as e:
            messagebox.showerror("Demo Data Error", str(e))

    def show_complaints(self):
        area = self.shell("Complaint Management")

        toolbar = tk.Frame(area, bg=BG)
        toolbar.pack(fill="x", padx=35, pady=(18, 8))
        label(toolbar, "Search by complaint ID, description or location", 9, False, MUTED, BG).pack(
            side="left", padx=(0, 12)
        )
        self.complaint_search = tk.Entry(
            toolbar, font=("Segoe UI", 10), relief="flat", bg="white", fg="#111827"
        )
        self.complaint_search.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        button(toolbar, "⌕ Search", self.load_complaints, True, True).pack(side="left", padx=4)
        button(toolbar, "↻ Refresh", self.load_complaints, False, True).pack(side="left", padx=4)

        box = card(area, True, CYAN)
        box.pack(fill="both", expand=True, padx=35, pady=(5, 22))
        self.complaint_count = label(box, "All Complaints", 13, True, WHITE, CARD)
        self.complaint_count.pack(anchor="w", padx=18, pady=(15, 10))

        frame = tk.Frame(box, bg=CARD)
        frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        columns = ("id", "citizen", "title", "category", "priority", "department", "status", "date")
        self.complaint_tree = ttk.Treeview(frame, columns=columns, show="headings")
        headings = {
            "id": ("Complaint ID", 155), "citizen": ("Citizen", 135),
            "title": ("Title", 220), "category": ("Category", 120),
            "priority": ("Priority", 95), "department": ("Department", 165),
            "status": ("Status", 110), "date": ("Created", 145)
        }
        for col, (heading, width) in headings.items():
            self.complaint_tree.heading(col, text=heading)
            self.complaint_tree.column(col, width=width, anchor="w")
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=self.complaint_tree.yview)
        self.complaint_tree.configure(yscrollcommand=yscroll.set)
        self.complaint_tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        self.complaint_tree.bind("<Double-1>", self.show_complaint_details)

        label(box, "Double-click a complaint to view details and update its status.",
              9, False, MUTED, CARD).pack(anchor="w", padx=18, pady=(0, 10))
        self.load_complaints()

    def load_complaints(self):
        if not hasattr(self, "complaint_tree"):
            return
        for item in self.complaint_tree.get_children():
            self.complaint_tree.delete(item)
        search = self.complaint_search.get().strip() if hasattr(self, "complaint_search") else ""
        rows = self.app.db.complaints(filters={"search": search})
        for r in rows:
            self.complaint_tree.insert("", "end", values=(
                r["complaint_id"], r["citizen_name"], r["title"], r["category"],
                r["priority"], r["recommended_department"], r["status"],
                str(r["created_at"])[:16]
            ))
        if hasattr(self, "complaint_count"):
            self.complaint_count.configure(text=f"All Complaints  •  {len(rows)} records")

    def show_complaint_details(self, event=None):
        selection = self.complaint_tree.selection()
        if not selection:
            return
        cid = self.complaint_tree.item(selection[0])["values"][0]
        row = self.app.db.get_complaint(cid)
        if not row:
            messagebox.showerror("Complaint Not Found", "The selected complaint no longer exists.")
            self.load_complaints()
            return

        w = tk.Toplevel(self.app.root)
        w.title(f"Complaint Details — {cid}")
        w.geometry("820x700")
        w.minsize(700, 600)
        w.configure(bg=BG)

        label(w, cid, 20, True, CYAN, BG).pack(anchor="w", padx=30, pady=(22, 3))
        label(w, "Complaint details and administrative status control", 9, False, MUTED, BG).pack(
            anchor="w", padx=30, pady=(0, 14)
        )

        box = card(w, True, CYAN)
        box.pack(fill="both", expand=True, padx=30, pady=5)
        details = (
            f"Citizen: {row['citizen_name']}\n"
            f"Email: {row['citizen_email']}\n"
            f"Phone: {row['citizen_phone']}\n\n"
            f"Title: {row['title']}\n"
            f"Location: {row['location']}\n"
            f"Category: {row['category']}  ({self._fmt_conf(row['category_confidence'])})\n"
            f"Priority: {row['priority']}  ({self._fmt_conf(row['priority_confidence'])})\n"
            f"Department: {row['recommended_department']}\n"
            f"Status: {row['status']}\n"
            f"Created: {row['created_at']}\n\n"
            f"Description:\n{row['description']}\n\n"
            f"AI Summary:\n{row['ai_summary']}"
        )
        text = tk.Text(box, wrap="word", font=("Segoe UI", 10), bg=CARD, fg=WHITE,
                       insertbackground=WHITE, relief="flat", bd=0, height=24)
        text.insert("1.0", details)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True, padx=20, pady=18)

        btn = tk.Frame(w, bg=BG)
        btn.pack(fill="x", padx=30, pady=15)
        label(btn, "Update status:", 9, True, MUTED, BG).pack(side="left", padx=(0, 8))
        for status in ("Assigned", "In Progress", "Resolved", "Reopened"):
            button(btn, status, lambda s=status: self.change_complaint_status(cid, s, w),
                   status == "Resolved", True).pack(side="left", padx=4)

    @staticmethod
    def _fmt_conf(value):
        if value is None:
            return "N/A"
        try:
            return f"{float(value):.2f}%"
        except (TypeError, ValueError):
            return str(value)

    def change_complaint_status(self, cid, status, window):
        try:
            changed = self.app.db.update_status(cid, status, self.app.session.get("name", "Administrator"))
            if not changed:
                messagebox.showerror("Update Failed", "Complaint could not be found.", parent=window)
                return
            messagebox.showinfo("Status Updated", f"Complaint {cid} is now {status}.", parent=window)
            window.destroy()
            self.load_complaints()
        except Exception as exc:
            messagebox.showerror("Update Failed", str(exc), parent=window)

    def show_analytics(self):
        area=self.shell("Analytics & Insights")
        label(area,"Advanced data analysis • workload • hotspots • resolution • trends",
              10,False,MUTED,BG).pack(anchor="w",padx=35,pady=(14,8))
        toolbar=tk.Frame(area,bg=BG); toolbar.pack(fill="x",padx=35,pady=(0,10))
        button(toolbar,"↻ Refresh Analytics",self.show_analytics,False,True).pack(side="right")

        try:
            from services.analytics import AnalyticsService
            data=AnalyticsService(self.app.db).analytics()
        except Exception as exc:
            box=card(area,True,RED); box.pack(fill="x",padx=35,pady=20)
            label(box,"ANALYTICS ERROR",12,True,RED,CARD).pack(anchor="w",padx=18,pady=(14,5))
            label(box,str(exc),10,False,WHITE,CARD,wraplength=1000).pack(anchor="w",padx=18,pady=(0,14))
            return

        s=data["stats"]
        kpi=tk.Frame(area,bg=BG); kpi.pack(fill="x",padx=35,pady=5)
        vals=[
            ("Resolution Rate",f"{s['resolved']/s['total']*100 if s['total'] else 0:.1f}%",GREEN),
            ("Critical Share",f"{s['critical']/s['total']*100 if s['total'] else 0:.1f}%",RED),
            ("Active Cases",str(s["open"]+s["assigned"]+s["in_progress"]),AMBER),
            ("Tracked Locations",str(len(data["locations"])),CYAN)]
        for n,v,c in vals:
            box=card(kpi,True,c); box.pack(side="left",fill="x",expand=True,padx=(0,8))
            label(box,n,8,True,MUTED,CARD).pack(anchor="w",padx=14,pady=(11,1))
            label(box,v,20,True,c,CARD).pack(anchor="w",padx=14,pady=(0,11))

        panels=tk.Frame(area,bg=BG); panels.pack(fill="both",expand=True,padx=35,pady=12)
        for col in range(3): panels.grid_columnconfigure(col,weight=1)
        panels.grid_rowconfigure(0,weight=1)
        self.analysis_panel(panels,0,"Department Workload",data["departments"],CYAN)
        self.analysis_panel(panels,1,"Hotspot Locations",data["locations"],PURPLE)
        self.resolution_panel(panels,2,"Resolution by Category",data["resolution"],GREEN)

        trend=card(area,True,BLUE); trend.pack(fill="x",padx=35,pady=(0,12))
        label(trend,"Complaint Trend — Recent Dates",12,True,WHITE,CARD).pack(anchor="w",padx=18,pady=(12,5))
        self.draw_trend(trend,data["days"])

        note=card(area,True,AMBER); note.pack(fill="x",padx=35,pady=(0,18))
        label(note,"ANALYTICS NOTE",8,True,AMBER,CARD).pack(anchor="w",padx=16,pady=(9,2))
        label(note,"This page is intentionally different from Overview: it analyzes workload, locations, resolution performance and time trends from SQLite.",
              9,False,WHITE,CARD).pack(anchor="w",padx=16,pady=(0,9))

    def analysis_panel(self,parent,col,title,rows,accent):
        box=card(parent,True,accent); box.grid(row=0,column=col,sticky="nsew",padx=5)
        label(box,title,11,True,WHITE,CARD).pack(anchor="w",padx=14,pady=(13,9))
        if not rows:
            label(box,"No data available",9,False,MUTED,CARD).pack(anchor="w",padx=14,pady=20); return
        maximum=max(int(r["count"]) for r in rows) or 1
        for r in rows:
            name=r["department"] if "department" in r.keys() else r["location"]
            count=int(r["count"])
            line=tk.Frame(box,bg=CARD); line.pack(fill="x",padx=14,pady=5)
            label(line,str(name),8,True,TEXT,CARD).pack(side="left")
            label(line,str(count),8,True,accent,CARD).pack(side="right")
            bar=tk.Frame(box,bg="#1B2A43",height=7); bar.pack(fill="x",padx=14,pady=(0,3))
            tk.Frame(bar,bg=accent,height=7).place(relwidth=count/maximum,relheight=1)

    def resolution_panel(self,parent,col,title,rows,accent):
        box=card(parent,True,accent); box.grid(row=0,column=col,sticky="nsew",padx=5)
        label(box,title,11,True,WHITE,CARD).pack(anchor="w",padx=14,pady=(13,9))
        if not rows:
            label(box,"No data available",9,False,MUTED,CARD).pack(anchor="w",padx=14,pady=20); return
        for r in rows:
            total=int(r["total"]); resolved=int(r["resolved"] or 0); rate=resolved/total*100 if total else 0
            line=tk.Frame(box,bg=CARD); line.pack(fill="x",padx=14,pady=5)
            label(line,str(r["category"]),8,True,TEXT,CARD).pack(side="left")
            label(line,f"{resolved}/{total} • {rate:.0f}%",8,True,accent,CARD).pack(side="right")

    def draw_trend(self,parent,rows):
        if not rows:
            label(parent,"No trend data available yet.",9,False,MUTED,CARD).pack(anchor="w",padx=18,pady=12); return
        maxv=max(int(r["count"]) for r in rows) or 1
        chart=tk.Frame(parent,bg=CARD,height=110); chart.pack(fill="x",padx=18,pady=(0,14))
        for r in rows[-10:]:
            col=tk.Frame(chart,bg=CARD,width=60); col.pack(side="left",fill="y",expand=True)
            label(col,str(r["count"]),8,True,BLUE,CARD).pack()
            tk.Frame(col,bg=BLUE,height=max(8,int(55*int(r["count"])/maxv)),width=20).pack()
            label(col,str(r["day"])[5:],7,False,MUTED,CARD).pack()


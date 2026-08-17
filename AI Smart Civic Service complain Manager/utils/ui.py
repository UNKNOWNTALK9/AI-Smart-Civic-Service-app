import tkinter as tk
from tkinter import ttk

FONT="Segoe UI"
BG="#070B14"
SURFACE="#0D1422"
SURFACE2="#111B2E"
CARD="#0F1726"
WHITE="#F8FAFC"
TEXT="#E5E7EB"
MUTED="#94A3B8"
CYAN="#22D3EE"
BLUE="#3B82F6"
PURPLE="#8B5CF6"
GREEN="#22C55E"
AMBER="#F59E0B"
RED="#EF4444"
BORDER="#24344D"

def setup_style(root):
    s=ttk.Style(root)
    try: s.theme_use("clam")
    except: pass
    s.configure("Treeview",font=(FONT,9),rowheight=40,background=CARD,
                fieldbackground=CARD,foreground=TEXT,borderwidth=0)
    s.configure("Treeview.Heading",font=(FONT,9,"bold"),padding=11,
                background=SURFACE2,foreground=WHITE)
    s.map("Treeview",background=[("selected","#173A5B")],
          foreground=[("selected",WHITE)])
    s.configure("TCombobox",padding=8,font=(FONT,10),fieldbackground=SURFACE2,
                background=SURFACE2,foreground=TEXT)

def clear(w):
    for x in w.winfo_children(): x.destroy()

def label(parent,text,size=10,bold=False,fg=TEXT,bg=BG,**kw):
    return tk.Label(parent,text=text,font=(FONT,size,"bold" if bold else "normal"),
                    fg=fg,bg=bg,**kw)

def button(parent,text,command,primary=True,compact=False):
    bg=BLUE if primary else SURFACE2
    fg=WHITE
    b=tk.Button(parent,text=text,command=command,font=(FONT,9 if compact else 10,"bold"),
                bd=0,cursor="hand2",padx=13 if compact else 17,pady=7 if compact else 10,
                bg=bg,fg=fg,activebackground="#2563EB",activeforeground=WHITE,
                relief="flat",highlightthickness=0)
    b.bind("<Enter>",lambda e: b.configure(bg="#22D3EE" if primary else "#1B2A43",fg="#06111B" if primary else WHITE))
    b.bind("<Leave>",lambda e: b.configure(bg=bg,fg=fg))
    return b

def card(parent, neon=False, accent=CYAN):
    f=tk.Frame(parent,bg=CARD,highlightbackground=accent if neon else BORDER,
               highlightthickness=1,bd=0)
    return f

def pill(parent,text,bg="#123449",fg=CYAN):
    return tk.Label(parent,text=text,font=(FONT,8,"bold"),bg=bg,fg=fg,padx=9,pady=4)

def neon_line(parent,height=2,color=CYAN):
    return tk.Frame(parent,bg=color,height=height)

def animate_pulse(widget, colors=(CYAN,BLUE,PURPLE), interval=420):
    state={"i":0}
    def tick():
        if not widget.winfo_exists(): return
        widget.configure(highlightbackground=colors[state["i"]%len(colors)])
        state["i"]+=1
        widget.after(interval,tick)
    tick()

def animate_glow(label_widget, base=CYAN, dim="#7C8EA5", interval=650):
    state={"on":True}
    def tick():
        if not label_widget.winfo_exists(): return
        state["on"]=not state["on"]
        label_widget.configure(fg=base if state["on"] else dim)
        label_widget.after(interval,tick)
    tick()

def fade_in(widget, steps=12, delay=25):
    # Tkinter cannot alpha-fade individual widgets reliably; this provides
    # a smooth reveal using incremental padding/size.
    if not widget.winfo_exists(): return
    widget.update_idletasks()
    if hasattr(widget,"pack_info") and widget.winfo_manager()=="pack":
        info=widget.pack_info()
        original=int(info.get("pady",0)) if str(info.get("pady","0")).isdigit() else 0
        widget.pack_configure(pady=(max(original-steps*2,0),original))
        def step(n=0):
            if not widget.winfo_exists(): return
            if n>=steps:
                widget.pack_configure(pady=original); return
            widget.pack_configure(pady=(max(original-(steps-n)*2,0),original))
            widget.after(delay,lambda:step(n+1))
        step()

def animated_title(parent,title,subtitle=None,size=26):
    box=tk.Frame(parent,bg=parent.cget("bg"))
    t=label(box,title,size,True,WHITE,parent.cget("bg"))
    t.pack(anchor="w")
    neon_line(box,2,CYAN).pack(fill="x",pady=(7,5))
    animate_glow(t)
    if subtitle:
        label(box,subtitle,10,False,MUTED,parent.cget("bg")).pack(anchor="w")
    return box

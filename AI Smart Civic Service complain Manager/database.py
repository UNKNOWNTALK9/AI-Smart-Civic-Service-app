import sqlite3
import secrets
from datetime import datetime, timedelta
from config import DB_PATH, DEPARTMENTS

class DatabaseManager:
    def __init__(self, path=DB_PATH):
        self.path = str(path)
        self.initialize()

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self):
        with self.connect() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL, phone TEXT, password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'citizen', created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS complaints(
                id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id TEXT UNIQUE NOT NULL,
                citizen_id INTEGER NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL,
                location TEXT, category TEXT, category_confidence REAL, priority TEXT,
                priority_confidence REAL, ai_summary TEXT, recommended_department TEXT,
                status TEXT NOT NULL DEFAULT 'Open', image_path TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL, resolved_at TEXT,
                FOREIGN KEY(citizen_id) REFERENCES users(id));
            CREATE TABLE IF NOT EXISTS ai_predictions(
                id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id TEXT, category TEXT,
                category_confidence REAL, priority TEXT, priority_confidence REAL,
                summary TEXT, model_name TEXT, model_version TEXT, created_at TEXT);
            CREATE TABLE IF NOT EXISTS departments(
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, description TEXT);
            CREATE TABLE IF NOT EXISTS complaint_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id TEXT, old_status TEXT,
                new_status TEXT, changed_by TEXT, note TEXT, created_at TEXT);
            """)
            for name in set(DEPARTMENTS.values()):
                c.execute("INSERT OR IGNORE INTO departments(name,description) VALUES(?,?)",
                          (name, "Civic service department responsible for related complaints."))
            from utils.security import hash_password
            admin = c.execute("SELECT id FROM users WHERE email=?", ("admin@civic.local",)).fetchone()
            if not admin:
                c.execute("INSERT INTO users(name,email,phone,password_hash,role,created_at) VALUES(?,?,?,?,?,?)",
                          ("System Administrator","admin@civic.local","0000000000",
                           hash_password("Admin@123"),"admin",datetime.now().isoformat(timespec="seconds")))

    def execute(self, sql, params=(), fetch=False, many=False):
        with self.connect() as c:
            cur = c.executemany(sql, params) if many else c.execute(sql, params)
            if fetch:
                return cur.fetchall()
            return cur.lastrowid

    def authenticate(self, email, password, role):
        from utils.security import verify_password
        row = self.execute("SELECT * FROM users WHERE email=? AND role=?", (email.strip().lower(), role), True)
        return row[0] if row and verify_password(password, row[0]["password_hash"]) else None

    def register(self, name, email, phone, password):
        from utils.security import hash_password
        try:
            return self.execute("INSERT INTO users(name,email,phone,password_hash,role,created_at) VALUES(?,?,?,?,?,?)",
                (name.strip(),email.strip().lower(),phone.strip(),hash_password(password),"citizen",
                 datetime.now().isoformat(timespec="seconds")))
        except sqlite3.IntegrityError:
            return None

    def create_complaint(self, citizen_id, title, description, location, analysis, image_path=""):
        now = datetime.now().isoformat(timespec="seconds")
        cid = f"CIV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}"
        rowid = self.execute("""INSERT INTO complaints
        (complaint_id,citizen_id,title,description,location,category,category_confidence,priority,
        priority_confidence,ai_summary,recommended_department,status,image_path,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (cid,citizen_id,title,description,location,analysis["category"],analysis["category_confidence"],
         analysis["priority"],analysis["priority_confidence"],analysis["summary"],analysis["department"],
         "Open",image_path,now,now))
        self.execute("""INSERT INTO ai_predictions
        (complaint_id,category,category_confidence,priority,priority_confidence,summary,model_name,model_version,created_at)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (cid,analysis["category"],analysis["category_confidence"],analysis["priority"],
         analysis["priority_confidence"],analysis["summary"],analysis.get("model_name",""),"1.0",now))
        return cid

    def complaints(self, citizen_id=None, filters=None):
        q = """SELECT c.*, u.name citizen_name FROM complaints c JOIN users u ON u.id=c.citizen_id WHERE 1=1"""
        p=[]
        if citizen_id is not None: q += " AND c.citizen_id=?"; p.append(citizen_id)
        filters = filters or {}
        for key, col in [("category","c.category"),("priority","c.priority"),("status","c.status"),("department","c.recommended_department")]:
            if filters.get(key) and filters[key] != "All":
                q += f" AND {col}=?"; p.append(filters[key])
        if filters.get("search"):
            q += " AND (c.complaint_id LIKE ? OR c.description LIKE ? OR c.location LIKE ?)"
            s=f"%{filters['search']}%"; p += [s,s,s]
        q += " ORDER BY c.id DESC"
        return self.execute(q, p, True)

    def get_complaint(self, cid):
        rows=self.execute("""SELECT c.*,u.name citizen_name,u.email citizen_email,u.phone citizen_phone
                             FROM complaints c JOIN users u ON u.id=c.citizen_id WHERE c.complaint_id=?""",(cid,),True)
        return rows[0] if rows else None

    def update_status(self, cid, new_status, changed_by, note=""):
        row=self.get_complaint(cid)
        if not row: return False
        now=datetime.now().isoformat(timespec="seconds")
        resolved=now if new_status=="Resolved" else row["resolved_at"]
        self.execute("UPDATE complaints SET status=?,updated_at=?,resolved_at=? WHERE complaint_id=?",
                     (new_status,now,resolved,cid))
        self.execute("""INSERT INTO complaint_history(complaint_id,old_status,new_status,changed_by,note,created_at)
                        VALUES(?,?,?,?,?,?)""",(cid,row["status"],new_status,changed_by,note,now))
        return True

    def stats(self):
        """Return dashboard counts using the same connection-safe execute() API."""
        total = self.execute("SELECT COUNT(*) AS n FROM complaints", fetch=True)[0]["n"]
        open_count = self.execute(
            "SELECT COUNT(*) AS n FROM complaints WHERE status='Open'", fetch=True
        )[0]["n"]
        assigned = self.execute(
            "SELECT COUNT(*) AS n FROM complaints WHERE status='Assigned'", fetch=True
        )[0]["n"]
        progress = self.execute(
            "SELECT COUNT(*) AS n FROM complaints WHERE status='In Progress'", fetch=True
        )[0]["n"]
        resolved = self.execute(
            "SELECT COUNT(*) AS n FROM complaints WHERE status='Resolved'", fetch=True
        )[0]["n"]
        critical = self.execute(
            "SELECT COUNT(*) AS n FROM complaints WHERE priority='Critical'", fetch=True
        )[0]["n"]
        return {
            "total": total,
            "open": open_count,
            "assigned": assigned,
            "in_progress": progress,
            "resolved": resolved,
            "critical": critical,
        }

    def complaint_counts_by_category(self):
        return self.execute(
            "SELECT COALESCE(category,'Uncategorized') AS category, COUNT(*) AS count "
            "FROM complaints GROUP BY category ORDER BY count DESC",
            fetch=True
        )

    def complaint_counts_by_priority(self):
        return self.execute(
            "SELECT COALESCE(priority,'Unknown') AS priority, COUNT(*) AS count "
            "FROM complaints GROUP BY priority "
            "ORDER BY CASE priority "
            "WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 "
            "WHEN 'Medium' THEN 3 WHEN 'Low' THEN 4 ELSE 5 END",
            fetch=True
        )

    def recent_complaints(self, limit=10):
        return self.execute(
            "SELECT complaint_id, title, category, priority, status, created_at "
            "FROM complaints ORDER BY id DESC LIMIT ?",
            (int(limit),), True
        )

    def complaints_by_department(self):
        return self.execute(
            "SELECT COALESCE(recommended_department,'Unassigned') AS department, COUNT(*) AS count "
            "FROM complaints GROUP BY recommended_department ORDER BY count DESC", fetch=True)

    def complaints_by_location(self):
        return self.execute(
            "SELECT COALESCE(location,'Unknown') AS location, COUNT(*) AS count "
            "FROM complaints GROUP BY location ORDER BY count DESC LIMIT 8", fetch=True)

    def complaints_by_day(self):
        return self.execute(
            "SELECT substr(created_at,1,10) AS day, COUNT(*) AS count "
            "FROM complaints GROUP BY day ORDER BY day ASC LIMIT 14", fetch=True)

    def resolution_by_category(self):
        return self.execute(
            "SELECT COALESCE(category,'Uncategorized') AS category, COUNT(*) AS total, "
            "SUM(CASE WHEN status='Resolved' THEN 1 ELSE 0 END) AS resolved "
            "FROM complaints GROUP BY category ORDER BY total DESC", fetch=True)

    def seed_demo_complaints(self, user_id=None):
        """Insert demo complaints using the real complaints schema."""
        existing = self.execute(
            "SELECT COUNT(*) AS n FROM complaints", fetch=True
        )[0]["n"]
        if existing:
            return 0

        # Admin accounts cannot own complaints; create a dedicated demo citizen.
        if user_id is None:
            row = self.execute(
                "SELECT id FROM users WHERE role='citizen' ORDER BY id LIMIT 1",
                fetch=True
            )
            if row:
                user_id = row[0]["id"]

        if user_id is None:
            from utils.security import hash_password
            try:
                user_id = self.execute(
                    """INSERT INTO users
                    (name,email,phone,password_hash,role,created_at)
                    VALUES(?,?,?,?,?,?)""",
                    ("Demo Citizen", "demo@civic.local", "03000000000",
                     hash_password("Demo@123"), "citizen",
                     datetime.now().isoformat(timespec="seconds"))
                )
            except sqlite3.IntegrityError:
                user_id = self.execute(
                    "SELECT id FROM users WHERE email=?",
                    ("demo@civic.local",), True
                )[0]["id"]

        samples = [
            ("Streetlight outage near school","Streetlight",
             "Several streetlights are not working near the school road.",
             "School Road","Low","Resolved"),
            ("Small road pothole","Road",
             "A small pothole has appeared on the side road.",
             "Block A","Low","Open"),
            ("Garbage collection delayed","Waste",
             "Garbage has not been collected for three days.",
             "Market Area","Medium","In Progress"),
            ("Blocked drainage","Drainage",
             "Drain is partially blocked with standing water.",
             "Central Street","Medium","Assigned"),
            ("Multiple broken streetlights","Streetlight",
             "Multiple streetlights are not working in the neighborhood.",
             "Residential Area","Medium","Open"),
            ("Damaged road lane","Road",
             "Road surface is damaged across one lane.",
             "Main Road","Medium","In Progress"),
            ("Major water pipe leak","Water",
             "A major water pipe is leaking continuously.",
             "Main Road","High","Assigned"),
            ("Severe road damage","Road",
             "The road has severe cracks and vehicles cannot pass easily.",
             "Main Road","High","In Progress"),
            ("Overflowing drainage","Drainage",
             "Drainage is overflowing onto the street.",
             "Market Area","High","Open"),
            ("Dangerous exposed wire","Electricity",
             "An exposed electrical wire is sparking near houses.",
             "Block A","Critical","Assigned"),
            ("Flooding several homes","Drainage",
             "Sewage is flooding several homes.",
             "Residential Area","Critical","In Progress"),
            ("Electrical fire risk","Electricity",
             "Damaged electrical equipment is creating a fire risk.",
             "School Road","Critical","Open"),
        ]

        now=datetime.now()
        inserted=0
        for i,(title,category,description,location,priority,status) in enumerate(samples,1):
            cid=f"CIV-DEMO-{i:03d}"
            created=(now-timedelta(hours=i*3)).isoformat(timespec="seconds")
            self.execute(
                """INSERT INTO complaints
                (complaint_id,citizen_id,title,description,location,category,
                 category_confidence,priority,priority_confidence,ai_summary,
                 recommended_department,status,image_path,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (cid,user_id,title,description,location,category,95.0,priority,92.0,
                 description,"Municipal Services",status,"",created,created)
            )
            inserted+=1
        return inserted

"""
Simple rule-based FAQ chatbot for the Citizen Control Center.

No external AI/API calls - it answers common questions about a citizen's
own complaints (counts, status, average resolution time, etc.) by reading
straight from the local database. Keeps things fast, offline and free.
"""
import re
from datetime import datetime
from config import DEPARTMENTS, CATEGORIES

GREETING_RE = re.compile(r"\b(hi|hello|hey|good morning|good evening|good afternoon)\b", re.I)
THANKS_RE = re.compile(r"\b(thanks|thank you|thx|ty)\b", re.I)
HELP_RE = re.compile(r"\b(help|what can you do|options|commands)\b", re.I)

TOTAL_RE = re.compile(r"\b(how many|total|count)\b.*\bcomplaints?\b", re.I)
OPEN_RE = re.compile(r"\b(open|pending|unresolved|waiting)\b", re.I)
INPROGRESS_RE = re.compile(r"\bin[\s-]?progress\b", re.I)
RESOLVED_RE = re.compile(r"\bresolved|closed|completed|done\b", re.I)
CRITICAL_RE = re.compile(r"\bcritical|urgent|priority\b", re.I)

TIME_RE = re.compile(
    r"\b(how (long|much time)|time (does it|it) take|resolution time|resolve.*take|average.*(time|days)|"
    r"turnaround|eta|when will .*(resolve|fix))\b", re.I)

STATUS_ID_RE = re.compile(r"\bCIV-[0-9A-Z-]+\b", re.I)
STATUS_WORD_RE = re.compile(r"\bstatus\b", re.I)

DEPT_RE = re.compile(r"\bdepartment|which department|who handles\b", re.I)
CATEGORY_RE = re.compile(r"\bcategor(y|ies)|types? of complaints?\b", re.I)


def _avg_resolution_days(rows):
    """Average days between created_at and resolved_at for resolved rows."""
    diffs = []
    for r in rows:
        if r["status"] == "Resolved" and r["resolved_at"]:
            try:
                created = datetime.fromisoformat(r["created_at"])
                resolved = datetime.fromisoformat(r["resolved_at"])
                diffs.append((resolved - created).total_seconds() / 86400)
            except Exception:
                continue
    if not diffs:
        return None
    return sum(diffs) / len(diffs)


class ComplaintChatbot:
    """Answers a citizen's questions about their own complaints."""

    WELCOME = (
        "Hi! I'm your Civic Assistant. Ask me things like:\n"
        "• \"How many complaints do I have?\"\n"
        "• \"How long does it take to resolve a complaint?\"\n"
        "• \"What's the status of CIV-2024...\"\n"
        "• \"How many are still open?\"\n"
        "• \"Which department handles Water issues?\""
    )

    def __init__(self, db):
        self.db = db

    def reply(self, citizen_id, message):
        text = (message or "").strip()
        if not text:
            return "Please type a question - for example, \"how many complaints do I have?\""

        rows = self.db.complaints(citizen_id)

        # Specific complaint lookup (by ID) takes priority
        id_match = STATUS_ID_RE.search(text)
        if id_match:
            return self._complaint_status(id_match.group(0))

        if GREETING_RE.search(text):
            return "Hello! How can I help with your complaints today?"

        if THANKS_RE.search(text):
            return "You're welcome! Anything else I can help with?"

        if HELP_RE.search(text):
            return self.WELCOME

        if TIME_RE.search(text):
            return self._resolution_time(rows)

        if STATUS_WORD_RE.search(text) and not id_match:
            return ("Sure - which complaint? Share its ID (e.g. CIV-20240101120000-AB12), "
                    "or check the \"My Complaints\" tab for the full list.")

        if RESOLVED_RE.search(text):
            n = sum(r["status"] == "Resolved" for r in rows)
            return f"You have {n} resolved complaint(s) out of {len(rows)} total."

        if INPROGRESS_RE.search(text):
            n = sum(r["status"] == "In Progress" for r in rows)
            return f"You have {n} complaint(s) currently In Progress."

        if OPEN_RE.search(text):
            n = sum(r["status"] == "Open" for r in rows)
            return f"You have {n} open (pending) complaint(s)."

        if CRITICAL_RE.search(text):
            n = sum(r["priority"] == "Critical" for r in rows)
            return f"You have {n} complaint(s) marked Critical priority."

        if DEPT_RE.search(text):
            return self._department_info(text)

        if CATEGORY_RE.search(text):
            return "Complaints are grouped into: " + ", ".join(CATEGORIES) + "."

        if TOTAL_RE.search(text):
            return self._total_summary(rows)

        # Fallback: try to be a little helpful using overall stats anyway
        if rows:
            return (f"I'm not sure I understood that. You currently have {len(rows)} complaint(s) "
                     "on file. Try asking about status, open/resolved counts, or resolution time - "
                     "or type \"help\" to see examples.")
        return ("I'm not sure I understood that. Type \"help\" to see example questions "
                "you can ask me.")

    def _total_summary(self, rows):
        if not rows:
            return "You haven't submitted any complaints yet."
        open_n = sum(r["status"] == "Open" for r in rows)
        prog_n = sum(r["status"] == "In Progress" for r in rows)
        res_n = sum(r["status"] == "Resolved" for r in rows)
        return (f"You have {len(rows)} complaint(s) total - "
                f"{open_n} Open, {prog_n} In Progress, {res_n} Resolved.")

    def _resolution_time(self, rows):
        avg = _avg_resolution_days(rows)
        if avg is None:
            # Fall back to a system-wide average across all complaints
            all_rows = self.db.complaints()
            avg = _avg_resolution_days(all_rows)
            if avg is None:
                return ("I don't have enough resolved complaints yet to calculate an average "
                        "resolution time. Once complaints are marked Resolved, I can tell you.")
            return (f"None of your complaints are resolved yet, but on average across all "
                    f"citizens it takes about {avg:.1f} day(s) to resolve a complaint.")
        return f"On average, your complaints have taken about {avg:.1f} day(s) to resolve."

    def _complaint_status(self, cid):
        row = self.db.get_complaint(cid.upper())
        if not row:
            return f"I couldn't find a complaint with ID {cid.upper()}. Please double check the ID."
        extra = ""
        if row["status"] == "Resolved" and row["resolved_at"]:
            try:
                created = datetime.fromisoformat(row["created_at"])
                resolved = datetime.fromisoformat(row["resolved_at"])
                days = (resolved - created).total_seconds() / 86400
                extra = f" It took {days:.1f} day(s) to resolve."
            except Exception:
                pass
        return (f"Complaint {row['complaint_id']} ({row['category']}, {row['priority']} priority) "
                f"is currently \"{row['status']}\".{extra}")

    def _department_info(self, text):
        for cat in CATEGORIES:
            if cat.lower() in text.lower():
                dept = DEPARTMENTS.get(cat, "Municipal Services")
                return f"{cat} complaints are handled by the {dept}."
        return ("Departments by category: " +
                ", ".join(f"{c} → {DEPARTMENTS.get(c, 'Municipal Services')}" for c in CATEGORIES))

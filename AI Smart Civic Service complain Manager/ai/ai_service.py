import json,joblib,re
from config import MODELS_DIR,DEPARTMENTS
from ai.summary import summarize
from ai.train_models import train_all
SEVERITY_RULES=[
(r"\b(exposed wire|sparking|electrocution|fire risk|life threatening|immediate danger)\b","Critical",98),
(r"\b(sewage flooding|flooding several homes|major flooding|trapping residents)\b","Critical",96),
(r"\b(major|severe|completely blocked|blocking most|cannot pass|continuous leak|overflowing)\b","High",88),
(r"\b(several|multiple|three days|poor|difficult|damaged across|standing water)\b","Medium",76),
(r"\b(small|minor|one lamp|slightly|delayed by one day|cosmetic)\b","Low",82)]
class AIService:
    def __init__(self):self.load()
    def load(self):
        try:
            self.classifier=joblib.load(MODELS_DIR/"complaint_classifier.pkl")
            self.priority=joblib.load(MODELS_DIR/"priority_model.pkl")
            self.meta=json.loads((MODELS_DIR/"metrics.json").read_text())
        except Exception:
            self.meta=train_all()
            self.classifier=joblib.load(MODELS_DIR/"complaint_classifier.pkl")
            self.priority=joblib.load(MODELS_DIR/"priority_model.pkl")
    def analyze(self,text):
        category=str(self.classifier.predict([text])[0])
        try:cconf=float(max(self.classifier.predict_proba([text])[0])*100)
        except:cconf=None
        ptext=f"{text} category_{category.lower()}"
        ml_priority=str(self.priority.predict([ptext])[0])
        try:ml_conf=float(max(self.priority.predict_proba([ptext])[0])*100)
        except:ml_conf=None
        chosen=None
        for pattern,priority,confidence in SEVERITY_RULES:
            if re.search(pattern,text.lower()):chosen=(priority,confidence);break
        priority,pconf=chosen if chosen else (ml_priority,ml_conf)
        return {"category":category,"category_confidence":cconf,"priority":priority,
                "priority_confidence":pconf,"summary":summarize(text),
                "department":DEPARTMENTS.get(category,"Municipal Services"),
                "model_name":self.meta.get("best_model","Classification Model"),
                "priority_source":"Severity rules" if chosen else "ML priority model"}

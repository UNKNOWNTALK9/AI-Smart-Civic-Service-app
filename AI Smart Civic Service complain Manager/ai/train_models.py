import json, joblib, pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from config import DATASET_PATH, MODELS_DIR
from ai.preprocessing import load_dataset

def metrics(y, pred):
    p,r,f,_=precision_recall_fscore_support(y,pred,average="weighted",zero_division=0)
    return {"accuracy":accuracy_score(y,pred),"precision":p,"recall":r,"f1":f,
            "confusion_matrix":confusion_matrix(y,pred).tolist(),
            "report":classification_report(y,pred,zero_division=0)}

def train_all():
    MODELS_DIR.mkdir(exist_ok=True)
    df,stats=load_dataset(DATASET_PATH)
    Xtr,Xte,ytr,yte=train_test_split(df.complaint_text,df.category,test_size=.2,random_state=42,stratify=df.category)
    candidates={
      "Logistic Regression":LogisticRegression(max_iter=1200),
      "Naive Bayes":MultinomialNB()
    }
    results={}
    best=None
    for name,clf in candidates.items():
        pipe=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2),min_df=1)),("model",clf)])
        pipe.fit(Xtr,ytr); pred=pipe.predict(Xte); m=metrics(yte,pred); results[name]=m
        if best is None or m["f1"]>best[1]["f1"]: best=(name,m,pipe)
    joblib.dump(best[2],MODELS_DIR/"complaint_classifier.pkl")
    # Priority model uses text + predicted category as input.
    df["priority_text"]=df.complaint_text+" category_"+df.category.str.lower()
    ptr,pte,pyr,pye=train_test_split(df.priority_text,df.priority,test_size=.2,random_state=42,stratify=df.priority)
    priority=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2))),("model",LogisticRegression(max_iter=1200))])
    priority.fit(ptr,pyr); pp=priority.predict(pte)
    pm=metrics(pye,pp)
    joblib.dump(priority,MODELS_DIR/"priority_model.pkl")
    meta={"dataset":stats,"classification_models":results,"best_model":best[0],
          "classification_test_samples":len(yte),"priority_test_samples":len(pye),
          "priority_metrics":pm,"training_date":pd.Timestamp.now().isoformat(),
          "feature_count":len(best[2].named_steps["tfidf"].vocabulary_)}
    (MODELS_DIR/"metrics.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    return meta

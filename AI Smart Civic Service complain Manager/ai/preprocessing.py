import re, pandas as pd
from sklearn.model_selection import train_test_split

def clean_text(text):
    text = "" if pd.isna(text) else str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def load_dataset(path):
    df=pd.read_csv(path)
    required={"complaint_text","category","priority"}
    missing=required-set(df.columns)
    if missing: raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    before=len(df)
    df=df.dropna(subset=["complaint_text","category","priority"]).copy()
    missing_removed=before-len(df)
    df["complaint_text"]=df["complaint_text"].map(clean_text)
    df=df[df["complaint_text"].str.len()>2].drop_duplicates(subset=["complaint_text"])
    return df, {"original":before,"missing_removed":missing_removed,"duplicates_removed":before-missing_removed-len(df),"final":len(df)}

def split(df):
    return train_test_split(df["complaint_text"], df["category"], test_size=.2, random_state=42, stratify=df["category"])

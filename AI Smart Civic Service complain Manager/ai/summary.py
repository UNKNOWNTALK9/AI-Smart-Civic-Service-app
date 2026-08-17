import re
def summarize(text):
    text = re.sub(r"\s+", " ", text.strip())
    if not text: return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    s=sentences[0]
    words=s.split()
    if len(words)>18: s=" ".join(words[:18])+"..."
    return s[0].upper()+s[1:] if s else s

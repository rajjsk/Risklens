import spacy
from spacy.matcher import Matcher

# Load spacy English model
nlp = spacy.load("en_core_web_sm")

# Matcher for notice periods
matcher = Matcher(nlp.vocab)
matcher.add("NOTICE_PERIOD", [[{"LIKE_NUM": True}, {"LOWER": {"IN": ["day","days","month","months","year","years"]}}]])

def extract_fields(text: str):
    """
    Extracts fields like dates, money, notice periods from text
    """
    doc = nlp(text)
    dates = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
    money = [ent.text for ent in doc.ents if ent.label_ == 'MONEY']
    
    matches = matcher(doc)
    notice_periods = []
    for mid, start, end in matches:
        notice_periods.append(doc[start:end].text)
    
    return {
        'dates': dates,
        'money': money,
        'notice_periods': notice_periods
    }

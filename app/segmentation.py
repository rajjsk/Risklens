import re

def naive_clause_split(text: str):
    """
    Split text into clauses based on headings or numbered lists.
    Returns list of tuples: (title, body)
    """
    # Try splitting by heading-like patterns
    chunks = re.split(r"\n\s*(\d+\.|[A-Z][A-Za-z\s]{1,40}:)\s+", text)
    
    if len(chunks) <= 1:
        # fallback: split by double newline
        return [(None, p.strip()) for p in text.split('\n\n') if p.strip()]
    
    pairs = []
    paras = re.split(r"\n\n+", text)
    
    for p in paras:
        header_search = re.match(r"^(?P<h>\d+\.|[A-Z][^\n]{1,80}:)\s*(?P<body>.*)$", p, re.DOTALL)
        if header_search:
            h = header_search.group('h').strip()
            b = header_search.group('body').strip()
            pairs.append((h, b))
        else:
            pairs.append((None, p.strip()))
    
    return pairs

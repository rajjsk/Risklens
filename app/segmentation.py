import re
from typing import List, Dict, Optional, Tuple

### Normalise text before using it 

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()



#### Extract Entity


def extract_entity(block: str) -> Optional[Dict[str, Optional[str]]]:
    """
    Extract a single entity from a block.
    Returns dict with name, pan, address.
    """
    if not block or not block.strip():
        return None

    block = block.strip()

    # -------- Name --------
    name_match = re.search(r'Name\s*:\s*([^,]+)', block)
    name = name_match.group(1).strip() if name_match else None
    if not name:
        return None

    # -------- PAN --------
    pan_match = re.search(r'\bPAN\s*:\s*([A-Z]{5}[0-9]{4}[A-Z])', block)
    pan = pan_match.group(1) if pan_match else None

    # -------- Address (semantic & flexible, exclude 'at:') --------
    address_match = re.search(
        r'''
        (?:residing|resident|address|situated|located|having)      # keywords
        \s*(?:at\s*:)?                                             # optional "at:" after keyword
        \s*
        (?P<addr>.*?)
        (?=                                                       # lookahead
            \bPAN\b|
            \bAge\b|
            \bHEREINAFTER\b|
            \bName\b|
            $)
        ''',
        block,
        re.IGNORECASE | re.DOTALL | re.VERBOSE
    )

    address = (
        address_match.group("addr")
        .replace('\n', ' ')
        .strip()
        if address_match else None
    )

    return {"name": name, "pan": pan, "address": address}

### function to detect role blocks  

def detect_role_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Detects role blocks in the text.
    Returns a list of tuples: (role_name, block_text)
    Works for Licensor, Licensee(s), Owner, Tenant(s), etc., robustly.
    """

    # Expanded role keywords
    role_keywords = [
        "Licensor", "Licensee", "Licensees",
        "Owner", "Tenant", "Tenants",
        "Lender", "Borrower",
        "Guarantor", "Co-Applicant",
        "Supplier", "Buyer",
        "Party", "Parties",
        "Seller", "Purchaser"
    ]

    # Create regex pattern dynamically
    role_pattern = r'(?P<role>' + '|'.join(role_keywords) + r')\s*:'

    # Find all role headers
    matches = list(re.finditer(role_pattern, text, flags=re.IGNORECASE))

    
    role_blocks = []

    for i, match in enumerate(matches):
        role = match.group("role").strip()
        start = match.end()

        # End is the start of next role match, or end of text
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip()

        # Only add if block has content
        if block:
            role_blocks.append((role, block))

    return role_blocks



### Extract Parties by Role 

def extract_parties_by_role(text: str) -> Tuple[List[Dict[str, Optional[str]]], List[Dict[str, Optional[str]]]]:
    """
    Extract parties from text and separate by roles.
    Returns two lists: (party_1_list, party_2_list)
    """

    # FIXED role detection regex

    role_blocks = detect_role_blocks(text)

    print(f"______________no of role blocks ------------- {len(role_blocks)}")  # debug

    print(f"______________-role blocks ------------- {role_blocks}")  # debug

    party_1 = []  # Typically first role (e.g., Licensor)
    party_2 = []  # Typically second role (e.g., Licensee)

    for i, (role, block) in enumerate(role_blocks):
        role_normalized = role.strip().lower()

        # Split multiple entities: look for "Name:" occurrences
        entity_blocks = re.split(r'\n?\d*\)\s*Name\s*:', block)
        for eb in entity_blocks:
            eb = eb.strip()
            if not eb:
                continue
            # Prepend "Name:" to match extraction pattern
            if not eb.lower().startswith("name:"):
                eb = "Name: " + eb
            entity = extract_entity(eb)
            if entity:
                entity["Role"] = role_normalized
                # Assign to party_1 or party_2 based on order
                if i == 0:
                    party_1.append(entity)
                elif i == 1:
                    party_2.append(entity)

    return party_1, party_2



### Extract Cluases from the agreement 


def extract_clauses(text: str):
    """
    Robust extraction of operative agreement clauses.
    """

    # -------- Layer 1: Legal transition phrases --------
    transition_match = re.search(
        r'''
        (
            NOW\s+(?:THEREFORE|THIS)\b.*?
            (?:AGREED|WITNESSETH|DECLARED).*?
            (?:FOLLOWS|UNDER)
          |
            THE\s+PARTIES\b.*?
            (?:AGREE|AGREED).*?
            (?:FOLLOWS|UNDER)
          |
            TERMS\s+AND\s+CONDITIONS\b.*?
            (?:FOLLOWS|UNDER)
        )
        \s*:?
        ''',
        text,
        re.IGNORECASE | re.DOTALL | re.VERBOSE
    )

    if transition_match:
        clauses_text = text[transition_match.end():]
    else:
        # -------- Layer 2: First numbered clause --------
        first_clause = re.search(
            r'(?m)^\s*\d+(?:\.\d+)*[\.\)]\s*[A-Z]',
            text
        )

        if not first_clause:
            return []

        clauses_text = text[first_clause.start():]

    # -------- Stop before schedules / annexures --------
    clauses_text = re.split(
        r'\n\s*(SCHEDULE|ANNEXURE|EXHIBIT)\b',
        clauses_text,
        flags=re.IGNORECASE
    )[0]

    # -------- Clause extraction --------
    clause_pattern = re.compile(
        r'''
        (?m)
        ^\s*
        (?P<num>\d+(?:\.\d+)*)
        [\.\)]
        \s*
        (?P<title>[A-Z][A-Za-z\s&]{2,80})
        :?\s*
        (?P<body>.*?)
        (?=^\s*\d+(?:\.\d+)*[\.\)]\s*[A-Z]|\Z)
        ''',
        re.DOTALL | re.VERBOSE
    )

    clauses = []

    for m in clause_pattern.finditer(clauses_text):
        clauses.append({
            "clause_no": m.group("num"),
            "title": m.group("title").strip(),
            "text": m.group("body").strip()
        })

    return clauses


### parse contract : wrapped into one function


def parse_contract(text: str):
    """
    Returns:
    party_1, party_2, clauses
    """

    text = normalize_text(text)

    #print(f"normalised text is : \n {text}")

    if not text:
        return None, None, []

    party_1, party_2 = extract_parties_by_role(text)
    clauses = extract_clauses(text)

    return party_1, party_2, clauses



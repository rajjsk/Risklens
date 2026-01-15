import re

# =====================================================
# 1. Normalize Text
# =====================================================
def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()


# =====================================================
# 2. Extract Entity (Name, PAN, Address) — ROBUST
# =====================================================
def extract_entity(block: str):
    if not block or not block.strip():
        return None

    # Remove standalone role headings (e.g., "Licensor:", "Buyer :")
    block = re.sub(
        r'(?m)^\s*[A-Z][A-Za-z\s]+?\s*:\s*$',
        '',
        block
    )

    # -------- Name (strict extraction) --------
    name_match = re.search(
        r'\bName\s*:\s*([A-Z][A-Za-z.\s]+)',
        block
    )

    name = name_match.group(1).strip() if name_match else None

    # ❌ Reject role words or colon-ended noise
    if name:
        lowered = name.lower().strip()
        if (
            lowered in {
                "licensor", "licensee", "licensees",
                "lessor", "lessee",
                "owner", "tenant",
                "seller", "buyer",
                "party", "parties"
            }
            or name.endswith(":")
            or name.endswith(" :")
        ):
            name = None

    # -------- PAN --------
    pan_match = re.search(
        r'\bPAN\s*:\s*([A-Z]{5}[0-9]{4}[A-Z])',
        block
    )
    pan = pan_match.group(1) if pan_match else None

    # -------- Address (semantic & flexible) --------
    address_match = re.search(
        r'''
        (?:residing|resident|address|situated|located|having)
        .*?
        (?P<addr>
            .*?
        )
        (?=
            \bPAN\b|
            \bAge\b|
            \bHEREINAFTER\b|
            \bName\b|
            $
        )
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

    # -------- FINAL VALIDATION --------
    if not name:
        return None

    if not pan and not address:
        # Reject pure noise like "Licensees:" or "Owner :"
        return None

    return {
        "name": name,
        "pan": pan,
        "address": address
    }



# =====================================================
# 3. Extract Parties (Role-Agnostic)
# =====================================================
def extract_parties(text: str):
    """
    Returns:
    party_1, party_2
    Each party is a list of entities or None
    """

    # Only parse before WHEREAS / NOW THEREFORE
    preamble = re.split(
        r'\n\s*WHEREAS\b|\n\s*NOW THEREFORE\b',
        text,
        flags=re.IGNORECASE
    )[0]

    # Find numbered party blocks
    party_blocks = re.findall(
        r'(?m)^\s*\d+\)\s*(.*?)(?=^\s*\d+\)\s*|\Z)',
        preamble,
        re.DOTALL
    )

    print(f"Party Blocks : {party_blocks}")

    parties = []

    for block in party_blocks:
        entities = []

        # Split multiple persons under same party
        persons = re.split(
            r'(?m)^\s*\d+\)\s*Name\s*:',
            block
        )
        #print(persons)

        for p in persons:
            p = p.strip()
            #print(f"person identified : {p}")
            if not p:
                continue

            entity = extract_entity("Name: " + p)
            #print(f"entity extracted : {entity}")
            if entity:
                entities.append(entity)

        # Only accept real parties
        if entities:
            parties.append(entities)

    print(parties)

    party_1 = parties[0] if len(parties) > 0 else None
    party_2 = parties[1] if len(parties) > 1 else None

    return party_1, party_2


# =====================================================
# 4. Extract Agreement Clauses
# =====================================================
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

# =====================================================
# 5. Wrapper Function (Single Entry Point)
# =====================================================
def parse_contract(text: str):
    """
    Returns:
    party_1, party_2, agreement_clauses
    """

    text = normalize_text(text)

    if not text:
        return None, None, []

    party_1, party_2 = extract_parties(text)
    agreement_clauses = extract_clauses(text)

    return party_1, party_2, agreement_clauses

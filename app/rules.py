RISK_RULES = [
    {'id':'missing_governing_law','description':'Governing Law / dispute resolution clause missing','weight':15,'condition': lambda clause: clause['label'] != 'Governing Law'},
    {'id':'missing_termination','description':'Termination clause missing','weight':15,'condition': lambda clause: clause['label'] != 'Termination'},
    {'id':'missing_confidentiality','description':'Confidentiality clause missing','weight':10,'condition': lambda clause: clause['label'] != 'Confidentiality'},
    {'id':'missing_liability','description':'Liability clause missing','weight':10,'condition': lambda clause: clause['label'] != 'Liability'},
    {'id':'missing_indemnity','description':'Indemnity clause missing','weight':10,'condition': lambda clause: clause['label'] != 'Indemnity'},
    {'id':'missing_ip','description':'Intellectual Property clause missing','weight':10,'condition': lambda clause: clause['label'] != 'Intellectual Property'},
    {'id':'missing_warranties','description':'Warranties clause missing','weight':10,'condition': lambda clause: clause['label'] != 'Warranties'},
    {'id':'missing_force_majeure','description':'Force Majeure clause missing','weight':10,'condition': lambda clause: clause['label'] != 'Force Majeure'}
]

def score_contract(clause_objs):
    """
    Calculates realistic contract risk score based on missing clauses
    """
    total_weight = sum(r['weight'] for r in RISK_RULES)
    risk_score = 0
    for r in RISK_RULES:
        expected_label = r['id'].split('_')[1].replace('ip','Intellectual Property').capitalize()
        if not any(clause['label'] == expected_label for clause in clause_objs):
            risk_score += r['weight']
    return int((risk_score / total_weight) * 100) if total_weight else 0

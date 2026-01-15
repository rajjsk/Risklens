import pandas as pd

def score_clause_risk_general(clause: dict) -> dict:
    """
    Returns only:
    - score: int (1–10)
    - reasons: list[str]
    """

    text = clause["text"].lower()
    label = clause.get("predicted_label", "").strip()

    base_risk = {
        "Period": 2,
        "Notice Period": 3,
        "Payment": 2,
        "Termination": 5,
        "Confidentiality": 3,
        "Liability": 6,
        "Indemnity": 7,
        "Intellectual Property": 5,
        "Governing Law": 2,
        "Warranties": 4,
        "Force Majeure": 3,
        "Maintenance": 1,
        "Use of Premises": 1,
        "Alteration": 2,
        "Inspection": 2,
        "Registration": 1
    }

    score = base_risk.get(label, 3)
    reasons = []

    # --- Risk escalators (only real hazards) ---

    if any(k in text for k in [
        "sole discretion", "absolute discretion",
        "without consent", "as deemed fit"
    ]):
        score += 2
        reasons.append("Unilateral discretion granted to one party.")

    if label == "Termination":
        if "without notice" in text:
            score += 3
            reasons.append("Termination without notice.")
        elif "immediate" in text:
            score += 2
            reasons.append("Immediate termination clause.")

    if any(k in text for k in ["penalty", "forfeit", "forfeiture"]):
        score += 2
        reasons.append("Financial penalty or forfeiture involved.")

    if label in ["Liability", "Indemnity"] and any(
        k in text for k in ["any and all", "unlimited", "whatsoever"]
    ):
        score += 2
        reasons.append("Unlimited liability or indemnity exposure.")

    if label == "Intellectual Property" and any(
        k in text for k in ["exclusive", "perpetual", "irrevocable"]
    ):
        score += 2
        reasons.append("Strong or permanent IP rights transfer.")

    if any(k in text for k in ["at any time", "from time to time"]):
        score += 1
        reasons.append("Open-ended or discretionary timing.")

    score = min(max(score, 1), 10)

    return {
        "score": score,
        "reasons": reasons or ["Standard clause with no material risk."]
    }




def clauses_to_table(clauses: list) -> pd.DataFrame:
    """
    Converts extracted clause data into a structured table.

    Returns columns:
    - clause_no
    - title
    - predicted_label
    - risk_score
    """
    rows = []
    for clause in clauses:
        rows.append({
            "clause_no": clause.get("clause_no"),
            "title": clause.get("title"),
            "predicted_label": clause.get("predicted_label"),
            "risk_score": clause.get("risk_score")
        })

    return pd.DataFrame(rows)

def interpret_contract_risk(score: float) -> str:
    if score <= 3:
        return "Low Risk"
    elif score <= 6:
        return "Medium Risk"
    else:
        return "High Risk"
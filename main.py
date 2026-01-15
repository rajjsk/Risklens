import argparse
from pathlib import Path
from app.pdf_utils import extract_text_pages, render_page_to_image, annotate_pdf
from app.ocr_utils import image_ocr
from app.segmentation import *
from app.classify import ZeroShotClassifier
from app.extractor import extract_fields
from app.rules import score_clause_risk_general,clauses_to_table,interpret_contract_risk
from app.report import save_report
import pandas as pd





def process_contract_score(pdf_path: str):
    """
    lang must be:
    - 'eng' for English
    - 'mar' for Marathi

    OCR runs in ONE language per document.
    Marathi OCR automatically falls back to English if it fails.
    """
    print("____process initiated____")

    pages = extract_text_pages(pdf_path)
    print("___pages extracted___")
    print(f"No of Pages : {len(pages)}")

    full_text = "\n\n".join(pages)
    party_1, party_2, agreement_clauses = parse_contract(full_text)

    party_1_df=pd.DataFrame(party_1)
    party_2_df=pd.DataFrame(party_2)

    print(f"First Party : {pd.DataFrame(party_1)}")
    print(f"Second Party : {pd.DataFrame(party_2)}")
    # print(f"clauses: {agreement_clauses}")

    # --- Zero-Shot Classification ---
    print("importing classifier")
    classifier=ZeroShotClassifier()
    clause_texts = [clause['text']+": "+clause['text'] for clause in agreement_clauses]
    classified_results = classifier.predict(clause_texts, top_k=2, threshold=0.1)

    print(f"✅ Classified Results: \n{classified_results}")


    # Combine results with clauses
    for clause, res in zip(agreement_clauses, classified_results):
         clause['predicted_label'] = res['top_label']
         clause_res=score_clause_risk_general(clause)
         clause['risk_score']=clause_res['score']
         clause['reason_for_risk']=clause_res['reasons']
         

    clauses_table=clauses_to_table(agreement_clauses)
    final_risk_score = round(clauses_table['risk_score'].mean(), 2)
    risk_level = interpret_contract_risk(final_risk_score)
    risky_clause_table = clauses_table[clauses_table['risk_score'] >= 5]

    print(f"✅ Clause Table : \n{clauses_table}")
    print(f"✅ Final Risk Score : \n{final_risk_score}")
    print(f"✅ Risk Category  : \n{risk_level}")
    
    return party_1_df,party_2_df,final_risk_score,risk_level,risky_clause_table





if __name__=="__main__":
        #pdf_path=r"C:\Users\Raj\Downloads\Dummy_Contract_No_Clause_Type.pdf"
        pdf_path=r"Leave_and_License_Agreement_Dummy_Revised.pdf"

        process_contract_score(pdf_path)
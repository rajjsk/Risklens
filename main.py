import argparse
from pathlib import Path
from app.pdf_utils import extract_text_pages, render_page_to_image, annotate_pdf
from app.ocr_utils import image_ocr
from app.segmentation import naive_clause_split
from app.classify import ZeroShotClassifier
from app.extractor import extract_fields
from app.rules import score_contract
from app.report import save_report


# Color mapping based on risk score
def risk_color(score: int):
    """
    Returns RGB color tuple based on risk score
    Green = low risk, Red = high risk
    """
    if score <= 25:
        return (0, 1, 0)         # Green
    elif score <= 50:
        return (1, 1, 0)         # Yellow
    elif score <= 75:
        return (1, 0.65, 0)      # Orange
    else:
        return (1, 0, 0)         # Red


def process(pdf_path: str, out_dir: str, lang: str = "eng"):
    """
    lang must be:
    - 'eng' for English
    - 'mar' for Marathi

    OCR runs in ONE language per document.
    Marathi OCR automatically falls back to English if it fails.
    """
    print("____process initiated____")

    pages = extract_text_pages(pdf_path)

    print("pages extracted")

    # OCR fallback for empty pages
    for i, t in enumerate(pages):
        if not t or not t.strip():
            img = render_page_to_image(pdf_path, i)
            pages[i] = image_ocr(img, lang=lang)

    full_text = "\n\n".join(pages)

    
    clauses = naive_clause_split(full_text)

    print(f"clauses: {clauses}")
    classifier = ZeroShotClassifier()

    clause_objs = []
    highlights = []

    # Process each clause
    for idx, (title, body) in enumerate(clauses):
        text_for_clf = (title or "") + "\n" + (body or "")
        label_out = classifier.predict(text_for_clf)

        label = label_out["labels"][0]
        score = label_out["scores"][0]
        fields = extract_fields(body or "")

        clause_objs.append({
            "title": title,
            "body": body,
            "label": label,
            "label_score": float(score),
            "fields": fields
        })

        clause_height = 20 + (body.count("\n") * 15)
        color = risk_color(int(score * 100))

        highlights.append({
            "page": 0,
            "bbox": (50, 50 + idx * 40, 500, 50 + idx * 40 + clause_height),
            "color": color
        })

    contract_risk = score_contract(clause_objs)
    print(contract_risk)

    report = {
        "contract_risk_score": contract_risk,
        "clauses": clause_objs
    }

    
    basename = Path(pdf_path).stem
    save_report(report, out_dir, basename)

    out_pdf = Path(out_dir) / f"annotated_{basename}.pdf"
    annotate_pdf(pdf_path, highlights, str(out_pdf))

    print("Done. Report + annotated PDF saved to", out_dir)
    print("Contract Risk Score:", contract_risk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input PDF")
    parser.add_argument("--output", default="out", help="Output folder")
    parser.add_argument(
        "--lang",
        default="eng",
        choices=["eng", "mar"],
        help="OCR language: 'eng' (English) or 'mar' (Marathi). "
             "Only one language is used per document."
    )

    args = parser.parse_args()
    process(args.input, args.output, args.lang)

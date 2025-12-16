import streamlit as st
from pathlib import Path
import json
import pytesseract
import os
import logging
import warnings
import tensorflow as tf

from main import process, risk_color

# -------------------------------
# Explicit Tesseract configuration
# -------------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

# -------------------------------
# Suppress noisy warnings
# -------------------------------
tf.get_logger().setLevel("ERROR")
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(
    page_title="RiskLens - Contract Risk Analyzer",
    layout="wide"
)

st.title("📄 RiskLens – AI Contract Risk Analyzer")

st.markdown(
    """
Upload a contract PDF and analyze legal risk using AI.
Supports **English** and **Marathi** documents.
"""
)

# -------------------------------
# Inputs
# -------------------------------
pdf_file = st.file_uploader("Upload Contract PDF", type=["pdf"])
lang = st.selectbox("OCR Language", ["eng", "mar"], index=0)

# -------------------------------
# Processing
# -------------------------------
if pdf_file:
    output_dir = Path("out")
    output_dir.mkdir(exist_ok=True)

    temp_pdf = Path("temp_uploaded.pdf")
    with open(temp_pdf, "wb") as f:
        f.write(pdf_file.getbuffer())

    if st.button("🚀 Run Analysis"):
        with st.spinner("Processing contract..."):
            try:
                process(str(temp_pdf), str(output_dir), lang)

                report_file = output_dir / f"{temp_pdf.stem}_report.json"

                if report_file.exists():
                    with open(report_file, "r", encoding="utf-8") as f:
                        report = json.load(f)

                    # -------------------------------
                    # Contract Risk Score
                    # -------------------------------
                    contract_score = report.get("contract_risk_score", 0)
                    st.metric(
                        label="📊 Contract Risk Score",
                        value=f"{contract_score} / 100"
                    )

                    st.divider()

                    # -------------------------------
                    # Clause-level breakdown
                    # -------------------------------
                    st.subheader("Clause Risk Analysis")

                    for clause in report.get("clauses", []):
                        title = clause.get("title") or "Clause"
                        body = clause.get("body", "")
                        label = clause.get("label", "Unknown")
                        score = clause.get("label_score", 0.0)
                        fields = clause.get("fields", {})

                        score_pct = int(score * 100)
                        rgb = risk_color(score_pct)
                        color_hex = "#%02x%02x%02x" % tuple(int(c * 255) for c in rgb)

                        with st.expander(f"{title} — {label} ({score_pct}%)"):
                            st.markdown(
                                f"""
                                <div style="
                                    background-color:{color_hex};
                                    padding:12px;
                                    border-radius:6px;
                                    color:black;
                                ">
                                {body}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            if fields:
                                st.markdown("**Extracted Fields**")
                                st.json(fields)

                # -------------------------------
                # Annotated PDF Download
                # -------------------------------
                annotated_pdf = output_dir / f"annotated_{temp_pdf.stem}.pdf"
                if annotated_pdf.exists():
                    st.download_button(
                        label="📥 Download Annotated PDF",
                        data=annotated_pdf.read_bytes(),
                        file_name=annotated_pdf.name,
                        mime="application/pdf"
                    )

                st.success("✅ Contract processed successfully")

            except Exception as e:
                st.error(f"❌ Error processing the PDF: {e}")

# 📄 RiskLens – AI-Powered Contract Risk Analyzer

RiskLens is an AI-driven contract analysis system that extracts text from PDFs using OCR, identifies contractual clauses, classifies legal risk, and generates an annotated risk report.
It supports English and Marathi contracts and provides a Streamlit-based UI for interactive analysis.

# 🚀 Features

📑 PDF Contract Processing

🔍 OCR-based Text Extraction (Tesseract OCR)

🌐 Multi-language Support (English & Marathi)

🧠 Zero-Shot Clause Classification

⚠️ Risk Scoring & Highlighting

📊 Automated Risk Report Generation

🖍️ Annotated PDF Output

🖥️ Interactive Streamlit UI

# 🛠️ Tech Stack

Programming Language: Python 3.10+

OCR Engine: Tesseract OCR (v5.5.0)

NLP / ML: Transformers, Zero-Shot Classification

PDF Processing: PyMuPDF, Pillow

Frontend: Streamlit

Environment: Conda

Deployment Ready: Local / Cloud (GCP, AWS)

## 📂 Project Structure

```text
RiskLens/
├── app/
│   ├── pdf_utils.py        # PDF text extraction & annotation
│   ├── ocr_utils.py        # OCR utilities (Tesseract)
│   ├── segmentation.py    # Clause segmentation
│   ├── classify.py        # Zero-shot classifier
│   ├── extractor.py       # Field extraction
│   ├── rules.py           # Risk scoring logic
│   └── report.py          # Report generation
│
├── streamlit_app.py       # Streamlit UI
├── main.py                # CLI entry point
├── requirements.txt
├── README.md
└── out/                   # Output files
```

# ⚙️ Setup Instructions
## 1️⃣ Create Conda Environment
conda create -n risklens python=3.10 -y
conda activate risklens

## 2️⃣ Install Dependencies
pip install -r requirements.txt

## 3️⃣ Install Tesseract OCR (Windows)

Download: https://github.com/UB-Mannheim/tesseract/wiki

Install to:

C:\Program Files\Tesseract-OCR\


Ensure available languages:

tessdata/
├── eng.traineddata
├── mar.traineddata

# ▶️ Run the Application
## 🔹 Streamlit UI (Recommended)
streamlit run streamlit_app.py


Upload a PDF

Select OCR language (English / Marathi)

Click Run Analysis

Download annotated PDF & view risk scores

## 🔹 CLI Mode
python main.py --input contract.pdf --output out --lang eng

# 📊 Output

### ✅ Risk Score (0–100)

### 📑 Clause-level Classification

### ⚠️ Highlighted Risky Clauses

### 📄 Annotated PDF

### 📁 JSON Risk Report

## 🧠 Risk Scoring Logic
Risk Level	Color
Low	🟢 Green
Medium	🟡 Yellow
High	🟠 Orange
Critical	🔴 Red
# 🎯 Use Cases

Legal Contract Review

Vendor Agreement Risk Analysis

Compliance Auditing

Legal Tech Demonstrations

Resume & Portfolio Projects

# 🔮 Future Enhancements

Multi-page clause-to-page mapping

Named Entity Recognition (NER)

Legal domain fine-tuned models

Cloud deployment (GCP / AWS)

Role-based access

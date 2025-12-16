import pdfplumber
from PIL import Image
import fitz
from pathlib import Path

def extract_text_pages(pdf_path:str):
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            text = p.extract_text()
            pages_text.append(text or "")
    return pages_text

def render_page_to_image(pdf_path:str, pageno:int, dpi:int=200):
    doc = fitz.open(pdf_path)
    page = doc[pageno]
    mat = fitz.Matrix(dpi/72, dpi/72)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def annotate_pdf(input_pdf:str, highlights:list, output_pdf:str):
    doc = fitz.open(input_pdf)
    for h in highlights:
        page = doc[h['page']]
        rect = fitz.Rect(h['bbox'])
        highlight = page.add_caret_annot(rect)
        highlight.set_colors(stroke=h.get('color',(1,0,0)))
        highlight.update()
    doc.save(output_pdf)

from PIL import Image
import cv2
import numpy as np
import pytesseract
import os
from pytesseract import TesseractError

# ---- Explicit Tesseract binding (Windows safe) ----
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"


def pil_to_cv(img: Image.Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def clean_image_for_ocr(pil_img: Image.Image) -> Image.Image:
    img = pil_to_cv(pil_img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(th)


def image_ocr(pil_img: Image.Image, lang: str = "eng") -> str:
    """
    SAFE OCR:
    - lang must be 'eng' OR 'mar'
    - NEVER uses eng+mar
    - Falls back to English if Marathi fails
    """
    cleaned = clean_image_for_ocr(pil_img)

    try:
        return pytesseract.image_to_string(cleaned, lang=lang)
    except TesseractError:
        return pytesseract.image_to_string(cleaned, lang="eng")

import pytesseract
import cv2
import os
from pdf2image import convert_from_path
from pytesseract import Output
from dotenv import load_dotenv
import numpy as np

root_path = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(root_path, ".env")
load_dotenv(dotenv_path)
pytesseract.pytesseract.tesseract_cmd =  os.getenv("TESSERACT_CMD")


def preprocess_image(img):
    """
    Prepare image for OCR:
    - Convert to grayscale to simplify data and focus on text contrast.
    - Apply median blur to reduce noise.

    """

    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY) 

    return cv2.medianBlur(gray, 3)


def pdf_to_text(pdf_path, dpis=(300, 400, 600,800)):

    """
    Extract text from a PDF using OCR for pdfs stored as images. 
    - Calls preprocess_image() to improve OCR quality.
    - Tries multiple DPIs (dots per inch) since the text size is unknown and optimal DPI is not known a priori.
    - Selects the result with the most characters as the "best" text (simple heuristic: more characters -> more content).

    Input:
        pdf_path: path to the PDF file
    Output:
        extracted text string
    """

    best_text = ""
    max_chars = 0

    for dpi in dpis:
        pages = convert_from_path(pdf_path, dpi)
        all_text = ""

        for page in pages:
            img = preprocess_image(page)
            text = pytesseract.image_to_string(img, config='--oem 3 --psm 4')
            all_text += text + "\n" 

        if len(text) > max_chars:  
            max_chars = len(text)
            best_text = all_text
        
        
    print("pdf parsed")
    return best_text

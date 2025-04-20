import os
from pdf2image import convert_from_path
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import io


import os


# Cấu hình đường dẫn tới Tesseract nếu cần (tuỳ hệ điều hành)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(pdf_path, max_pages=None):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page_num in range(len(doc)):
        if max_pages and page_num >= max_pages:
            break
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(image)
        all_text += text + "\n"
    return all_text

# Test nhanh khi chạy file trực tiếp
if __name__ == "__main__":
    test_file = "./data/pdfs/sample.pdf"
    text = extract_text_from_pdf(test_file)
    print(text[:1000])  # In thử 1000 ký tự đầu

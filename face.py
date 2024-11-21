import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from PIL import Image
import os

# Configure Tesseract OCR path (if needed)
# For Windows, it may be something like:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def pdf_to_text(pdf_path):
    """
    Convert PDF to text using OCR for images and PyMuPDF for text extraction.

    Args:
    - pdf_path (str): Path to the PDF file.

    Returns:
    - str: Extracted text from the PDF.
    """
    # Initialize text container
    full_text = ""

    # Open the PDF using PyMuPDF
    doc = fitz.open(pdf_path)

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        
        # Try to extract text using PyMuPDF first (for non-image PDFs)
        text = page.get_text()
        
        # If no text is extracted (i.e., it's an image-based page), use OCR
        if not text.strip():
            # Convert the page to an image
            pix = page.get_pixmap()
            img_path = f"page_{page_num}.png"
            pix.save(img_path)
            
            # Use pytesseract to extract text from the image
            img = Image.open(img_path)
            text = pytesseract.image_to_string(img)
            
            # Remove the temporary image file
            os.remove(img_path)

        # Append the extracted text from this page
        full_text += text + "\n"

    return full_text


if __name__ == "__main__":
    input_pdf = "report2 real.pdf"  # Path to your input PDF

    # Extract text from the PDF
    extracted_text = pdf_to_text(input_pdf)

    # Print extracted text (for demonstration)
    print(extracted_text)

    # Optionally, you can save the text to a file
    with open("output.txt", "w") as text_file:
        text_file.write(extracted_text)

    print("Text extraction complete. Output saved to 'output.txt'.")

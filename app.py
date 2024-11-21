 

# # from flask import Flask, request, jsonify
# # import face_recognition
# # import cv2
# # import numpy as np
# # import requests
# # from io import BytesIO
# # from PIL import Image
# # from typing import List, Union
# # from werkzeug.utils import secure_filename
# # import os

# # app = Flask(__name__)
# # app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# # app.config['UPLOAD_FOLDER'] = 'uploads'

# # # Ensure upload folder exists
# # os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # def load_image_from_source(image_source):
# #     """
# #     Load image from file path or URL
# #     Supports local files and image URLs
# #     """
# #     try:
# #         if isinstance(image_source, str) and (image_source.startswith('http://') or image_source.startswith('https://')):
# #             response = requests.get(image_source)
# #             image = Image.open(BytesIO(response.content))
# #             image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
# #         else:
# #             image = face_recognition.load_image_file(image_source)
# #         return image
# #     except Exception as e:
# #         raise ValueError(f"Could not load image: {str(e)}")

# # def verify_faces(known_image_source: str, unknown_image_sources: Union[str, List[str]]):
# #     """
# #     Compare one face against multiple faces
# #     """
# #     try:
# #         # Load reference face
# #         known_image = load_image_from_source(known_image_source)
# #         known_encodings = face_recognition.face_encodings(known_image)
        
# #         if len(known_encodings) == 0:
# #             return {"matched": False, "error": "No face detected in reference image"}

# #         known_encoding = known_encodings[0]

# #         # Handle single image or list of images
# #         if isinstance(unknown_image_sources, str):
# #             unknown_image_sources = [unknown_image_sources]

# #         # Check each image
# #         results = []
# #         for idx, unknown_source in enumerate(unknown_image_sources):
# #             try:
# #                 # Load and check unknown face
# #                 unknown_image = load_image_from_source(unknown_source)
# #                 unknown_encodings = face_recognition.face_encodings(unknown_image)

# #                 if len(unknown_encodings) == 0:
# #                     results.append({
# #                         "image_index": idx,
# #                         "image_source": unknown_source,
# #                         "matched": False,
# #                         "error": "No face detected"
# #                     })
# #                     continue

# #                 # Check each face in the current image
# #                 matches = []
# #                 for unknown_encoding in unknown_encodings:
# #                     face_distances = face_recognition.face_distance([known_encoding], unknown_encoding)
# #                     matches.append({
# #                         "distance": float(face_distances[0]),
# #                         "matched": face_distances[0] < 0.6
# #                     })

# #                 results.append({
# #                     "image_index": idx,
# #                     "image_source": unknown_source,
# #                     "matches": matches
# #                 })

# #             except Exception as e:
# #                 results.append({
# #                     "image_index": idx,
# #                     "image_source": unknown_source,
# #                     "matched": False,
# #                     "error": str(e)
# #                 })

# #         return {
# #             "results": results,
# #             "overall_matched": any(any(match["matched"] for match in result["matches"]) 
# #                                  for result in results if "matches" in result)
# #         }

# #     except Exception as e:
# #         return {"matched": False, "error": str(e)}


# # # @app.route('/verify', methods=['POST'])
# # # def verify():
# # #     try:
# # #         # Parse JSON input
# # #         data = request.get_json()
# # #         if not data:
# # #             return jsonify({"error": "Invalid or missing JSON input"}), 400
        
# # #         # Validate input structure
# # #         reference_image = data.get("reference_image")
# # #         comparison_images = data.get("comparison_images")
        
# # #         if not reference_image:
# # #             return jsonify({"error": "Missing 'reference_image' in input"}), 400
        
# # #         if not comparison_images or not isinstance(comparison_images, list):
# # #             return jsonify({"error": "Missing or invalid 'comparison_images' in input"}), 400

# # #         # Perform face verification
# # #         result = verify_faces(reference_image, comparison_images)
# # #         return jsonify(result)

# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 500

# # @app.route('/verify', methods=['POST'])
# # def verify():
# #     try:
# #         # Parse JSON input
# #         data = request.get_json()
# #         if not data:
# #             return jsonify({"error": "Invalid or missing JSON input"}), 400
        
# #         # Validate input structure
# #         reference_image = data.get("reference_image")
# #         comparison_images = data.get("comparison_images")
        
# #         if not reference_image:
# #             return jsonify({"error": "Missing 'reference_image' in input"}), 400
        
# #         if not comparison_images or not isinstance(comparison_images, list):
# #             return jsonify({"error": "Missing or invalid 'comparison_images' in input"}), 400

# #         # Perform face verification
# #         result = verify_faces(reference_image, comparison_images)

# #         # Check if overall matched is True
# #         if result.get("overall_matched"):
# #             return "matched 200k", 200

# #         # Return detailed results if not completely matched
# #         return jsonify(result)

# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500


# # if __name__ == '__main__':
# #     app.run(debug=True, host='0.0.0.0', port=5000)


# from flask import Flask, request, jsonify
# import pytesseract
# from pdf2image import convert_from_path
# import fitz  # PyMuPDF
# from PIL import Image
# import os
# import tempfile

# # Initialize Flask app
# app = Flask(__name__)

# # Set the Tesseract executable path explicitly for Windows (uncomment if needed)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# def pdf_to_text(pdf_path):
#     """
#     Convert PDF to text using PyMuPDF for both text and image extraction.
    
#     Args:
#     - pdf_path (str): Path to the PDF file.

#     Returns:
#     - str: Extracted text from the PDF.
#     """
#     full_text = ""

#     # Open the PDF using PyMuPDF
#     doc = fitz.open(pdf_path)

#     for page_num in range(doc.page_count):
#         page = doc.load_page(page_num)

#         # Try to extract text directly
#         text = page.get_text()
        
#         # If no text is found, use PyMuPDF's pixmap for OCR
#         if not text.strip():
#             try:
#                 # Convert page to image
#                 pix = page.get_pixmap()
                
#                 # Save pixmap as temporary image
#                 img_path = tempfile.mktemp(suffix=".png")
#                 pix.save(img_path)
                
#                 # Use Tesseract OCR on the image
#                 text = pytesseract.image_to_string(Image.open(img_path))
            
#             except Exception as e:
#                 print(f"OCR Error on page {page_num}: {str(e)}")
#                 text = ""
            
#             finally:
#                 # Clean up temporary image if it exists
#                 if 'img_path' in locals() and os.path.exists(img_path):
#                     os.remove(img_path)

#         # Append the extracted text from the current page
#         full_text += text + "\n"

#     return full_text


# @app.route('/extract_text', methods=['POST'])
# def extract_text():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     # Save the uploaded PDF file temporarily in a temp directory
#     with tempfile.NamedTemporaryFile(delete=False) as tmp_pdf:
#         pdf_path = tmp_pdf.name
#         file.save(pdf_path)

#     # Extract text from the PDF using the pdf_to_text function
#     try:
#         extracted_text = pdf_to_text(pdf_path)
#         return jsonify({"extracted_text": extracted_text}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         # Clean up the temporary PDF file after extraction
#         if os.path.exists(pdf_path):
#             os.remove(pdf_path)


# if __name__ == '__main__':
#     # Ensure app listens on all interfaces, useful for cloud deployment
#     app.run(debug=True, host='0.0.0.0', port=8000)

from flask import Flask, request, jsonify
import requests
import PyPDF2
import io

app = Flask(__name__)

def extract_text_from_pdf_bytes(pdf_bytes):
    """
    Extract text from PDF bytes.
    
    Args:
        pdf_bytes (bytes): PDF content as bytes
    
    Returns:
        str: Extracted text from PDF
    """
    try:
        # Use PyPDF2 for efficient text extraction
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"

@app.route('/extract_pdf', methods=['POST'])
def extract_pdf():
    """
    Endpoint to extract text from PDF.
    Supports file upload and PDF URL.
    
    Returns:
        JSON response with extracted text
    """
    # Check if PDF is uploaded as a file
    if 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']
        pdf_bytes = pdf_file.read()
        extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
        return jsonify({"text": extracted_text})
    
    # Check if PDF URL is provided
    elif 'pdf_url' in request.json:
        try:
            pdf_url = request.json['pdf_url']
            
            # Download PDF with timeout and size limit to prevent server overload
            response = requests.get(pdf_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Limit download size to 10MB to prevent excessive load
            content_length = int(response.headers.get('content-length', 0))
            if content_length > 10 * 1024 * 1024:  # 10MB limit
                return jsonify({"error": "PDF size exceeds 10MB limit"}), 413
            
            pdf_bytes = response.content
            extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
            return jsonify({"text": extracted_text})
        
        except requests.RequestException as e:
            return jsonify({"error": f"Error downloading PDF: {str(e)}"}), 400
    
    else:
        return jsonify({"error": "No PDF file or URL provided"}), 400

# Optional: Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
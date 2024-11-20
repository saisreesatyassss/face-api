# import face_recognition
# import cv2
# import numpy as np
# import requests
# from io import BytesIO
# from PIL import Image
# from typing import List, Union

# def load_image_from_source(image_source):
#     """
#     Load image from file path or URL
#     Supports local files and image URLs
#     """
#     try:
#         if isinstance(image_source, str) and (image_source.startswith('http://') or image_source.startswith('https://')):
#             response = requests.get(image_source)
#             image = Image.open(BytesIO(response.content))
#             image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#         else:
#             image = face_recognition.load_image_file(image_source)
#         return image
#     except Exception as e:
#         raise ValueError(f"Could not load image: {str(e)}")

# def verify_faces(known_image_source: str, unknown_image_sources: Union[str, List[str]]):
#     """
#     Compare one face against multiple faces
#     Args:
#         known_image_source: Path or URL to the reference face
#         unknown_image_sources: List of paths or URLs to compare against
#     """
#     try:
#         # Load reference face
#         known_image = load_image_from_source(known_image_source)
#         known_encodings = face_recognition.face_encodings(known_image)
        
#         if len(known_encodings) == 0:
#             return {"matched": False, "error": "No face detected in reference image"}

#         known_encoding = known_encodings[0]

#         # Handle single image or list of images
#         if isinstance(unknown_image_sources, str):
#             unknown_image_sources = [unknown_image_sources]

#         # Check each image
#         for idx, unknown_source in enumerate(unknown_image_sources):
#             try:
#                 # Load and check unknown face
#                 unknown_image = load_image_from_source(unknown_source)
#                 unknown_encodings = face_recognition.face_encodings(unknown_image)

#                 if len(unknown_encodings) == 0:
#                     continue  # Skip if no face detected

#                 # Check each face in the current image
#                 for unknown_encoding in unknown_encodings:
#                     face_distances = face_recognition.face_distance([known_encoding], unknown_encoding)
#                     if face_distances[0] < 0.6:  # Threshold for matching
#                         return {
#                             "matched": True,
#                             "image_index": idx,
#                             "image_source": unknown_source,
#                             "distance": float(face_distances[0])
#                         }

#             except Exception as e:
#                 print(f"Error processing image {idx}: {str(e)}")
#                 continue

#         # If no matches found
#         return {
#             "matched": False,
#             "message": "No matching faces found in any of the provided images"
#         }

#     except Exception as e:
#         return {"matched": False, "error": str(e)}

# # Example usage
# if __name__ == "__main__":
#     # Single reference image
#     reference_image =         "https://imgs.search.brave.com/sLyyKnVs3pQCsSTIl_gXO4cHO0iq69jPeUTfLlMcXog/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly90My5m/dGNkbi5uZXQvanBn/LzA1LzQ2Lzc2LzI4/LzM2MF9GXzU0Njc2/Mjg2NF9nYmNXelVR/aklRWEsybWhGd3p5/cTEwdDNLNm4wYTBI/MC5qcGc"
    
#     # List of images to compare against
#     compare_images = [
#         "image1.jpg",
#         "image2.jpg",
#         "https://example.com/test1.jpg",
#         "https://example.com/test2.jpg"
#     ]

#     # Example with URL and local files
#     result = verify_faces(reference_image ,compare_images)
#     print("Verification result:", result)



from flask import Flask, request, jsonify
import face_recognition
import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image
from typing import List, Union
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def load_image_from_source(image_source):
    """
    Load image from file path or URL
    Supports local files and image URLs
    """
    try:
        if isinstance(image_source, str) and (image_source.startswith('http://') or image_source.startswith('https://')):
            response = requests.get(image_source)
            image = Image.open(BytesIO(response.content))
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            image = face_recognition.load_image_file(image_source)
        return image
    except Exception as e:
        raise ValueError(f"Could not load image: {str(e)}")

def verify_faces(known_image_source: str, unknown_image_sources: Union[str, List[str]]):
    """
    Compare one face against multiple faces
    """
    try:
        # Load reference face
        known_image = load_image_from_source(known_image_source)
        known_encodings = face_recognition.face_encodings(known_image)
        
        if len(known_encodings) == 0:
            return {"matched": False, "error": "No face detected in reference image"}

        known_encoding = known_encodings[0]

        # Handle single image or list of images
        if isinstance(unknown_image_sources, str):
            unknown_image_sources = [unknown_image_sources]

        # Check each image
        results = []
        for idx, unknown_source in enumerate(unknown_image_sources):
            try:
                # Load and check unknown face
                unknown_image = load_image_from_source(unknown_source)
                unknown_encodings = face_recognition.face_encodings(unknown_image)

                if len(unknown_encodings) == 0:
                    results.append({
                        "image_index": idx,
                        "image_source": unknown_source,
                        "matched": False,
                        "error": "No face detected"
                    })
                    continue

                # Check each face in the current image
                matches = []
                for unknown_encoding in unknown_encodings:
                    face_distances = face_recognition.face_distance([known_encoding], unknown_encoding)
                    matches.append({
                        "distance": float(face_distances[0]),
                        "matched": face_distances[0] < 0.6
                    })

                results.append({
                    "image_index": idx,
                    "image_source": unknown_source,
                    "matches": matches
                })

            except Exception as e:
                results.append({
                    "image_index": idx,
                    "image_source": unknown_source,
                    "matched": False,
                    "error": str(e)
                })

        return {
            "results": results,
            "overall_matched": any(any(match["matched"] for match in result["matches"]) 
                                 for result in results if "matches" in result)
        }

    except Exception as e:
        return {"matched": False, "error": str(e)}

@app.route('/verify', methods=['POST'])
def verify():
    try:
        # Check if the post request has the files part
        if 'reference_image' not in request.files:
            return jsonify({"error": "No reference image provided"}), 400
        
        reference_file = request.files['reference_image']
        if reference_file.filename == '':
            return jsonify({"error": "No reference image selected"}), 400

        # Save reference image
        reference_filename = secure_filename(reference_file.filename)
        reference_path = os.path.join(app.config['UPLOAD_FOLDER'], reference_filename)
        reference_file.save(reference_path)

        # Get comparison images
        comparison_images = []
        
        # Handle URL-based comparisons
        comparison_urls = request.form.getlist('comparison_urls')
        if comparison_urls:
            comparison_images.extend(comparison_urls)

        # Handle file-based comparisons
        if 'comparison_images' in request.files:
            files = request.files.getlist('comparison_images')
            for file in files:
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    comparison_images.append(filepath)

        if not comparison_images:
            return jsonify({"error": "No comparison images provided"}), 400

        # Perform verification
        result = verify_faces(reference_path, comparison_images)

        # Clean up uploaded files
        try:
            os.remove(reference_path)
            for path in comparison_images:
                if not path.startswith('http'):
                    os.remove(path)
        except Exception as e:
            print(f"Error cleaning up files: {str(e)}")

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

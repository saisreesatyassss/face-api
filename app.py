 

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


# @app.route('/verify', methods=['POST'])
# def verify():
#     try:
#         # Parse JSON input
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Invalid or missing JSON input"}), 400
        
#         # Validate input structure
#         reference_image = data.get("reference_image")
#         comparison_images = data.get("comparison_images")
        
#         if not reference_image:
#             return jsonify({"error": "Missing 'reference_image' in input"}), 400
        
#         if not comparison_images or not isinstance(comparison_images, list):
#             return jsonify({"error": "Missing or invalid 'comparison_images' in input"}), 400

#         # Perform face verification
#         result = verify_faces(reference_image, comparison_images)
#         return jsonify(result)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/verify', methods=['POST'])
def verify():
    try:
        # Parse JSON input
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON input"}), 400
        
        # Validate input structure
        reference_image = data.get("reference_image")
        comparison_images = data.get("comparison_images")
        
        if not reference_image:
            return jsonify({"error": "Missing 'reference_image' in input"}), 400
        
        if not comparison_images or not isinstance(comparison_images, list):
            return jsonify({"error": "Missing or invalid 'comparison_images' in input"}), 400

        # Perform face verification
        result = verify_faces(reference_image, comparison_images)

        # Check if overall matched is True
        if result.get("overall_matched"):
            return "matched 200k", 200

        # Return detailed results if not completely matched
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=500)
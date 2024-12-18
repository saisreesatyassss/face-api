# import face_recognition
# import cv2
# import numpy as np

# def verify_face(known_image_path, unknown_image_path):
#     # Load known face
#     known_image = face_recognition.load_image_file(known_image_path)
#     known_encoding = face_recognition.face_encodings(known_image)[0]

#     # Load unknown face
#     unknown_image = face_recognition.load_image_file(unknown_image_path)
#     unknown_encodings = face_recognition.face_encodings(unknown_image)

#     if len(unknown_encodings) == 0:
#         return {"verified": False, "error": "No face detected in unknown image"}

#     # Compare faces
#     matches = face_recognition.compare_faces([known_encoding], unknown_encodings[0])
#     face_distances = face_recognition.face_distance([known_encoding], unknown_encodings[0])

#     result = {
#         "verified": matches[0],
#         "distance": float(face_distances[0]),
#         "threshold_met": face_distances[0] < 0.6  # Typical threshold
#     }

#     return result

# # Example usage
# if __name__ == "__main__":
#     result = verify_face("img1.png", "img3.jpeg")
#     print(result)










import face_recognition
import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image

def load_image_from_source(image_source):
    """
    Load image from file path or URL
    Supports local files and image URLs
    """
    try:
        # Check if it's a URL
        if isinstance(image_source, str) and (image_source.startswith('http://') or image_source.startswith('https://')):
            response = requests.get(image_source)
            image = Image.open(BytesIO(response.content))
            # Convert PIL Image to numpy array
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            # Load from local file
            image = face_recognition.load_image_file(image_source)
        
        return image
    except Exception as e:
        raise ValueError(f"Could not load image: {str(e)}")

def verify_face(known_image_source, unknown_image_source):
    try:
        # Load known face
        known_image = load_image_from_source(known_image_source)
        known_encodings = face_recognition.face_encodings(known_image)
        
        if len(known_encodings) == 0:
            return {"verified": False, "error": "No face detected in known image"}

        known_encoding = known_encodings[0]

        # Load unknown face
        unknown_image = load_image_from_source(unknown_image_source)
        unknown_encodings = face_recognition.face_encodings(unknown_image)

        if len(unknown_encodings) == 0:
            return {"verified": False, "error": "No face detected in unknown image"}

        # Compare faces
        matches = face_recognition.compare_faces([known_encoding], unknown_encodings[0])
        face_distances = face_recognition.face_distance([known_encoding], unknown_encodings[0])

        result = {
            "verified": matches[0],
            "distance": float(face_distances[0]),
            "threshold_met": face_distances[0] < 0.6  # Typical threshold
        }

        return result

    except Exception as e:
        return {"verified": False, "error": str(e)}

# Example usage
if __name__ == "__main__": 
    # URL example
    url_result = verify_face(
        "https://imgs.search.brave.com/sLyyKnVs3pQCsSTIl_gXO4cHO0iq69jPeUTfLlMcXog/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly90My5m/dGNkbi5uZXQvanBn/LzA1LzQ2Lzc2LzI4/LzM2MF9GXzU0Njc2/Mjg2NF9nYmNXelVR/aklRWEsybWhGd3p5/cTEwdDNLNm4wYTBI/MC5qcGc", 
       "img3.jpeg"
    )
    print("URL example result:", url_result)#   f a c e - a p i  
 
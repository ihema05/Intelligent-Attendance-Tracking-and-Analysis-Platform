import face_recognition
import pickle
import os
import cv2

# ====================================================
# CONFIG
# ====================================================
IMAGES_DIR = "images"
ENCODING_FILE = "encodings.pkl"

known_encodings = []
known_names = []

# ====================================================
# LOAD IMAGES AND ENCODE
# ====================================================
print("[INFO] Encoding faces...")

for filename in os.listdir(IMAGES_DIR):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(IMAGES_DIR, filename)

        # Filename format:
        # Ziad_Reda_Mohamed_231014601.jpg
        name = os.path.splitext(filename)[0]

        image = face_recognition.load_image_file(path)
        locations = face_recognition.face_locations(image)

        if len(locations) != 1:
            print(f"[WARNING] {filename} skipped (found {len(locations)} faces)")
            continue

        encoding = face_recognition.face_encodings(image, locations)[0]
        known_encodings.append(encoding)
        known_names.append(name)

        print(f"[OK] Encoded: {name}")

# ====================================================
# SAVE ENCODINGS
# ====================================================
data = {
    "encodings": known_encodings,
    "names": known_names
}

with open(ENCODING_FILE, "wb") as f:
    pickle.dump(data, f)

print(f"[DONE] Encodings saved to {ENCODING_FILE}")

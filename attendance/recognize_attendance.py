import cv2
import face_recognition
import pickle
import sys
import os
import csv
from datetime import datetime

# ====================================================
# ARGUMENTS FROM R
# ====================================================
course = sys.argv[1]
csv_path = sys.argv[2]
week = int(sys.argv[3])   # ✅ numeric week from R

# ====================================================
# LOAD FACE ENCODINGS
# ====================================================
with open("encodings.pkl", "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]

# ====================================================
# ENSURE CSV EXISTS
# ====================================================
if not os.path.exists(csv_path):
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "StudentID",
            "Name",
            "Date",
            "Time",
            "Course",
            "Week",
            "Confidence",
            "Present"
        ])

# ====================================================
# LOAD EXISTING ATTENDANCE (PREVENT DUPLICATES)
# ====================================================
recorded = set()

with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["Week"] != "":
            recorded.add((row["StudentID"], int(row["Week"])))

# ====================================================
# START CAMERA
# ====================================================
cap = cv2.VideoCapture(0)

print(f"[INFO] Camera started for {course} | Week {week}")
print("[INFO] Press Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, locations)

    for (top, right, bottom, left), face_encoding in zip(locations, encodings):

        matches = face_recognition.compare_faces(
            known_encodings, face_encoding, tolerance=0.45
        )

        name = "Unknown"
        confidence = 0

        if True in matches:
            matched_idxs = [i for i, m in enumerate(matches) if m]
            counts = {}

            for i in matched_idxs:
                counts[known_names[i]] = counts.get(known_names[i], 0) + 1

            name = max(counts, key=counts.get)
            confidence = round((counts[name] / len(matches)) * 100, 2)

        if name != "Unknown":
            parts = name.split("_")
            student_id = parts[-1]
            student_name = " ".join(parts[:-1])

            key = (student_id, week)

            # ====================================================
            # ONE ATTENDANCE PER STUDENT PER WEEK
            # ====================================================
            if key not in recorded:
                now = datetime.now()

                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        student_id,
                        student_name,
                        now.strftime("%Y-%m-%d"),
                        now.strftime("%H:%M:%S"),
                        course,
                        week,
                        confidence,
                        1
                    ])

                recorded.add(key)
                print(f"[SAVED] {student_name} | Week {week}")

        # DRAW FACE BOX
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(
            frame,
            f"{name} ({confidence}%)",
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    cv2.imshow("Attendance Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("[INFO] Camera closed")

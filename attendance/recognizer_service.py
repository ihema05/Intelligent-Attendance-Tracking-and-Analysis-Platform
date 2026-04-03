import cv2
import face_recognition
import os
import pickle
import pandas as pd
from datetime import datetime
import time
import sys

# Global flag used to stop camera from R
RUN_FLAG_FILE = "recognizer_run.flag"

# Folder to store attendance
ATTENDANCE_DIR = "attendance"
if not os.path.exists(ATTENDANCE_DIR):
    os.makedirs(ATTENDANCE_DIR)

# Load encodings
ENCODINGS_FILE = "encodings.pkl"
data = pickle.load(open(ENCODINGS_FILE, "rb"))
known_encodings = data["encodings"]
known_names = data["names"]


def mark_attendance(name, course):
    """Writes a row into the course CSV."""
    course_csv = os.path.join(ATTENDANCE_DIR, f"{course}.csv")

    # Create file if missing
    if not os.path.exists(course_csv):
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
        df.to_csv(course_csv, index=False)

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_ = now.strftime("%H:%M:%S")

    df = pd.read_csv(course_csv)

    # Avoid double entry
    if not ((df["Name"] == name) & (df["Date"] == date)).any():
        df.loc[len(df)] = [name, date, time_]
        df.to_csv(course_csv, index=False)
        print(f"[LOG] Marked attendance for {name} in {course}")


def start_recognition(course):
    """Main camera loop. Runs until R deletes the flag file."""

    # Create flag ON
    with open(RUN_FLAG_FILE, "w") as f:
        f.write("run")

    print("[SERVICE] Starting recognition...")
    print(f"[SERVICE] Course: {course}")

    video = cv2.VideoCapture(0)
    if not video.isOpened():
        print("[ERROR] Camera not found.")
        return

    while os.path.exists(RUN_FLAG_FILE):

        ret, frame = video.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Face locations
        try:
            locs = face_recognition.face_locations(rgb, model="hog")
        except:
            locs = []

        # Face encodings
        try:
            encs = face_recognition.face_encodings(rgb, locs)
        except:
            encs = []

        for enc in encs:
            matches = face_recognition.compare_faces(known_encodings, enc, tolerance=0.45)
            name = "Unknown"

            if True in matches:
                idx = matches.index(True)
                name = known_names[idx]

            if name != "Unknown":
                mark_attendance(name, course)

        time.sleep(0.05)  # Reduce CPU usage

    video.release()
    print("[SERVICE] Recognition STOPPED")


def stop_recognition():
    """R removes the run flag."""
    if os.path.exists(RUN_FLAG_FILE):
        os.remove(RUN_FLAG_FILE)
        print("[SERVICE] Stop signal sent")


# Allow CLI control as well
if __name__ == "__main__":
    cmd = sys.argv[1]

    if cmd == "start":
        course = sys.argv[2]
        start_recognition(course)

    elif cmd == "stop":
        stop_recognition()

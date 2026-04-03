import os
import pandas as pd

# Always use absolute path to prevent nested folders
BASE_DIR = os.getcwd()
ATTENDANCE_DIR = os.path.join(BASE_DIR, "attendance")

# Create correct folder if missing
if not os.path.exists(ATTENDANCE_DIR):
    os.makedirs(ATTENDANCE_DIR)

courses = [
    "Prof. Training In Mobile App Programming",
    "Introduction To Artificial Intelligence",
    "Operating Systems",
    "Mathematical Foundations For Al",
    "Advanced Statistics",
    "Fundamentals Of Robotics"
]

for course in courses:
    file_path = os.path.join(ATTENDANCE_DIR, f"{course}.csv")

    df = pd.DataFrame(columns=["Name", "Date", "Time"])
    df.to_csv(file_path, index=False)

    print(f"[CREATED] {file_path}")

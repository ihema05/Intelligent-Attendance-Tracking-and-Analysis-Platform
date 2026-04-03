import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import os

COURSES = {
    "Prof. Training In Mobile App Programming": "mobile_app",
    "Introduction To Artificial Intelligence": "ai_intro",
    "Operating Systems": "operating_systems",
    "Mathematical Foundations For AI": "math_ai",
    "Advanced Statistics": "statistics"
}

PYTHON_EXE = sys.executable  # uses active conda env

def run_attendance(course_key):
    course_code = COURSES[course_key]
    enc_path = "encodings.pkl"
    out_csv = f"attendance_{course_code}.csv"

    cmd = [
        PYTHON_EXE,
        "recognize_attendance.py",
        "--encodings", enc_path,
        "--output", out_csv,
        "--course", course_key,
        "--camera", "0"
    ]

    subprocess.Popen(cmd)

def main():
    root = tk.Tk()
    root.title("Attendance System (AI-Based)")
    root.geometry("500x450")

    title = tk.Label(root, text="Automatic Attendance System", 
                     font=("Arial", 18, "bold"))
    title.pack(pady=20)

    frame = tk.Frame(root)
    frame.pack()

    for course in COURSES:
        btn = ttk.Button(frame, text=course,
                         command=lambda c=course: run_attendance(c))
        btn.pack(pady=8, fill="x", ipadx=10)

    root.mainloop()

if __name__ == "__main__":
    main()

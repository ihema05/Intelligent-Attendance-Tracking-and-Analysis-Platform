# attendance_gui.py — Tkinter GUI with embedded webcam + robust recognition fallback
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading, time, csv, pickle
from pathlib import Path
from datetime import datetime
import cv2
import face_recognition
import numpy as np
import pandas as pd

# === SETTINGS ===
ENCODINGS_PATH = "encodings.pkl"   # must exist in project folder
DETECTION_MODEL = "hog"            # "hog" for CPU; "cnn" requires proper dlib build
CAMERA_INDEX = 0                   # try 1 if 0 doesn't work
DEFAULT_TOLERANCE = 0.6
MIN_CONF_PERCENT = 30.0            # minimum mapped confidence to log
DEBOUNCE_SECONDS = 10              # don't log same person too often
COURSES = {
    "Prof. Training In Mobile App Programming": "attendance_mobile_app.csv",
    "Introduction To Artificial Intelligence": "attendance_ai_intro.csv",
    "Operating Systems": "attendance_operating_systems.csv",
    "Mathematical Foundations For AI": "attendance_math_ai.csv",
    "Advanced Statistics": "attendance_statistics.csv"
}
# =================

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance System (Tkinter)")
        self.frame = ttk.Frame(root, padding=10)
        self.frame.grid(sticky="nsew")
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        # Left controls
        left = ttk.Frame(self.frame)
        left.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        ttk.Label(left, text="Select course:", font=("Arial", 11)).pack(anchor="w")
        self.course_var = tk.StringVar(value=list(COURSES.keys())[0])
        ttk.Combobox(left, textvariable=self.course_var, values=list(COURSES.keys()), state="readonly", width=48).pack(pady=6)

        ttk.Button(left, text="Start Camera (Preview)", command=self.start_preview).pack(fill="x", pady=4)
        ttk.Button(left, text="Start Recognition (Log)", command=self.start_recognition).pack(fill="x", pady=4)
        ttk.Button(left, text="Stop", command=self.stop).pack(fill="x", pady=4)

        ttk.Label(left, text="Tolerance (lower = stricter):").pack(anchor="w", pady=(8,0))
        self.tol_var = tk.DoubleVar(value=DEFAULT_TOLERANCE)
        ttk.Scale(left, from_=0.3, to=1.0, variable=self.tol_var, orient="horizontal").pack(fill="x")

        ttk.Label(left, text="Min Confidence% to log:").pack(anchor="w", pady=(8,0))
        self.conf_var = tk.DoubleVar(value=MIN_CONF_PERCENT)
        ttk.Scale(left, from_=20, to=95, variable=self.conf_var, orient="horizontal").pack(fill="x")

        self.status = tk.StringVar(value="Status: Idle")
        ttk.Label(left, textvariable=self.status, foreground="blue").pack(anchor="w", pady=(10,0))

        # Right: video preview
        right = ttk.Frame(self.frame)
        right.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.video_label = ttk.Label(right)
        self.video_label.pack()

        # bottom: recognition info
        bottom = ttk.Frame(self.frame)
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8,0))
        self.recog_text = tk.StringVar(value="Ready")
        ttk.Label(bottom, textvariable=self.recog_text, font=("Arial", 12)).pack()

        # internals
        self.vs = None
        self.running = False
        self.recognizing = False
        self.thread = None
        self.known_encodings = []
        self.known_ids = []
        self.last_seen = {}
        self.load_encodings()

    def load_encodings(self):
        p = Path(ENCODINGS_PATH)
        if not p.exists():
            messagebox.showerror("Missing encodings", f"Could not find {ENCODINGS_PATH}")
            self.status.set("Status: Missing encodings.pkl")
            return
        with open(p, "rb") as fh:
            data = pickle.load(fh)
        self.known_encodings = data.get("encodings", [])
        self.known_ids = data.get("ids", data.get("names", []))
        self.status.set(f"Loaded {len(self.known_ids)} encodings")

    def start_preview(self):
        if self.running:
            self.status.set("Already running")
            return
        # try DirectShow on Windows (more reliable)
        try:
            self.vs = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        except Exception:
            self.vs = cv2.VideoCapture(CAMERA_INDEX)
        if not self.vs.isOpened():
            self.status.set("Unable to open camera. Check index/permissions.")
            messagebox.showerror("Camera", "Unable to open camera. Try changing CAMERA_INDEX to 1 and restart.")
            return
        self.running = True
        self.recognizing = False
        self.thread = threading.Thread(target=self.video_loop, daemon=True)
        self.thread.start()
        self.status.set("Camera preview started")

    def start_recognition(self):
        if not self.running:
            self.start_preview()
            time.sleep(0.5)
        self.recognizing = True
        self.last_seen = {}
        self.status.set("Recognition started — logging enabled")

    def stop(self):
        self.running = False
        self.recognizing = False
        self.status.set("Stopping...")
        time.sleep(0.2)
        if self.vs:
            self.vs.release()
            self.vs = None
        self.video_label.config(image="")
        self.status.set("Status: Idle")

    def video_loop(self):
        try:
            while self.running:
                ret, frame = self.vs.read()
                if not ret:
                    self.status.set("Frame read failed")
                    break

                # display frame in GUI
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img = img.resize((640, 480))
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

                if self.recognizing:
                    small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
                    rgb = small[:, :, ::-1]

                    # Robust face_locations + face_encodings with fallback
                    try:
                        locs = face_recognition.face_locations(rgb, model=DETECTION_MODEL)
                    except Exception as e:
                        print("face_recognition face_locations error:", e)
                        locs = []

                    encs = []
                    if len(locs) > 0:
                        try:
                            encs = face_recognition.face_encodings(rgb, locs)
                        except TypeError as te:
                            print("face_recognition error (TypeError), falling back to face_encodings(rgb):", te)
                            try:
                                encs = face_recognition.face_encodings(rgb)
                                if len(locs) != len(encs):
                                    locs = face_recognition.face_locations(rgb, model=DETECTION_MODEL)
                            except Exception as e2:
                                print("face_recognition fallback also failed:", e2)
                                encs = []
                        except Exception as e:
                            print("face_recognition face_encodings error:", e)
                            encs = []
                    else:
                        try:
                            encs = face_recognition.face_encodings(rgb)
                            locs = face_recognition.face_locations(rgb, model=DETECTION_MODEL)
                        except Exception as e:
                            print("face_recognition no-locs fallback failed:", e)
                            locs = []; encs = []

                    for enc, loc in zip(encs, locs):
                        if len(self.known_encodings) == 0:
                            name = "Unknown (no encodings)"
                            conf = 0.0
                        else:
                            try:
                                dists = face_recognition.face_distance(self.known_encodings, enc)
                                idx = int(np.argmin(dists))
                                best = float(dists[idx])
                                conf = round(max(0, min(1.0, 1.0 - best)) * 100.0, 2)
                                if best <= float(self.tol_var.get()) and conf >= float(self.conf_var.get()):
                                    name = self.known_ids[idx]
                                else:
                                    name = "Unknown"
                            except Exception as e:
                                print("Distance/argmin error:", e)
                                name = "Unknown"
                                conf = 0.0

                        self.recog_text.set(f"Recognized: {name} — {conf}%")

                        # log attendance if meets criteria
                        course_csv = COURSES[self.course_var.get()]
                        if name != "Unknown":
                            now = time.time()
                            key = f"{name}|{course_csv}"
                            if key not in self.last_seen or (now - self.last_seen[key]) > DEBOUNCE_SECONDS:
                                self.mark_attendance(Path(course_csv), name, self.course_var.get(), conf)
                                self.last_seen[key] = now

                # brief sleep
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                    break
        except RuntimeError as e:
            print("[ERROR] Runtime in video loop:", e)

    def mark_attendance(self, csv_path: Path, student_id, course_name, confidence):
        if not csv_path.exists():
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["StudentID","Course","Date","Time","Confidence"])
        try:
            df = pd.read_csv(csv_path)
            today = datetime.now().date().isoformat()
            if ((df["StudentID"] == student_id) & (df["Date"] == today) & (df["Course"] == course_name)).any():
                print(f"[INFO] {student_id} already marked in {csv_path.name}")
                return
        except Exception:
            pass
        now = datetime.now()
        row = [student_id, course_name, now.date().isoformat(), now.time().strftime("%H:%M:%S"), confidence]
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)
        print(f"[LOG] Wrote attendance: {row}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()

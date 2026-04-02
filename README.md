# Intelligent Attendance Tracking and Analysis Platform

## 📌 Overview

The **Intelligent Attendance Tracking and Analysis Platform** is an AI-powered system designed to automate student attendance using facial recognition technology and provide advanced statistical insights through an interactive dashboard.

This system eliminates manual attendance processes, reduces errors, and enables data-driven decision-making through real-time visualization and analysis.

---

## 🚀 Features

* 🎥 **Face Recognition Attendance**

  * Automatically detects and recognizes students using computer vision.
* 📅 **Week-Based Attendance System**

  * Attendance is recorded per academic week (Week 1–15).
* 🔒 **Duplicate Prevention**

  * Ensures one attendance entry per student per week.
* 📊 **Statistical Analysis**

  * Computes mean, median, mode, variance, and standard deviation of attendance.
* 📈 **Interactive Dashboard**

  * Visualizes attendance using bar charts and pie charts.
* 👨‍🏫 **Teacher Login System**

  * Each instructor accesses only their assigned course.
* 📁 **Automatic Data Management**

  * CSV files are created and updated automatically.

---

## 🧠 Technologies Used

* **Python**

  * OpenCV (`cv2`) – webcam and image processing
  * face_recognition – facial detection and matching
  * pandas – data handling
* **R (Shiny Framework)**

  * shiny – web dashboard
  * ggplot2 – data visualization
  * dplyr – data manipulation
  * reticulate – R-Python integration

---

## ⚙️ How It Works

1. Faces are encoded using a dataset of student images.
2. The system captures real-time video via webcam.
3. Detected faces are matched against stored encodings.
4. Attendance is recorded in a CSV file for the selected week.
5. The Shiny dashboard reads the data and displays statistics and charts.

---

## 📊 Statistical Insights

The system provides:

* Mean attendance per week
* Median attendance
* Mode (most frequent attendance level)
* Variance and standard deviation
* Weekly and distribution-based visualizations

---

## 🎯 Objective

To build a **reliable, automated, and data-driven attendance system** that combines artificial intelligence with statistical analysis for improved accuracy and insights.

---

## 📌 Future Improvements

* Attendance percentage tracking
* Absence detection and alerts
* Export reports (PDF/Excel)
* Multi-class or admin dashboard support

---

## 👨‍💻 Author

Developed as part of an academic project in **Computer Science / Artificial Intelligence** with a focus on **Advanced Statistics and Machine Learning integration**.

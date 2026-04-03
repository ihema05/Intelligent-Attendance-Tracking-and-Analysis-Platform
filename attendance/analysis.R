# analysis.R
library(dplyr)
library(ggplot2)
library(readr)
library(lubridate)

# CONFIG: change path as needed
attendance_file <- "C:\Users\ibrahim kamal\projects\attendance\attendance.csv"
semester_start <- as.Date("2025-09-01") # change to your semester start date

att <- read_csv(attendance_file, col_types = cols())

# convert date/time
att <- att %>%
  mutate(Date = as_date(Date),
         Week = as.integer(floor(as.numeric(difftime(Date, semester_start, units="days")) / 7) + 1)) %>%
  filter(Week >= 1 & Week <= 15)

# Attendance count per student per week
weekly <- att %>%
  group_by(Course, StudentID, Week) %>%
  summarise(Count = n(), AvgConfidence = mean(Confidence, na.rm=TRUE), .groups="drop")

# attendance rate: how many weeks student attended at least once (out of 15)
attendance_weeks <- weekly %>%
  group_by(Course, StudentID) %>%
  summarise(WeeksAttended = n(), AvgConf = mean(AvgConfidence, na.rm=TRUE), .groups="drop") %>%
  mutate(AttendanceRate = WeeksAttended / 15)

# Plot: class-wide weekly attendance totals
class_weekly <- weekly %>%
  group_by(Course, Week) %>%
  summarise(Total = sum(Count), .groups="drop")

ggplot(class_weekly, aes(x = Week, y = Total, color = Course)) +
  geom_line(size=1.2) +
  geom_point() +
  theme_minimal() +
  labs(title="Weekly Attendance Totals (15 weeks)", x="Week", y="Total recorded presences")

# Plot: top 10 students by attendance rate per course
top_students <- attendance_weeks %>%
  group_by(Course) %>%
  arrange(desc(AttendanceRate)) %>%
  slice_head(n=10)

ggplot(top_students, aes(x = reorder(StudentID, AttendanceRate), y = AttendanceRate)) +
  geom_col() +
  facet_wrap(~Course, scales = "free_x") +
  coord_flip() +
  labs(title="Top students by attendance rate", y="Attendance Rate (0-1)", x="StudentID") +
  theme_minimal()

# Save cleaned tables for Shiny
write_csv(weekly, "weekly_attendance.csv")
write_csv(attendance_weeks, "attendance_rates.csv")





Webcam
↓
OpenCV (cv2)
↓
face_recognition
↓
encodings.pkl
↓
Python CSV (weekly attendance)
↓
R reads CSV
↓
dplyr → statistics
↓
ggplot2 → graphs
↓
Shiny → dashboard

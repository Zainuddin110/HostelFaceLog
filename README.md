# HostelFaceLog
HostelVision is a smart hostel attendance system that uses live face recognition for secure, contactless entry and exit. Register students by photo, visualize room occupancy, edit profiles, and download logs—all through a beautiful Streamlit interface.

# Hostel Face Recognition Attendance System

A modern, full-stack hostel attendance solution using face recognition. Built with **Streamlit** for the admin interface, supports local registration, room-wise visualization, live entry/exit logging, and editable student profiles.

🚀 Features

- **Live Face Recognition:** Mark entry and exit with a webcam or CCTV (RTSP/IP camera support).
- **Room-wise Visualization:** See which students are inside by room, with bar and pie charts.
- **Student Registration:** Add new students via photo upload (admin only).
- **Edit Profiles:** Admin can update student details and photos.
- **Download Logs:** Export all entry/exit logs as Excel.
- **User-friendly Dashboard:** Clean, modern interface with live metrics and charts.
- **Local SQLite Database:** All data stored securely and locally.

---

## 📦 Project Structure
├── main.py # Streamlit frontend and main app
├── database.py # SQLite database helpers
├── face_utils.py # Face recognition and processing logic
├── requirements.txt # Python package requirements
└── README.md # This file

Getting Started:
git clone https://github.com/Zainuddin110/HostelFaceLog.git
cd HostelFaceLog

python -m venv newenv(this project will only run on Python 3.11)
# Windows:
newenv\Scripts\activate
# macOS/Linux:
source newenv/bin/activate

pip install -r requirements.txt

streamlit run main.py

Database
Do not upload hostel_db.sqlite to GitHub.
The database (hostel_db.sqlite) will be created automatically on first run.
All attendance, student profiles, and logs are stored locally in this file.

Dashboard
Live stats: students inside/outside, today's entry/exit counts
Room-wise occupancy (bar chart)
Status pie chart (inside/outside)
Full logs table with Excel export

diting & Registration
Register a student by name, roll, room, and photo.
Admin can edit all fields, including photo, from the UI.

Security & Privacy
Data stays local (SQLite).
No student photos or info are uploaded to any cloud unless you do so.

Pull requests and suggestions are welcome! For major changes, please open an issue first to discuss what you would like to change.

Acknowledgements
face_recognition
Streamlit
OpenCV
Pandas

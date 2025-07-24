import os
from PIL import Image
import streamlit as st
import pandas as pd
import io
import cv2
import numpy as np
from PIL import Image
import datetime
import base64
import matplotlib.pyplot as plt
import time
import re
from collections import defaultdict
from database import *
from face_utils import *

st.set_page_config(page_title="Hostel Face Recognition", layout="wide")

# --- CSS and helpers ---
st.markdown("""
    <style>
        body { background: #181c20 !important; }
        .big-title { font-size:5.2rem; font-weight:800; color:#2563eb; margin-bottom:10px;}
        .student-card {
            background: #fff;
            border-radius: 24px;
            box-shadow: 0 4px 24px rgba(30,41,59,0.13);
            padding: 1.2rem 2rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
        }
        .student-img {
            border-radius: 15px;
            margin-right: 22px;
            border: 3px solid #e0e7ef;
            box-shadow: 0 1px 6px rgba(59,130,246,0.08);
        }
        .stDownloadButton>button {
            background: linear-gradient(90deg,#2563eb 30%,#0ea5e9 100%);
            color:white;
            border-radius: 1.2rem;
            padding: 0.7rem 1.5rem;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

def img_bytes_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode('utf-8')

init_db()

def room_sort_key(room):
    m = re.match(r"([A-Za-z]+)-(\d+)", room)
    if m:
        return (m.group(1), int(m.group(2)))
    return (room, 0)

def count_unknown_visitors_today():
    folder = "unknown_entries"
    if not os.path.exists(folder):
        return 0
    today = datetime.datetime.now().strftime("%Y%m%d")
    return len([f for f in os.listdir(folder) if f.startswith(f"visitor.{today}") and f.endswith(".jpg")])

PAGE_DICT = {
    "Dashboard": "📊 Dashboard",
    "Entry Camera": "👤 Entry",
    "Exit Camera": "🚪 Exit",
    "Register Student": "📝 Register",
    "Registered Students": "👨‍🎓 Students",
    "Logs": "🗂️ Logs",
    "Unknown Entries": "🙎🏻 Visitors"
}
PAGES = list(PAGE_DICT.keys())

st.sidebar.title("✨ Navigation")
page = st.sidebar.radio(
    "Go to",
    PAGES,
    format_func=lambda x: PAGE_DICT[x]
)

# === DASHBOARD ===
if page == "Dashboard":
    st.markdown('<div class="big-title">Hostel Dashboard</div>', unsafe_allow_html=True)
    logs = get_logs()
    df = pd.DataFrame(logs, columns=["ID", "Student ID", "Name", "Action", "Timestamp"])

    students = get_all_students()
    inside = []
    outside = []
    for s in students:
        last = get_last_action(s['id'])
        if last == "entry":
            inside.append(s['name'])
        else:
            outside.append(s['name'])

    # Optional: Calculate today's entries/exits
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    if not df.empty:
        df['date'] = pd.to_datetime(df['Timestamp']).dt.date
        entries_today = df[(df['Action'] == 'entry') & (df['date'] == datetime.date.today())].shape[0]
        exits_today = df[(df['Action'] == 'exit') & (df['date'] == datetime.date.today())].shape[0]
        visitors_today = df[(df['Action'] == 'Visitors') & (df['date'] == datetime.date.today())].shape[0]
    else:
        entries_today = 0
        exits_today = 0
        visitors_today = 0

    # Row of metrics with emojis and daily info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<span style="font-size:1.4em"><b>Students Inside</b></span>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:2.7em; font-weight:700; margin-top:-15px;">{len(inside)}</div>', unsafe_allow_html=True)
        msg = f'↑ {entries_today} entries today' if entries_today > 0 else "↑ No entries today"
        st.markdown(f'<span style="color: #16a34a; font-size:1em;">{msg}</span>', unsafe_allow_html=True)

    with col2:
        st.markdown('<span style="font-size:1.4em"><b>Students Outside</b></span>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:2.7em; font-weight:700; margin-top:-15px;">{len(outside)}</div>', unsafe_allow_html=True)
        msg = f'↑ {exits_today} exits today' if exits_today > 0 else "↑ No exits today"
        st.markdown(f'<span style="color: #16a34a; font-size:1em;">{msg}</span>', unsafe_allow_html=True)

    with col3:
        visitors_today = count_unknown_visitors_today()
        st.markdown('<span style="font-size:1.4em"><b>Visitors Detected Today</b></span>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:2.7em; font-weight:700; margin-top:-15px; color:#eab308;">{visitors_today}</div>', unsafe_allow_html=True)
        msg = f'↑ {visitors_today} visitors today' if visitors_today > 0 else "↑ No Visitors today"
        st.markdown(f'<span style="color: #eab308; font-size:1em;">{msg}</span>', unsafe_allow_html=True)


    st.markdown('<h2 style="margin-top:18px; margin-bottom:0.7em;"><span style="font-size:1.3em;">📊</span> <span style="color:#2563eb;">Current Status Distribution</span></h2>', unsafe_allow_html=True)

    # ----- PIE CHART FOR INDIDE HOSTEL AND STUDENTS INSIDE BY ROOM -----
    inside_students = [s for s in get_all_students() if s['name'] in inside]
    room_dict = defaultdict(list)
    for student in inside_students:
        room_dict[student['room']].append(student['name'])
    room_counts = {room: len(names) for room, names in room_dict.items()}

    col1, col2 = st.columns([1, 1])  # 1 for pie, 1.3 for bar

    with col1:
        st.markdown("#### Status Pie Chart")
        sizes = [len(outside), len(inside)]
        colors = ['#ef4444', '#22c55e']
        if sum(sizes) == 0:
            st.info("No students inside or outside yet.")
        else:
            fig, ax = plt.subplots(figsize=(8, 8))
            wedges, texts, autotexts = ax.pie(
                sizes,
                colors=colors,
                autopct='%1.0f%%',
                startangle=120,
                wedgeprops={'edgecolor': 'white', 'linewidth': 0},
                pctdistance=0.67
            )
            centre_circle = plt.Circle((0, 0), 0.50, fc='#181c20', zorder=10)
            fig.gca().add_artist(centre_circle)
            plt.setp(texts, color='#333', weight='bold')
            plt.setp(autotexts, color='#fff', weight='bold', fontsize=20)
            ax.set(aspect="equal")
            fig.patch.set_facecolor('none')
            st.pyplot(fig)

    with col2:
        st.subheader("Student Status Table")
        status_df = pd.DataFrame({
            "id": [s['id'] for s in students],
            "Name": [s['name'] for s in students],
            "Room": [s['room'] for s in students],
            "Status": [("Inside" if s['name'] in inside else "Outside") for s in students]
        })
        def color_status(val):
            color = '#22c55e' if val == 'Inside' else '#ef4444'
            return f'background-color: {color}; color: #fff'
        
        status_df = status_df.reset_index(drop=True)

        # Show color table if possible
        try:
            st.dataframe(status_df.style.map(color_status, subset=['Status']))
        except Exception:
            st.dataframe(status_df)

    # --- Student Status Table & Room Occupancy Donut Chart Side by Side ---
    colA, colB = st.columns([1, 1])  # 1 for pie, 1.3 for bar

    with colA:
        st.subheader("Room Occupancy Pie Chart")
        if not inside_students:
            st.info("No students are currently inside any room.")
        else:
            room_counts = {room: len(names) for room, names in room_dict.items()}
            labels = list(room_counts.keys())
            sizes = list(room_counts.values())
            colors = plt.cm.Paired(np.arange(len(labels)))
            
            def label_formatter(pct, allvals):
                absolute = int(round(pct/100.*np.sum(allvals)))
                i = label_formatter.idx
                label = labels[i]
                label_formatter.idx += 1
                return f"{label}\n{pct:.1f}%"
            label_formatter.idx = 0

            fig, ax = plt.subplots(figsize=(8, 8))
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=None,  # We'll show in autopct!
                colors=colors,
                autopct=lambda pct: label_formatter(pct, sizes),
                startangle=120,
                wedgeprops={'edgecolor': 'white', 'linewidth': 0},
                pctdistance=0.72
            )
            label_formatter.idx = 0  # reset for redraws
            centre_circle = plt.Circle((0, 0), 0.50, fc='#181c20', zorder=10)
            fig.gca().add_artist(centre_circle)
            plt.setp(texts, color='#333', weight='bold')
            plt.setp(autotexts, color='#fff', weight='bold', fontsize=20)
            ax.set(aspect="equal")
            fig.patch.set_facecolor('none')
            st.pyplot(fig)

            st.markdown("#### Detailed Room Occupancy")
            for room, names in sorted(room_dict.items()):
                st.markdown(
                    f"<b>Room <span style='color:#3b82f6'>{room}</span>:</b> "
                    + ", ".join(f"<span style='color:#16a34a'>{n}</span>" for n in names),
                    unsafe_allow_html=True
                )

    with colB:
        st.markdown('<h3 style="margin-top:1.5em; color:#22c55e;">Students Currently Inside By Room</h3>', unsafe_allow_html=True)
        if not inside_students:
            st.info("No students are currently inside.")
        else:
            st.markdown("#### Roomwise Students Inside")
            room_df = pd.DataFrame(list(room_counts.items()), columns=["Room", "Students Inside"])
            st.bar_chart(room_df.set_index("Room"))


# === ENTRY CAMERA (Continuous) ===
elif page == "Entry Camera":
    st.markdown('<div class="big-title">Entry Camera</div>', unsafe_allow_html=True)
    if 'entry_camera_on' not in st.session_state:
        st.session_state.entry_camera_on = False
    if 'entry_logged_ids' not in st.session_state:
        st.session_state.entry_logged_ids = set()

    start = st.button("Start Entry Camera")
    stop = st.button("Stop Entry Camera")

    # --- Placeholder for messages ABOVE the video ---
    message_placeholder = st.empty()
    img_placeholder = st.empty()

    if start:
        st.session_state.entry_camera_on = True
        st.session_state.entry_logged_ids = set()
    if stop:
        st.session_state.entry_camera_on = False

    if st.session_state.entry_camera_on:
        cap = cv2.VideoCapture(0)
        while st.session_state.entry_camera_on:
            ret, frame = cap.read()
            if not ret:
                break
            frame_display = frame.copy()
            boxes = detect_faces_mediapipe(frame)
            known_students = get_all_students()
            # -- Clear message before every frame --
            status_msg = ""
            for box in boxes:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame_display, (x1, y1), (x2, y2), (0,200,83), 2)
                encoding = encode_face(frame, box)
                if encoding is not None:
                    sid, sname = recognize_face(encoding, known_students)
                    if sid and (sid not in st.session_state.entry_logged_ids):
                        add_log(sid, sname, "entry")
                        st.session_state.entry_logged_ids.add(sid)
                        status_msg = f"✅ <b>{sname}</b> has ENTERED Hostel at {datetime.datetime.now().strftime('%H:%M:%S')}"
                    elif sid is None:
                        # Unknown face detected
                        status_msg = "<span style='color:#eab308'>⚠️ Unknown person detected!</span>"
                        # Optional: Save snapshot of unknown face (uncomment if you want this)
                        face_img = frame[y1:y2, x1:x2]
                        import os
                        if not os.path.exists("unknown_entries"):
                            os.makedirs("unknown_entries")
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            cv2.imwrite(f"unknown_entries/visitor.{timestamp}.jpg", face_img)
            # --- Set the message above the live feed ---
            if status_msg:
                message_placeholder.markdown(f'<div style="font-size:1.5em; color:#16a34a;">{status_msg}</div>', unsafe_allow_html=True)
            img_placeholder.image(frame_display, channels='BGR', caption="Live Camera Frame")
            time.sleep(0.1)
            if not st.session_state.entry_camera_on:
                break
        cap.release()

# === EXIT CAMERA (Continuous) ===
elif page == "Exit Camera":
    st.markdown('<div class="big-title">Exit Camera</div>', unsafe_allow_html=True)
    if 'exit_camera_on' not in st.session_state:
        st.session_state.exit_camera_on = False
    if 'exit_logged_ids' not in st.session_state:
        st.session_state.exit_logged_ids = set()

    start = st.button("Start Exit Camera")
    stop = st.button("Stop Exit Camera")

    # --- Placeholder for messages ABOVE the video ---
    message_placeholder = st.empty()
    img_placeholder = st.empty()

    if start:
        st.session_state.exit_camera_on = True
        st.session_state.exit_logged_ids = set()
    if stop:
        st.session_state.exit_camera_on = False

    if st.session_state.exit_camera_on:
        cap = cv2.VideoCapture(0)
        while st.session_state.exit_camera_on:
            ret, frame = cap.read()
            if not ret:
                break
            frame_display = frame.copy()
            boxes = detect_faces_mediapipe(frame)
            known_students = get_all_students()
            status_msg = ""
            for box in boxes:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame_display, (x1, y1), (x2, y2), (200, 0, 30), 2)  # red rectangle for EXIT
                encoding = encode_face(frame, box)
                if encoding is not None:
                    sid, sname = recognize_face(encoding, known_students)
                    if sid and (sid not in st.session_state.exit_logged_ids):
                        add_log(sid, sname, "exit")
                        st.session_state.exit_logged_ids.add(sid)
                        status_msg = f"🚪 <b>{sname}</b> has EXITED Hostel at {datetime.datetime.now().strftime('%H:%M:%S')}"
                    elif sid is None:
                        # Unknown face detected
                        status_msg = "<span style='color:#eab308'>⚠️ Unknown person detected!</span>"
                        face_img = frame[y1:y2, x1:x2]
                        import os
                        if not os.path.exists("unknown_entries"):
                            os.makedirs("unknown_entries")
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        cv2.imwrite(f"unknown_entries/visitor_exit.{timestamp}.jpg", face_img)
            # --- Set the message above the live feed ---
            if status_msg:
                message_placeholder.markdown(
                    f'<div style="font-size:1.5em; color:#ef4444;">{status_msg}</div>',
                    unsafe_allow_html=True
                )
            img_placeholder.image(frame_display, channels='BGR', caption="Live Camera Frame")
            time.sleep(0.1)
            if not st.session_state.exit_camera_on:
                break
        cap.release()

# === REGISTER STUDENT ===
elif page == "Register Student":
    st.markdown('<div class="big-title">Register New Student </div>', unsafe_allow_html=True)
    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    room = st.text_input("Room Number")
    uploaded_img = st.file_uploader("Upload Student Photo (face only)", type=["jpg", "jpeg", "png"])

    if st.button("Register Student"):
        if not (name and roll and room and uploaded_img):
            st.warning("Please fill all details and upload a photo.")
        else:
            img_bytes = uploaded_img.read()
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img_np = np.array(image)
            st.image(image, caption="Uploaded Photo", width=200)

            encoding = encode_face_pil(img_np)
            if encoding is not None:
                add_student(name, roll, room, encoding, img_bytes)
                st.success("Student registered successfully! 🎉")
            else:
                st.error("No recognizable face found in the image. Try another photo.")

# === REGISTERED STUDENTS (EDITABLE) ===
elif page == "Registered Students":
    st.markdown('<div class="big-title">Registered Students</div>', unsafe_allow_html=True)
    students = get_all_students()
    if not students:
        st.info("No students registered yet.")
    else:
        # Group students by room and sort
        from collections import defaultdict
        room_dict = defaultdict(list)
        for s in students:
            room_dict[s['room']].append(s)
        # Sort rooms as A-101, A-102, B-101, etc.
        for i, (room, students_in_room) in enumerate(sorted(room_dict.items(), key=lambda x: room_sort_key(x[0]))):
            if i > 0:
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#3b82f6;'>Room {room}</h4>", unsafe_allow_html=True)
            # Sort students in room by name (optional)
            for s in sorted(students_in_room, key=lambda x: x['id']):
                with st.expander(f"{s['name']} (Roll {s['roll']})"):
                    img_data = img_bytes_to_base64(s['image']) if s.get('image') else ''
                    st.image(f"data:image/jpeg;base64,{img_data}", width=120)
                    with st.form(f"edit_{s['id']}"):
                        name = st.text_input("Name", value=s['name'])
                        roll = st.text_input("Roll", value=s['roll'])
                        room_new = st.text_input("Room", value=s['room'])
                        new_img = st.file_uploader("Change Photo", type=["jpg", "jpeg", "png"])
                        submit = st.form_submit_button("Save Changes")
                        if submit:
                            image_bytes = new_img.read() if new_img else None
                            update_student(s['id'], name, roll, room_new, image_bytes)
                            st.success("Profile updated! Refresh to see changes.")

# === LOGS ===
elif page == "Logs":
    st.markdown('<div class="big-title">All Logs</div>', unsafe_allow_html=True)
    logs = get_logs()
    df = pd.DataFrame(logs, columns=["ID", "Student ID", "Name", "Action", "Timestamp"])
    st.dataframe(df, use_container_width=True)
    st.write("Download all logs as Excel:")
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    st.download_button("Download Logs as Excel", excel_buffer, "hostel_logs.xlsx")

#==UNKNOWN ENTRIES==
elif page == "Unknown Entries":
    st.markdown('<div class="big-title">Visitors</div>', unsafe_allow_html=True)
    unknown_folder = "unknown_entries"

    if os.path.exists(unknown_folder) and os.listdir(unknown_folder):
        unknown_files = sorted(os.listdir(unknown_folder), reverse=True)[:30]  # Show latest 30
        cols = st.columns(5)
        for i, filename in enumerate(unknown_files):
            with cols[i % 5]:
                img_path = os.path.join(unknown_folder, filename)
                img = Image.open(img_path)
                st.image(img, caption=filename, width=110)
                # Optional: Show a delete button for admin
                if st.button(f"Delete {filename}", key=f"del_{filename}"):
                    os.remove(img_path)
    else:
        st.info("No unknown faces detected yet.")

st.sidebar.markdown("""
    <hr style='margin:1.2em 0 0.5em 0; border: none; border-top: 2px solid #3b82f6;'>
    <div style='color: #6ee7b7; text-align:center; font-size:1.08em; font-weight:600; margin-top:0.6em; letter-spacing:1px;'>
        Made by <span style="color:#3b82f6;"><b>Zainuddin</b></span> <br>
        <span style="font-size:0.97em; color:#64748b;">2025</span>
    </div>
""", unsafe_allow_html=True)

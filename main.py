import speech_recognition as sr
from translate import Translator
import pyttsx3
import time
import cv2
import mediapipe as mp
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
import poses
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtGui import QPixmap

#stosujemy pyqt6 do gui

app = QApplication([])

window = QWidget()

window.setStyleSheet("""
QWidget {
    background-color: #121212;
    color: white;
    font-family: Arial;
}

QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #00d4ff;
}

QLabel#status {
    font-size: 16px;
    padding: 10px;
    border-radius: 10px;
}

QPushButton {
    background-color: #1f1f1f;
    border: 1px solid #333;
    padding: 10px;
    border-radius: 10px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #2a2a2a;
    border: 1px solid #00d4ff;
}

QPushButton:pressed {
    background-color: #00d4ff;
    color: black;
}
""")



window.setWindowTitle("Personalny Trener Yogi")
window.resize(400, 300)

layout = QVBoxLayout()

title = QLabel("Personalny Trener Yogi")
title.setAlignment(Qt.AlignmentFlag.AlignCenter)
title.setStyleSheet("font-size: 18px; font-weight: bold;")


title.setObjectName("title")
status_label = QLabel("Status: STOP")
status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
status_label.setStyleSheet("font-size: 14px; color: red;")
status_label.setObjectName("status")


start_button = QPushButton("Start treningu")
start_button.setStyleSheet("padding: 10px; font-size: 14px;")

stop_button = QPushButton("Zatrzymaj")
stop_button.setStyleSheet("padding: 10px; font-size: 14px;")

layout.addWidget(title)
layout.addSpacing(20)
layout.addWidget(status_label)
layout.addSpacing(20)
layout.addWidget(start_button)
layout.addWidget(stop_button)


layout.setContentsMargins(20, 20, 20, 20)
layout.setSpacing(15)


# info_box = QLabel("📌 Wskazówki pojawią się tutaj")
# info_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
# info_box.setStyleSheet("""
#     background-color: #1e1e1e;
#     padding: 10px;
#     border-radius: 10px;
#     border: 1px solid #333;
# """)

window.setLayout(layout)

button_layout = QHBoxLayout()
button_layout.addWidget(start_button)
button_layout.addWidget(stop_button)

layout.addLayout(button_layout)
# layout.addWidget(info_box)

pose_images = {
    "Cow Pose": "poses/cow_pose.jpeg",
    "Cat Pose": "poses/cat_pose.jpg",
    "Downward Facing Dog": "poses/downard_facing_pose.jpeg",
    "Upward Facing Dog": "poses_images/upward.jpg",
    "Child Pose": "poses_images/child.jpg"
}

image_label = QLabel()
layout.addWidget(image_label)

def update_pose_image(pose_name):
    path = pose_images.get(pose_name)
    if path:
        pixmap = QPixmap(path)
        image_label.setPixmap(pixmap.scaled(250, 250))


running = False
last_pose_change_time = None
def start_training():
    global running, last_pose_change_time, current_pose_index, is_changing_pose

    running = True
    current_pose_index = 0
    is_changing_pose = False
    last_pose_change_time = time.time()

    status_label.setText("Status: START")
    status_label.setStyleSheet("font-size: 14px; color: green;")

def stop_training():
    global running
    running = False
    status_label.setText("Status: STOP")
    status_label.setStyleSheet("font-size: 14px; color: red;")
    # say_and_print("Zatrzymano trening")
    exit(1)

start_button.clicked.connect(start_training)
stop_button.clicked.connect(stop_training)

window.show()

engine = pyttsx3.init()


#mowa - pomocnicza
def speak(text):
    engine.say(text)
    engine.runAndWait()
    time.sleep(1)

#mowa i tekst
def say_and_print(text):
    print(text)
    speak(text)

#poprawnosc Cow Pose
def check_cow_pose(landmarks):
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    l_wr = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    head_up = nose.y < l_sh.y
    back_alignment = abs(l_sh.y - l_hip.y) < 0.15
    arms_vertical = abs(l_sh.x - l_wr.x) < 0.1
    legs_vertical = abs(l_hip.x - l_knee.x) < 0.1
    return head_up and back_alignment and arms_vertical and legs_vertical


def overlay_image(background, overlay, x=10, y=10, scale=0.4):
    overlay = cv2.resize(overlay, (0, 0), fx=scale, fy=scale)

    h, w = overlay.shape[:2]

    if y + h > background.shape[0] or x + w > background.shape[1]:
        return background

    roi = background[y:y+h, x:x+w]

    # jeśli PNG ma alpha
    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            roi[:, :, c] = (1 - alpha) * roi[:, :, c] + alpha * overlay[:, :, c]
    else:
        roi[:] = overlay

    background[y:y+h, x:x+w] = roi
    return background

#rozpoznawanie glosu
def recognise():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        time.sleep(0.5)
        audio = r.listen(source)
        try:
            recognised_text = r.recognize_google(audio, language='pl-PL')
            say_and_print("Powiedziałeś: " + recognised_text)
            return recognised_text.lower()
        except sr.UnknownValueError:
            say_and_print("Nie zrozumiałem")
            return None
        except sr.RequestError as e:
            say_and_print("Błąd rozpoznawania")
            print(e)
            return None

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
pose = mp_pose.Pose()

pose_list = ["Cow Pose", "Cat Pose", "Downward Facing Dog", "Upward Facing Dog", "Child Pose"]
current_pose_index = 0
pose_time = 20
change_pose_timeout = 8
is_changing_pose = False
last_pose_change_time = None

change_remaining = 0
while cap.isOpened():
    app.processEvents()
    if not running:
        continue
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    gesture = pose_list[current_pose_index]

    img_path = pose_images.get(gesture)

    if img_path:
        img_path = pose_images.get(gesture)

        if img_path:
            ref_img = cv2.imread(img_path)

            if ref_img is not None:
                h, w = frame.shape[:2]

                scale = 2.0

                ref_img = cv2.resize(ref_img, (0, 0), fx=scale, fy=scale)

                img_h, img_w = ref_img.shape[:2]

                x = w - img_w - 20
                y = 20

                frame = overlay_image(frame, ref_img, x=x, y=y, scale=1.0)

    elapsed_time = time.time() - last_pose_change_time

    remaining_time = int(pose_time - elapsed_time)

    if elapsed_time >= pose_time and not is_changing_pose:
        is_changing_pose = True
        change_pose_start_time = time.time()
        # say_and_print(f"Przygotuj sie. Nastepna poza: {pose_list[(current_pose_index + 1) % len(pose_list)]}")

    if last_pose_change_time is None:
        elapsed_time = 0
    else:
        elapsed_time = time.time() - last_pose_change_time

    if is_changing_pose:
        change_remaining = int(change_pose_timeout - (time.time() - change_pose_start_time))

        if change_remaining <= 0:
            current_pose_index = (current_pose_index + 1) % len(pose_list)
            last_pose_change_time = time.time()
            is_changing_pose = False
            # say_and_print(f"Start pozy: {pose_list[current_pose_index]}")

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        l_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        r_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        l_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
        r_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
        l_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        r_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        r_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

        #poprawnosc pozy
        is_correct = False

        if gesture == "Cow Pose":
            is_correct = check_cow_pose(landmarks)
        elif gesture == "Cat Pose":
            is_correct = poses.cat_pose(landmarks, mp_pose)

        #rysowanie
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )
        color = (0, 255, 0) if is_correct else (0, 0, 255)
        msg = "POZYCJA POPRAWNA" if is_correct else "POPRAW SIE"

        cv2.putText(frame, msg, (30, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 8)
        cv2.putText(frame, msg, (30, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    color, 3)

    next_pose_index = (current_pose_index + 1) % len(pose_list)
    next_pose = pose_list[next_pose_index]

    if not is_changing_pose:
        change_remaining = 0
    #tekst
    if is_changing_pose:
        time_text = "Zmien poze w ciagu: " + str(change_remaining) + " s"
    else:
        time_text = "Pozostaly czas: " + str(max(0, remaining_time)) + " s"

    cv2.putText(frame, f"Aktualna Poza: {gesture}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 8)
    cv2.putText(frame, f"Nastepna poza: {next_pose}", (30, 210),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 8)
    cv2.putText(frame, f"Aktualna Poza: {gesture}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 105, 180), 4)
    cv2.putText(frame, time_text, (30, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 8)
    cv2.putText(frame, time_text, (30, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (186, 85, 211), 3)
    cv2.putText(frame, f"Nastepna poza: {next_pose}", (30, 210),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 191, 255), 3)
    cv2.imshow("Kamera", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

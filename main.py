import speech_recognition as sr
import pyttsx3
import time
import cv2
import mediapipe as mp
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
import poses  # Importujemy Twój plik z logiką pozycji

# --- KONFIGURACJA GŁOSU ---
engine = pyttsx3.init()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def say_and_print(text):
    print(text)
    speak(text)


# --- KONFIGURACJA MEDIAPIPE ---
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose_detector = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# --- GUI PyQt6 ---
app = QApplication([])
window = QWidget()
window.setWindowTitle("Personalny Trener Yogi")
window.resize(400, 300)

layout = QVBoxLayout()
title = QLabel("Personalny Trener Yogi")
title.setAlignment(Qt.AlignmentFlag.AlignCenter)
title.setStyleSheet("font-size: 18px; font-weight: bold;")

status_label = QLabel("Status: STOP")
status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
status_label.setStyleSheet("font-size: 14px; color: red;")

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
window.setLayout(layout)

# --- LOGIKA STEROWANIA ---
running = False


def start_training():
    global running, last_pose_change_time
    running = True
    last_pose_change_time = time.time()
    status_label.setText("Status: START")
    status_label.setStyleSheet("font-size: 14px; color: green;")
    say_and_print("Rozpoczynamy trening. Pierwsza pozycja: Cow Pose")


def stop_training():
    global running
    running = False
    status_label.setText("Status: STOP")
    status_label.setStyleSheet("font-size: 14px; color: red;")
    say_and_print("Zakończono trening")
    exit(0)


start_button.clicked.connect(start_training)
stop_button.clicked.connect(stop_training)

window.show()

# --- PĘTLA GŁÓWNA TRENERA ---
cap = cv2.VideoCapture(0)
pose_list = ["Cow Pose", "Cat Pose", "Downward Facing Dog", "Upward Facing Dog", "Child Pose"]
current_pose_index = 0
pose_time = 20  # Czas trwania jednej pozycji w sekundach
last_pose_change_time = time.time()

while cap.isOpened():
    # Obsługa zdarzeń GUI (żeby przyciski działały w trakcie pętli)
    app.processEvents()

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    if running:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose_detector.process(rgb)

        gesture = pose_list[current_pose_index]
        is_correct = False

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # 1. Sprawdzanie pozycji przy użyciu pliku poses.py
            if gesture == "Cow Pose":
                is_correct = poses.cow_pose(landmarks, mp_pose)
            elif gesture == "Cat Pose":
                is_correct = poses.cat_pose(landmarks, mp_pose)
            elif gesture == "Downward Facing Dog":
                is_correct = poses.downward_facing_pose(landmarks, mp_pose)
            elif gesture == "Upward Facing Dog":
                is_correct = poses.upward_facing_pose(landmarks, mp_pose)
            elif gesture == "Child Pose":
                is_correct = poses.child_facing_pose(landmarks, mp_pose)

            # 2. Rysowanie szkieletu na obrazie
            mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

            # 3. Wyświetlanie informacji o poprawności
            color = (0, 255, 0) if is_correct else (0, 0, 255)
            msg = "POZYCJA OK!" if is_correct else "POPRAW SIE"
            cv2.putText(frame, msg, (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

        # 4. Logika czasu i zmiany pozycji
        elapsed = time.time() - last_pose_change_time
        remaining = int(pose_time - elapsed)

        if elapsed > pose_time:
            current_pose_index = (current_pose_index + 1) % len(pose_list)
            last_pose_change_time = time.time()
            say_and_print(f"Czas na {pose_list[current_pose_index]}")

        # 5. UI na obrazie kamery
        cv2.putText(frame, f"Poza: {gesture}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (151, 33, 64), 3)
        cv2.putText(frame, f"Czas: {remaining}s", (30, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Trener Yogi", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Wyjście przez ESC
        break

cap.release()
cv2.destroyAllWindows()
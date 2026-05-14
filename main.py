import speech_recognition as sr
import pyttsx3
import time
import cv2
import mediapipe as mp
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

# --- KONFIGURACJA MEDIAPIPE ---
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# --- KONFIGURACJA GŁOSU ---
engine = pyttsx3.init()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def say_and_print(text):
    print(text)
    speak(text)


# --- LOGIKA POZ (COW POSE) ---
def check_cow_pose(landmarks):
    # Punkty kluczowe (używamy lewej strony ciała - zał. ustawienie bokiem)
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    l_wr = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    # 1. Głowa uniesiona (nos powyżej linii barków)
    head_up = nose.y < l_sh.y

    # 2. Plecy wklęsłe (uproszczenie: bark i biodro w podobnej linii poziomej)
    back_alignment = abs(l_sh.y - l_hip.y) < 0.15

    # 3. Ramiona proste pod barkami (pionowa linia X)
    arms_vertical = abs(l_sh.x - l_wr.x) < 0.1

    # 4. Uda pionowo (biodro nad kolanem)
    legs_vertical = abs(l_hip.x - l_knee.x) < 0.1

    return head_up and back_alignment and arms_vertical and legs_vertical


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
stop_button = QPushButton("Zatrzymaj")

layout.addWidget(title)
layout.addSpacing(20)
layout.addWidget(status_label)
layout.addSpacing(20)
layout.addWidget(start_button)
layout.addWidget(stop_button)
window.setLayout(layout)

running = False


def start_training():
    global running
    running = True
    status_label.setText("Status: START")
    status_label.setStyleSheet("font-size: 14px; color: green;")
    print("Rozpoczynam trening")


def stop_training():
    global running
    running = False
    status_label.setText("Status: STOP")
    status_label.setStyleSheet("font-size: 14px; color: red;")
    exit(0)


start_button.clicked.connect(start_training)
stop_button.clicked.connect(stop_training)

window.show()

# --- PĘTLA GŁÓWNA ---
cap = cv2.VideoCapture(0)
pose_list = ["Cow Pose", "Cat Pose", "Downward Dog"]
current_pose_index = 0
last_pose_change_time = time.time()
pose_duration = 15  # sekundy na każdą pozę

while cap.isOpened():
    app.processEvents()  # Obsługa przycisków GUI

    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)

    if running:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        current_gesture = pose_list[current_pose_index]
        is_correct = False

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Sprawdzanie konkretnej pozy
            if current_gesture == "Cow Pose":
                is_correct = check_cow_pose(landmarks)

            # Rysowanie szkieletu
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Feedback wizualny
            color = (0, 255, 0) if is_correct else (0, 0, 255)
            msg = "POZYCJA POPRAWNA" if is_correct else "POPRAW SIE"
            cv2.putText(frame, msg, (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Wyświetlanie aktualnej pozy i czasu
        cv2.putText(frame, f"Poza: {current_gesture}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

        # Logika zmiany pozy
        if time.time() - last_pose_change_time > pose_duration:
            current_pose_index = (current_pose_index + 1) % len(pose_list)
            last_pose_change_time = time.time()
            say_and_print(f"Zmień pozę na: {pose_list[current_pose_index]}")

    cv2.imshow("Kamera Trenera", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
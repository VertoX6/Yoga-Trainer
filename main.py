import speech_recognition as sr
from translate import Translator
import pyttsx3
import time
import cv2
import mediapipe as mp
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
import poses
#stosujemy pyqt6 do gui

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

running = False
last_pose_change_time = None
def start_training():
    global running, last_pose_change_time
    running = True
    last_pose_change_time = time.time()
    status_label.setText("Status: START")
    status_label.setStyleSheet("font-size: 14px; color: green;")
    # say_and_print("Rozpoczynam trening")

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

    if last_pose_change_time is None:
        elapsed_time = 0
    else:
        elapsed_time = time.time() - last_pose_change_time

    remaining_time = int(pose_time - elapsed_time)

    if elapsed_time >= pose_time and not is_changing_pose:
        is_changing_pose = True
        change_pose_start_time = time.time()
        # say_and_print(f"Przygotuj sie. Nastepna poza: {pose_list[(current_pose_index + 1) % len(pose_list)]}")

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
        elif gesture == "Downward Facing Dog":
            is_correct = poses.downward_facing_pose(landmarks, mp_pose)
        elif gesture == "Upward Facing Dog":
            is_correct = poses.upward_facing_pose(landmarks, mp_pose)
        elif gesture == "Child Pose":
            is_correct = poses.child_facing_pose(landmarks, mp_pose)

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
    pose_image_list = ["./cow_pose.png", "./cat_pose.png", "./downward_dog.png", "./upward_dog.png", "./child_pose.png"]

    # wybor obrazka
    if is_changing_pose:
        image_index = next_pose_index
    else:
        image_index = current_pose_index

    pose_image = cv2.imread(pose_image_list[image_index])
    if pose_image is not None:
        image_width = 200
        image_height = 150
        pose_image = cv2.resize(pose_image, (image_width, image_height))
        h, w, _ = frame.shape
        padding_right = 30
        x = w - image_width - padding_right
        frame[50:50+image_height, x:x+image_width] = pose_image

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
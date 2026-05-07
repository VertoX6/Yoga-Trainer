import speech_recognition as sr
from translate import Translator
import pyttsx3
import time
import cv2
import mediapipe as mp
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
#stosujemy pyqt6 do gui

app = QApplication([])

window = QWidget()
window.setWindowTitle("Personalny Trener Yogi")
window.resize(400, 300)

start_button = QPushButton("Start treningu", parent=window)
start_button.setGeometry(100, 80, 200, 40)

stop_button = QPushButton("Zatrzymaj", parent=window)
stop_button.setGeometry(100, 140, 200, 40)

status_button = QPushButton("Status: STOP", parent=window)
status_button.setGeometry(100, 200, 200, 40)
status_button.setEnabled(False)

running = False

def start_training():
    global running
    running = True
    status_button.setText("Status: START")
    say_and_print("Rozpoczynam trening")

def stop_training():
    global running
    running = False
    status_button.setText("Status: STOP")
    say_and_print("Zatrzymano trening")

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

#rozpoznawanie głosu
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

say_and_print("Witaj w personalnym trenerze yogi")

say_and_print("Co chcesz zrobić?")

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

    gesture = "?"

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        l_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        r_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        l_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
        r_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
        l_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        r_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        r_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

        #rysowanie szkieletu
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    cv2.putText(frame, f"Poza: {gesture}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow("Kamera", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()


#command = recognise()
#say_and_print("ej")
#text = recognise()

# mp_pose = mp.solutions.pose
# mp_drawing = mp.solutions.drawing_utils
#
# def is_horizontal(y1, y2, tol=0.05):
#     return abs(y1 - y2) < tol
#
# def is_above(p1, p2):
#     return p1.y < p2.y
#
# def is_below(p1, p2):
#     return p1.y > p2.y
#
# def is_vertical(x1, x2, tol=0.05):
#     return abs(x1 - x2) < tol
#
# # --- gesty ---
# def is_T(l_sh, l_el, l_wr, r_sh, r_el, r_wr):
#     return (
#         is_horizontal(l_sh.y, l_el.y) and
#         is_horizontal(l_el.y, l_wr.y) and
#         is_horizontal(r_sh.y, r_el.y) and
#         is_horizontal(r_el.y, r_wr.y)
#     )
#
# def is_I(l_sh, l_wr, r_sh, r_wr):
#     return (
#         is_below(l_wr, l_sh) and
#         is_below(r_wr, r_sh)
#     )
#
# def is_Y(l_sh, l_wr, r_sh, r_wr):
#     return (
#         is_above(l_wr, l_sh) and
#         is_above(r_wr, r_sh)
#     )
#
# def is_L(l_sh, l_wr, r_sh, r_wr):
#     prawa_gora = is_above(r_wr, r_sh)
#     lewa_poziom = is_horizontal(l_sh.y, l_wr.y)
#     return prawa_gora and lewa_poziom
#
# def is_P(l_wr, l_sh, r_wr, nose, r_ear, tol=0.05):
#     left_down = l_wr.y > l_sh.y + 0.05
#     near_head_x = abs(r_wr.x - r_ear.x) < tol
#     near_head_y = abs(r_wr.y - r_ear.y) < tol
#     right_near_head = near_head_x and near_head_y
#     return left_down and right_near_head
#
# def is_K(l_sh, l_wr, r_sh, r_wr):
#     return (
#         is_above(l_wr, l_sh) and
#         is_below(r_wr, r_sh)
#         and is_above(l_wr, l_sh) and is_below(r_wr, r_sh)
#         and is_vertical(l_wr.x, r_wr.x)
#     )
#
#
# cap = cv2.VideoCapture(0)
# pose = mp_pose.Pose()
#
# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#
#     frame = cv2.flip(frame, 1)
#
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = pose.process(rgb)
#
#     gesture = "?"
#
#     if results.pose_landmarks:
#         landmarks = results.pose_landmarks.landmark
#
#         l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
#         r_sh = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
#         l_el = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
#         r_el = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
#         l_wr = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
#         r_wr = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
#         r_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
#
#         nose = landmarks[mp_pose.PoseLandmark.NOSE]
#         r_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR]
#         l_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR]
#         r_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
#         l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
#
#         # --- rozpoznawanie gestów ---
#         if is_T(l_sh, l_el, l_wr, r_sh, r_el, r_wr):
#             gesture = "T"
#         elif is_Y(l_sh, l_wr, r_sh, r_wr):
#             gesture = "Y"
#         elif is_I(l_sh, l_wr, r_sh, r_wr):
#             gesture = "I"
#         elif is_L(l_sh, l_wr, r_sh, r_wr):
#             gesture = "L"
#         elif is_K(l_sh, l_wr, r_sh, r_wr):
#             gesture = "K"
#         elif is_P(l_wr, l_sh, r_wr, nose, r_ear):
#             gesture = "P"
#
#         mp_drawing.draw_landmarks(
#             frame,
#             results.pose_landmarks,
#             mp_pose.POSE_CONNECTIONS
#         )
#
#     cv2.putText(frame, f"Litera: {gesture}", (30, 60),
#                 cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
#
#     cv2.imshow("Kamera", frame)
#
#     if cv2.waitKey(1) & 0xFF == 27:
#         break
#
# cap.release()
# cv2.destroyAllWindows()
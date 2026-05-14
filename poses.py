import numpy as np


def calculate_angle(a, b, c):
    """Oblicza kąt w stopniach między trzema punktami (b jest wierzchołkiem)."""
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle


def cow_pose(landmarks, mp_pose):
    # Głowa w górę, plecy w dół, kąt w biodrach ok. 90 stopni
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    hip_angle = calculate_angle(l_sh, l_hip, l_knee)
    return 70 < hip_angle < 110 and nose.y < l_sh.y


def cat_pose(landmarks, mp_pose):
    # Głowa w dół, plecy wygięte w górę (koci grzbiet)
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    hip_angle = calculate_angle(l_sh, l_hip, l_knee)
    # W kocie głowa jest wyraźnie niżej niż linia barków
    return 70 < hip_angle < 110 and nose.y > l_sh.y


def downward_facing_pose(landmarks, mp_pose):
    # Odwrócone "V" - biodra są najwyższym punktem ciała
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_wr = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    l_ank = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]

    # Biodra muszą być powyżej barków i kostek (pamiętaj: mniejszy y = wyżej na ekranie)
    is_v_shape = l_hip.y < l_sh.y and l_hip.y < l_ank.y
    # Kąt w biodrze powinien być ostry
    hip_angle = calculate_angle(l_sh, l_hip, l_ank)

    return is_v_shape and 40 < hip_angle < 90


def upward_facing_pose(landmarks, mp_pose):
    # Klatka piersiowa w górę, nogi proste na ziemi, biodra nisko
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_wr = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]

    # Ramiona wyprostowane (kąt w łokciu ok 180)
    # Głowa wysoko nad biodrami
    chest_up = l_sh.y < l_hip.y
    straight_legs = calculate_angle(l_hip, l_knee, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]) > 150

    return chest_up and straight_legs and l_wr.y > l_sh.y


def child_facing_pose(landmarks, mp_pose):
    # Klatka piersiowa na udach, czoło przy ziemi, biodra na piętach
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]

    # Bardzo ostry kąt w kolanie (biodra na piętach)
    knee_angle = calculate_angle(l_hip, l_knee, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE])
    # Barki bardzo nisko, blisko bioder w osi pionowej
    compact = abs(l_sh.y - l_knee.y) < 0.2

    return knee_angle < 60 and compact
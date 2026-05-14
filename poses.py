import numpy as np


def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle


def cow_pose(landmarks, mp_pose):
    # Punkty potrzebne do analizy (widok z boku)
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    l_wr = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    # 1. Sprawdzenie kąta w biodrze (powinien być bliski 90 stopni)
    # Wykorzystujemy biodro jako wierzchołek między barkiem a kolanem
    hip_angle = calculate_angle(l_sh, l_hip, l_knee)

    # 2. Czy głowa jest uniesiona? (Nose.y powinno być mniejsze niż Shoulder.y)
    head_up = nose.y < l_sh.y

    # 3. Czy ramiona są proste? (Kąt w łokciu - opcjonalnie, lub relacja X bark-nadgarstek)
    # Sprawdzamy czy nadgarstek jest mniej więcej pod barkiem
    arms_aligned = abs(l_sh.x - l_wr.x) < 0.15

    # Logika sukcesu: Biodra zgięte, głowa w górze, ramiona stabilne
    if 70 < hip_angle < 110 and head_up and arms_aligned:
        return True
    return False


# Puste szablony dla reszty, aby program się nie wywalał
def cat_pose(landmarks, mp_pose):
    return False


def downward_facing_pose(landmarks, mp_pose):
    return False


def upward_facing_pose(landmarks, mp_pose):
    return False


def child_facing_pose(landmarks, mp_pose):
    return False
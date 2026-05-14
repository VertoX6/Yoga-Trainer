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
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    l_wr = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    # kat w biodrze
    hip_angle = calculate_angle(l_sh, l_hip, l_knee)

    head_up = nose.y < l_sh.y

    #czy ramiona proste
    arms_aligned = abs(l_sh.x - l_wr.x) < 0.15
    if 70 < hip_angle < 110 and head_up and arms_aligned:
        return True
    return False


def cat_pose(landmarks, mp_pose):
    return False


def downward_facing_pose(landmarks, mp_pose):
    return False


def upward_facing_pose(landmarks, mp_pose):
    return False


def child_facing_pose(landmarks, mp_pose):
    return False
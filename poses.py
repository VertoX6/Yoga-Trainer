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
    #kat biodra
    hip_angle = calculate_angle(l_sh, l_hip, l_knee)
    head_up = nose.y < l_sh.y
    #czy ramiona proste
    arms_aligned = abs(l_sh.x - l_wr.x) < 0.15
    if 70 < hip_angle < 110 and head_up and arms_aligned:
        return True
    return False


def cat_pose(landmarks, mp_pose):
    l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    l_wr = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]
    #kat biodro
    hip_angle = calculate_angle(l_sh, l_hip, l_knee)
    #glowa w dol
    head_down = nose.y > l_sh.y
    #rece pionowo pod barkami
    arms_aligned = abs(l_sh.x - l_wr.x) < 0.15
    #zaokraglone plecy
    if 70 < hip_angle < 110 and head_down and arms_aligned:
        return True
    return False


def downward_facing_pose(landmarks, mp_pose):
    sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    ank = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    hip_angle = calculate_angle(sh, hip, ank)
    arm_angle = calculate_angle(sh, elbow, wrist)
    return (
        70 < hip_angle < 110 and
        arm_angle > 150
    )


def upward_facing_pose(landmarks, mp_pose):
    nose = landmarks[mp_pose.PoseLandmark.NOSE]
    sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]

    elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    back_angle = calculate_angle(sh, hip, knee)
    arm_angle = calculate_angle(sh, elbow, wrist)
    head_up = nose.y < sh.y
    arms_straight = arm_angle > 150
    return (
        head_up and
        arms_straight and
        120 < back_angle < 180
    )

def child_facing_pose(landmarks, mp_pose):
    sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]
    hip_angle = calculate_angle(sh, hip, knee)
    return (
        hip_angle < 60 and
        nose.y > sh.y
    )
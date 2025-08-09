import cv2
import mediapipe as mp
import numpy as np
import math
import time
import webbrowser
import random
from datetime import datetime
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- Configuration ---
SMILE_SCORE_MIN = 800
SMILE_SCORE_MAX = 4000

ATTENTION_TIMEOUT = 5.0
DISTRACTION_SITES = [
    "https://pointerpointer.com/",
    "https://longdogechallenge.com/",
    "https://cat-bounce.com/",
    "https://theuselessweb.com/",
    "https://www.boredbutton.com/"
]

# Challenge settings
CHALLENGE_MIN_INTERVAL = 20   # seconds
CHALLENGE_MAX_INTERVAL = 60   # seconds
CHALLENGE_MOUTH_THRESHOLD = 3000  # smile score threshold for open mouth
CHALLENGE_TIMEOUT = 15        # seconds to complete challenge

# --- Initialization ---
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

def initialize_dependencies():
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam.")
        return None, None, None, None

    volume_controller = None
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_controller = cast(interface, POINTER(IAudioEndpointVolume))
    except Exception as e:
        print(f"Error initializing volume control (Are you on Windows?): {e}")
        print("Volume control will be disabled.")

    return face_mesh, hands, cap, volume_controller

def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def detect_peace_sign(hand_landmarks):
    """Check if index and middle fingers are extended, others folded."""
    # Landmarks: https://google.github.io/mediapipe/solutions/hands#hand-landmark-model
    finger_tips = [8, 12, 16, 20]  # index, middle, ring, pinky tips
    finger_pips = [6, 10, 14, 18]  # pip joints

    extended = []
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            extended.append(True)
        else:
            extended.append(False)

    # Peace sign: index + middle extended, ring + pinky folded
    return extended[0] and extended[1] and not extended[2] and not extended[3]

def main():
    face_mesh, hands, cap, volume = initialize_dependencies()
    if not cap:
        return

    min_vol, max_vol = (volume.GetVolumeRange()[:2]) if volume else (0, 0)

    last_focused_time = time.time()
    attention_lost_triggered = False

    # Challenge state
    next_challenge_time = time.time() + random.randint(CHALLENGE_MIN_INTERVAL, CHALLENGE_MAX_INTERVAL)
    challenge_active = False
    challenge_start_time = None

    print("Smile Volume Controller with Peace Sign Challenge is running.")
    print("Press 'q' to quit.")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        img_h, img_w, _ = image.shape

        image.flags.writeable = False
        face_results = face_mesh.process(image)
        hand_results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        attention_status = "NOT DETECTED"
        smile_score = 0
        vol_percentage = 0

        # --- Face detection & attention check ---
        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            nose_tip = face_landmarks.landmark[1]
            left_edge = face_landmarks.landmark[234]
            right_edge = face_landmarks.landmark[454]
            face_width = right_edge.x - left_edge.x
            nose_ratio = (nose_tip.x - left_edge.x) / (face_width + 1e-6)

            if 0.35 < nose_ratio < 0.65:
                attention_status = "FOCUSED"
                last_focused_time = time.time()
                attention_lost_triggered = False
            else:
                attention_status = "LOST"

            # Smile detection
            left_corner = face_landmarks.landmark[291]
            right_corner = face_landmarks.landmark[61]
            top_lip = face_landmarks.landmark[13]
            bottom_lip = face_landmarks.landmark[14]

            left_corner_px = (int(left_corner.x * img_w), int(left_corner.y * img_h))
            right_corner_px = (int(right_corner.x * img_w), int(right_corner.y * img_h))
            top_lip_px = (int(top_lip.x * img_w), int(top_lip.y * img_h))
            bottom_lip_px = (int(bottom_lip.x * img_w), int(bottom_lip.y * img_h))

            horizontal_dist = euclidean_distance(left_corner_px, right_corner_px)
            vertical_dist = euclidean_distance(top_lip_px, bottom_lip_px)
            smile_score = horizontal_dist * vertical_dist

            vol_percentage = np.interp(smile_score, [SMILE_SCORE_MIN, SMILE_SCORE_MAX], [0, 100])
            vol_percentage = np.clip(vol_percentage, 0, 100)

            if volume and not challenge_active:
                target_vol_db = np.interp(vol_percentage, [0, 100], [min_vol, max_vol])
                try:
                    volume.SetMasterVolumeLevel(target_vol_db, None)
                except Exception:
                    pass

            # Draw mouth lines
            cv2.line(image, right_corner_px, left_corner_px, (0, 255, 0), 2)
            cv2.line(image, top_lip_px, bottom_lip_px, (0, 255, 0), 2)

        # --- Random challenge trigger ---
        current_time = time.time()
        if not challenge_active and current_time >= next_challenge_time:
            challenge_active = True
            challenge_start_time = current_time
            if volume:
                volume.SetMasterVolumeLevel(min_vol, None)  # mute
            print("Challenge started! Show peace sign and open mouth wide.")

        # --- If challenge is active ---
        if challenge_active:
            cv2.putText(image, "CHALLENGE: Peace sign + Open mouth!", (50, img_h - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            peace_detected = False
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    if detect_peace_sign(hand_landmarks):
                        peace_detected = True
                    mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if peace_detected and smile_score > CHALLENGE_MOUTH_THRESHOLD:
                # Challenge success
                filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                cv2.imwrite(filename, image)
                print(f"Challenge complete! Snapshot saved as {filename}")
                challenge_active = False
                next_challenge_time = current_time + random.randint(CHALLENGE_MIN_INTERVAL, CHALLENGE_MAX_INTERVAL)

            # Fail if timeout
            elif current_time - challenge_start_time > CHALLENGE_TIMEOUT:
                print("Challenge failed! Waiting for next one...")
                challenge_active = False
                next_challenge_time = current_time + random.randint(CHALLENGE_MIN_INTERVAL, CHALLENGE_MAX_INTERVAL)

        # --- Attention penalty ---
        time_since_focused = time.time() - last_focused_time
        if not attention_lost_triggered and time_since_focused > ATTENTION_TIMEOUT:
            print("Attention lost! Launching distraction...")
            webbrowser.open(random.choice(DISTRACTION_SITES), new=2)
            attention_lost_triggered = True

        # --- UI ---
        status_color = (0, 255, 0) if attention_status == "FOCUSED" else (0, 0, 255)
        cv2.putText(image, f'ATTENTION: {attention_status}', (img_w - 250, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        # Volume bar
        if not challenge_active:
            bar_x, bar_y, bar_w, bar_h = 50, 50, 50, 200
            bar_height = int(bar_h * vol_percentage / 100)
            cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 100), -1)
            cv2.rectangle(image, (bar_x, bar_y + bar_h - bar_height), (bar_x + bar_w, bar_y + bar_h), (0, 255, 0), -1)
            cv2.putText(image, f'{int(vol_percentage)}%', (bar_x, bar_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(image, f'Score: {int(smile_score)}', (bar_x, bar_y + bar_h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow('Smile Volume Controller', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Application closed.")

if __name__ == "__main__":
    main()

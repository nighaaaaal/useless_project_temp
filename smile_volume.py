# Smile-Controlled Volume - A Useless Hackathon Project
#
# This script uses your webcam to detect your face and measures
# how wide you are smiling. It then maps your smile width to your
# computer's system volume.
#
# A small smile = low volume. A huge grin = 100% volume!
#
# Required Libraries:
# pip install opencv-python
# pip install mediapipe
# pip install pycaw  (for Windows volume control)
#
# For macOS/Linux, you would need a different library for volume control.
# macOS: `osascript -e "set volume output volume {level}"`
# Linux: `amixer -D pulse sset Master {level}%`

import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- Initialization ---

# 1. Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# 2. Initialize Webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open webcam.")
    exit()

# 3. Initialize Windows Volume Controller (pycaw)
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    # Get the valid volume range (-65.25 to 0.0 for my system)
    vol_range = volume.GetVolumeRange()
    min_vol = vol_range[0]
    max_vol = vol_range[1]
except Exception as e:
    print(f"Error initializing volume control (Are you on Windows?): {e}")
    print("This script currently only supports Windows for volume control.")
    volume = None


# --- Configuration ---
# You might need to adjust these values based on your face and camera distance
SMILE_WIDTH_MIN = 50  # The pixel width of your mouth at rest
SMILE_WIDTH_MAX = 100 # The pixel width of your biggest smile

print("Smile Volume Controller is running.")
print("Smile wide to increase the volume!")
print("Press 'q' to quit.")

# --- Main Loop ---
while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a later selfie-view display
    # and convert the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = face_mesh.process(image)

    # Draw the face mesh annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    img_h, img_w, img_c = image.shape

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # --- Smile Detection Logic ---
            
            # We use specific landmarks for the corners of the mouth
            # Landmark 61 is the right corner, Landmark 291 is the left corner
            right_corner = face_landmarks.landmark[61]
            left_corner = face_landmarks.landmark[291]

            # Convert normalized landmark coordinates to pixel coordinates
            right_corner_px = (int(right_corner.x * img_w), int(right_corner.y * img_h))
            left_corner_px = (int(left_corner.x * img_w), int(left_corner.y * img_h))

            # Calculate the Euclidean distance between the corners
            smile_width = int(math.sqrt((right_corner_px[0] - left_corner_px[0])**2 + 
                                     (right_corner_px[1] - left_corner_px[1])**2))

            # --- Volume Control Logic ---

            # Map the smile width to a volume percentage (0 to 100)
            # np.interp is a handy function for mapping a value from one range to another
            vol_percentage = np.interp(smile_width, [SMILE_WIDTH_MIN, SMILE_WIDTH_MAX], [0, 100])
            
            # Clamp the value between 0 and 100
            vol_percentage = max(0, min(100, vol_percentage))

            # Set the system volume if the controller is available
            if volume:
                # Map the 0-100 percentage to the system's specific volume range
                target_vol_db = np.interp(vol_percentage, [0, 100], [min_vol, max_vol])
                try:
                    volume.SetMasterVolumeLevel(target_vol_db, None)
                except Exception as e:
                    # This can happen if the audio device is disconnected
                    print(f"Error setting volume: {e}")


            # --- Visual Feedback ---
            # Draw a line between the mouth corners to visualize the smile width
            cv2.line(image, right_corner_px, left_corner_px, (0, 255, 0), 2)
            
            # Draw a volume bar on the screen
            bar_x, bar_y, bar_w, bar_h = 50, 50, 50, 200
            cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 100), -1)
            bar_height = int(bar_h * (vol_percentage / 100))
            cv2.rectangle(image, (bar_x, bar_y + bar_h - bar_height), (bar_x + bar_w, bar_y + bar_h), (0, 255, 0), -1)
            
            # Display the volume percentage
            cv2.putText(image, f'{int(vol_percentage)}%', (bar_x, bar_y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)


    # Show the final image
    cv2.imshow('Smile Volume Controller', image)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
print("Application closed.")


<img width="3188" height="1202" alt="frame (3)" src="https://github.com/user-attachments/assets/517ad8e9-ad22-457d-9538-a9e62d137cd7" />

# Chirikku Kutta : A Smile Volume Controller with Peace Sign Challenge 🎯

**Author:** Mohamed Nihal T K N
**Team / Single-member Project:** Mohamed Nihal T K N

---

## Project Summary

A webcam-based desktop utility that dynamically controls system volume based on how wide you smile, and periodically challenges you to show a peace sign and open your mouth wide to verify engagement. If you look away for a set time the app launches a random "distraction" site to get your attention back.

This is a single‑member final project implementing real‑time face and hand tracking using MediaPipe, computer vision with OpenCV, and system audio control (Windows) via pycaw.

---

## Why this project?

### The Problem (tongue-in-cheek)

People get distracted while using their computers, or their playlists are either too quiet or too loud. Also, existing volume controls are boring.

### The Solution

Automatically set the system volume in real time based on a "smile score" (mouth width × mouth opening). To keep the user honest and engaged, the app occasionally mutes itself and demands a *peace sign + open mouth* challenge — complete it to save a snapshot and restore volume.

---

## Features

* Real-time face mesh detection (MediaPipe) to compute a smile score.
* Smooth mapping from smile score → system master volume (Windows via pycaw).
* Hand tracking to detect a peace sign (index + middle fingers extended).
* Random time-based challenge that mutes volume until user performs the gesture and opens mouth wide enough.
* Attention detection — if you look away for a configurable timeout, the app opens a random distraction website.
* Saves snapshot on successful challenge completion.

---

## Technologies / Libraries

**Software**

* Python 3.8+ (recommended)
* OpenCV (`cv2`)
* MediaPipe (`mediapipe`) — Face Mesh & Hands
* NumPy (`numpy`)
* pycaw (`pycaw`) — Windows audio control
* comtypes
* ctypes
* Other standard libs: `math`, `time`, `random`, `datetime`, `webbrowser`

**Platform**

* Developed and tested on **Windows** (pycaw used for system volume). The app will run on other OSes but system volume control will be disabled unless replaced with an OS-specific module.

---

## Files

* `main.py` — Main application (the code you provided).
* `README.md` — This file.
* `snapshot_YYYYMMDD_HHMMSS.png` — Generated on successful challenge (saved beside the script).

---

## Installation

1. Clone the repository or copy the files to your machine.

2. (Optional) Create and activate a virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3. Install required packages:

```bash
pip install opencv-python mediapipe numpy comtypes pycaw
```

> Note: Installing `pycaw` and using it requires Windows. If you're on macOS / Linux, the script will still run but volume control will be disabled and a message will be printed.

---

## Configuration (in `main.py`)

You can tweak the following constants near the top of the script:

* `SMILE_SCORE_MIN`, `SMILE_SCORE_MAX` — range for mapping smile score → volume.
* `ATTENTION_TIMEOUT` — seconds to wait before triggering the attention penalty when face is not detected or off-center.
* `DISTRACTION_SITES` — list of URLs opened when attention is lost.
* Challenge settings:

  * `CHALLENGE_MIN_INTERVAL`, `CHALLENGE_MAX_INTERVAL` — how often (seconds) a challenge may appear.
  * `CHALLENGE_MOUTH_THRESHOLD` — mouth openness threshold for challenge success.
  * `CHALLENGE_TIMEOUT` — seconds allowed to complete the challenge.

---

## Usage

1. Ensure your webcam is connected and not used by another application.
2. Run the app:

```bash
python main.py
```

3. The app window shows:

* A live video feed.
* Current attention status (FOCUSED / LOST).
* A vertical volume bar and numeric percentage (when no challenge is active).
* A CHALLENGE overlay when a challenge is active.

4. Controls:

* Press `q` to quit.

---

## Implementation Notes

* Smile score = horizontal mouth corner distance × vertical lip distance. This produces a value interpolated to 0–100% volume.
* Face centering is estimated using nose tip relative to left/right face edges.
* Peace sign detection uses MediaPipe hand landmarks to check whether index and middle fingertips are above their pip joints while ring & pinky are folded.
* The app mutes volume during a challenge (if OS volume control is available) and restores it upon success.

---

## Screenshots


![App Screenshot](https://github.com/nighaaaaal/useless_project_temp/blob/main/Screenshot%202025-08-15%20113656.png)
![App Screenshot](https://github.com/nighaaaaal/useless_project_temp/blob/main/Screenshot%202025-08-15%20113656.png)

---

## Troubleshooting & Tips

* If the webcam fails to open, ensure no other app is using it and that your OS permissions allow camera access.
* If `pycaw` fails to initialize, you'll see a printed error and the script will continue with volume control disabled.
* Tune `SMILE_SCORE_MIN/MAX` and `CHALLENGE_MOUTH_THRESHOLD` for your camera distance and facial proportions.
* Lighting helps: even, front-facing light improves detection robustness.

---

## Potential Improvements

* Smooth volume changes using a low-pass filter to avoid jitter.
* Add cross-platform volume control (macOS: `osascript` or `coreaudio`, Linux: `pulseaudio`/`pactl`).
* Add calibration step for smile and mouth thresholds per user.
* Improve attention detection using eye tracking / gaze estimation.
* Add GUI controls to change config at runtime.

---

## Demo
Note: The demo video availabe at https://github.com/nighaaaaal/useless_project_temp/blob/main/demo.mp4. However, in the demonstration video, the audio doesnt change as it is a screenrecording, But in it its clearly visible the audio bar changes, so its working, You can try it yourself.

TO VIEW THAT DOWNLOAD THE RAW FILE.

![Demo Video](https://github.com/nighaaaaal/useless_project_temp/blob/main/demo.mp4)

---

## License & Acknowledgements

* This project is shared by **Mohamed Nihal T K N**.
* Libraries used: MediaPipe, OpenCV, NumPy, pycaw.

---

Made with ❤️ by Mohamed Nihal T K N

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--25-25?link=https%3A%2F%2Fwww.tinkerhub.org%2Fevents%2FQ2Q1TQKX6Q%2FUseless%2520Projects)

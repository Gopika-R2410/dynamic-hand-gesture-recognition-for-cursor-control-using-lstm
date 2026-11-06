# Gesture Mouse

Control your cursor and run custom actions with hand gestures, using only a webcam.
Everything runs locally; no video leaves your computer.

## Install
    python -m venv venv
    venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
    pip install -r requirements.txt

Use Python 3.9 - 3.11.

## Run
    python main.py

## Built-in behaviour
- Move your index finger -> cursor moves (inside the yellow box).
- Pinch thumb + index -> click. Hold the pinch and move -> drag.

- Peace sign (index + middle up, ring + pinky down): scroll mode. Hand in the top of the
  yellow box scrolls up, bottom scrolls down, middle = stop.
- The bottom of the window shows the live pinch value. Pinch and read the number, then press
  + until "click when <" is above it.

## Custom gestures
1. Press R in the preview window, type a name (e.g. fist), hold the pose.
2. Choose an action in the terminal (shortcut, open site, scroll, lock...).
3. Record a gesture called "neutral" (relaxed open hand) so normal hands don't trigger things.
4. Hold the gesture ~0.3s to trigger it.

Suggested set: neutral, fist (ctrl+w), peace (alt+left), palm (lock/unlock).

## Keys
R record | M map | D delete | L lock | Q/Esc quit

## Tuning
- cursor.py: MARGIN (CursorController margin), pinch thresholds
- smoothing.py: min_cutoff (lower = smoother), beta (higher = less lag)
- classifier.py: threshold (lower = stricter matching)
- main.py: CONFIRM_FRAMES, COOLDOWN

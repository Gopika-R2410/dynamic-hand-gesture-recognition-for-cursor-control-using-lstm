"""Gesture Mouse - control your computer with custom hand gestures.

Preview-window keys:
  R = record a new gesture     M = (re)map a gesture to an action
  D = delete a gesture         L = lock / unlock control
  + / - = make click easier / harder
  Q or Esc = quit
"""
import sys
import time
import cv2

from tracker import HandTracker
from cursor import CursorController
from classifier import GestureClassifier, to_features
from actions import ActionStore, run_action, prompt_for_action, CONTINUOUS

SAMPLES_PER_GESTURE = 120
COUNTDOWN_SECONDS = 3
CONFIRM_FRAMES = 8        # gesture must be held this many frames
COOLDOWN = 1.0            # seconds between one-shot actions
NO_CURSOR_GESTURES = None  # cursor moves only for unknown / neutral / point


class Debouncer:
    def __init__(self, frames):
        self.frames = frames
        self.last = None
        self.count = 0

    def update(self, gesture):
        if gesture is not None and gesture == self.last:
            self.count += 1
        else:
            self.last, self.count = gesture, 1
        return self.last if (self.last is not None and self.count >= self.frames) else None


def open_camera():
    if sys.platform.startswith("win"):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def put(frame, text, y, color=(0, 255, 0), scale=0.6):
    cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2)


def main():
    cap = open_camera()
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    tracker = HandTracker()
    cursor = CursorController()
    clf = GestureClassifier()
    store = ActionStore()
    deb = Debouncer(CONFIRM_FRAMES)

    locked = False
    rec = None                 # recording state
    prev_stable = None
    fired = False
    last_fire = 0.0
    last_fire_continuous = 0.0
    flash_msg, flash_until = "", 0
    fps, t_prev = 0.0, time.time()

    print(__doc__)
    print("Known gestures:", clf.names() or "none yet - press R in the window")

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)  # mirror so right = right
        h, w = frame.shape[:2]
        now = time.time()

        hand = tracker.process(frame)
        gesture = None

        if hand:
            tracker.draw(frame, hand)
            lm = hand.landmark

            # ---- recording mode ----
            if rec:
                elapsed = now - rec["t0"]
                if elapsed < COUNTDOWN_SECONDS:
                    put(frame, f"Get ready: {COUNTDOWN_SECONDS - int(elapsed)}", 60, (0, 200, 255), 1.0)
                else:
                    rec["samples"].append(to_features(lm))
                    put(frame, f"Recording '{rec['name']}' {len(rec['samples'])}/{SAMPLES_PER_GESTURE}",
                        60, (0, 0, 255), 0.8)
                    if len(rec["samples"]) >= SAMPLES_PER_GESTURE:
                        clf.add_samples(rec["name"], rec["samples"])
                        name = rec["name"]
                        rec = None
                        print(f"\nSaved gesture '{name}'.")
                        if name != "neutral" and not store.get(name):
                            action = prompt_for_action()
                            if action:
                                store.set(name, action)
                                print(f"Mapped '{name}' -> {action}")
                        deb = Debouncer(CONFIRM_FRAMES)
                continue_normal = False
            else:
                continue_normal = True

            if continue_normal:
                gesture = clf.predict(lm)

                # cursor moves only when not locked and not showing a command gesture
                if not locked and (gesture in (None, "neutral", "point") or store.get(gesture) is None):
                    cursor.update(lm)
                else:
                    cursor.release()

                stable = deb.update(gesture if gesture != "neutral" else None)
                if stable != prev_stable:
                    prev_stable, fired = stable, False

                if stable:
                    action = store.get(stable)
                    if action and (not locked or action["type"] == "toggle_lock"):
                        if action["type"] in CONTINUOUS:
                            if now - last_fire_continuous > 0.08:
                                run_action(action)
                                last_fire_continuous = now
                        elif not fired and now - last_fire > COOLDOWN:
                            if action["type"] == "toggle_lock":
                                locked = not locked
                                flash_msg = "LOCKED" if locked else "UNLOCKED"
                            else:
                                run_action(action)
                                flash_msg = f"{stable} -> {action['type']}"
                            flash_until = now + 1.2
                            fired, last_fire = True, now
        else:
            cursor.release()
            deb.update(None)
            prev_stable, fired = None, False
            if rec:
                put(frame, "Show your hand to the camera", 60, (0, 0, 255), 0.8)

        # ---- HUD ----
        m = cursor.margin
        cv2.rectangle(frame, (int(w * m), int(h * m)), (int(w * (1 - m)), int(h * (1 - m))), (255, 255, 0), 1)
        fps = 0.9 * fps + 0.1 * (1.0 / max(now - t_prev, 1e-6))
        t_prev = now
        put(frame, f"{'LOCKED' if locked else 'ACTIVE'}  FPS {fps:4.1f}  Gesture: {gesture}", h - 40,
            (0, 0, 255) if locked else (0, 255, 0))
        put(frame, "R record | M map | D delete | L lock | Q quit", h - 12, (255, 255, 255), 0.5)
        put(frame, f"mode:{cursor.mode}  pinch:{cursor.ratio:.2f}  click when < {cursor.press:.2f}   (+/- to adjust)",
            h - 65, (255, 255, 0), 0.5)
        if now < flash_until:
            put(frame, flash_msg, 100, (0, 255, 255), 1.0)

        cv2.imshow("Gesture Mouse", frame)
        key = cv2.waitKey(1) & 0xFF

        if key in (27, ord("q")):
            break
        elif key in (ord("+"), ord("=")):
            cursor.press = min(cursor.press + 0.02, 0.8)
        elif key == ord("-"):
            cursor.press = max(cursor.press - 0.02, 0.05)
        elif key == ord("l"):
            locked = not locked
            cursor.release()
        elif key == ord("r") and not rec:
            name = input("\nName for the new gesture (use 'neutral' for a relaxed hand): ").strip().lower()
            if name:
                rec = {"name": name, "t0": time.time(), "samples": []}
                print("Hold the pose in front of the camera, slightly moving/rotating your hand...")
        elif key == ord("m"):
            print("Gestures:", clf.names())
            name = input("Which gesture to map? ").strip().lower()
            if name in clf.names():
                action = prompt_for_action()
                if action:
                    store.set(name, action)
                    print(f"Mapped '{name}' -> {action}")
            else:
                print("No such gesture.")
        elif key == ord("d"):
            print("Gestures:", clf.names())
            name = input("Which gesture to delete? ").strip().lower()
            if clf.delete(name):
                store.remove(name)
                print(f"Deleted '{name}'.")

    cursor.release()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

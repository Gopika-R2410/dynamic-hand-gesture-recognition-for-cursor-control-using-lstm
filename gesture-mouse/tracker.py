"""Webcam hand tracking using MediaPipe."""
import cv2
import mediapipe as mp


class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.drawer = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=0,  # 0 = fastest
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
        )

    def process(self, frame_bgr):
        """Returns the MediaPipe landmark list (or None). Frame should already be mirrored."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        if result.multi_hand_landmarks:
            return result.multi_hand_landmarks[0]
        return None

    def draw(self, frame, hand_landmarks):
        self.drawer.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

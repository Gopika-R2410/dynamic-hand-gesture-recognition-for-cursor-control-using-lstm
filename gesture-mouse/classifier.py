"""Custom gesture recording + KNN classifier."""
import json
import os
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "gesture_data.json")


def to_features(lm):
    """Position- and scale-invariant 63-number feature vector."""
    pts = np.array([[p.x, p.y, p.z] for p in lm])
    pts = pts - pts[0]                         # wrist = origin
    scale = np.linalg.norm(pts[9]) or 1.0      # hand size
    return (pts / scale).flatten()


class GestureClassifier:
    def __init__(self, threshold=1.2):
        self.threshold = threshold   # max distance to nearest sample, else "unknown"
        self.data = {}
        self.model = None
        self._load()
        self.train()

    def _load(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE) as f:
                self.data = json.load(f)

    def _save(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f)

    def names(self):
        return sorted(self.data.keys())

    def add_samples(self, name, samples):
        self.data.setdefault(name, []).extend([s.tolist() for s in samples])
        self._save()
        self.train()

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            self._save()
            self.train()
            return True
        return False

    def train(self):
        X, y = [], []
        for name, samples in self.data.items():
            X += samples
            y += [name] * len(samples)
        if not X:
            self.model = None
            return
        self.model = KNeighborsClassifier(n_neighbors=min(5, len(X)))
        self.model.fit(np.array(X), y)

    def predict(self, lm):
        """Returns gesture name or None."""
        if self.model is None:
            return None
        f = to_features(lm).reshape(1, -1)
        dist, _ = self.model.kneighbors(f, n_neighbors=1)
        if dist[0][0] > self.threshold:
            return None
        return self.model.predict(f)[0]

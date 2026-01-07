import json
import os
from PySide6.QtCore import QStandardPaths

class HistoryManager:
    def __init__(self):
        self.filename = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "history.json")
        self.ensure_dir()
        self.history = self.load()

    def ensure_dir(self):
        dirname = os.path.dirname(self.filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def load(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return []

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.history, f)

    def add_entry(self, filepath):
        if filepath in self.history:
            self.history.remove(filepath)
        self.history.insert(0, filepath)
        self.history = self.history[:10] # Keep last 10
        self.save()

    def get_recent(self):
        return self.history

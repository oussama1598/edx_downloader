import os
import json


class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = {}

        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_file):
            return

        with open(self.config_file, 'r') as file:
            self.config = json.load(file)

    def _save_config(self):
        with open(self.config_file, 'w') as file:
            file.write(json.dumps(self.config))

    def get(self, key):
        if key not in self.config:
            return None

        return self.config[key]

    def set(self, key, value):
        self.config[key] = value

        self._save_config()

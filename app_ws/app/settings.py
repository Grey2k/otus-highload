import os


class Settings:
    def __init__(self):
        self.data = {}

    @classmethod
    def from_env(cls):
        obj = cls()
        obj.data = {k: v for k, v in os.environ.items()}
        return obj

    def get(self, key, default=None):
        return self.data.get(key, default)

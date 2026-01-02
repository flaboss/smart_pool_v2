import json
from pathlib import Path

class Translator:
    def __init__(self, lang="pt"):
        self.lang = lang
        self.translations = {}
        self.load(lang)

    def load(self, lang):
        path = Path(__file__).parent / f"{lang}.json"
        with open(path, encoding="utf-8") as f:
            self.translations = json.load(f)
        self.lang = lang

    def t(self, key):
        return self.translations.get(key, key)

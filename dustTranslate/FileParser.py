import os.path
import re

class PropertiesParser():
    def __init__(self, filepath):
        self.filepath = filepath
        self.tags = {}
        self.parseFile(filepath)

    def parseFile(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, encoding='utf-8') as file:
                for line in file:
                    key, value = line.split('=', 1)
                    self.tags[key] = value.rstrip()
        else:
            pass

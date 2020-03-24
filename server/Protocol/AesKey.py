import os

class AesKey:
    def __init__(self, size):
        self.key = os.urandom(size)
        
    def regenerate(self, size):
        self.key = os.urandom(size)
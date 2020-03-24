import hashlib

class Signature:
    def sign(self, msg):
        return hashlib.sha256(msg).hexdigest()
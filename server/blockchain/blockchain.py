# consists in blocks
# block consist transaction
# block are connected through hashing
        # uniq digital fingerprint - transaction + previous blocks fingerprint
from Block import Block
blockchain = []

genesis_block = Block("Random msg arbitrary...", ["Satoshi sent 1 BTC to Ivan"])
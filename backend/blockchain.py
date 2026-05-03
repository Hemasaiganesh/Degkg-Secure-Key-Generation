# blockchain.py
import hashlib
import time
import json
import datetime

# ================= BLOCK CLASS =================
class Block:
    def __init__(self, index, data, prev_hash, difficulty=2):
        self.index = index
        self.timestamp = datetime.datetime.now().isoformat()
        self.data = data
        self.prev_hash = prev_hash
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.mine_block()

    # Hash calculation
    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.data, sort_keys=True)}{self.prev_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    # Proof-of-Work Mining (LIMITED LOOP)
    def mine_block(self):
        target = "0" * self.difficulty
        for _ in range(100000):   # prevent Flask freeze
            hash_val = self.calculate_hash()
            if hash_val.startswith(target):
                return hash_val
            self.nonce += 1
        return self.calculate_hash()   # fallback

    # Convert block to dict
    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty
        }

# ================= BLOCKCHAIN CLASS =================
class Blockchain:
    def __init__(self, difficulty=2):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty

    def create_genesis_block(self):
        return Block(0, {"msg": "Genesis Block"}, "0", difficulty=1)

    # Add new block
    def add_block(self, data):
        prev_block = self.chain[-1]
        new_block = Block(len(self.chain), data, prev_block.hash, self.difficulty)
        self.chain.append(new_block)
        return new_block

    # Validate blockchain
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False
            if current.prev_hash != prev.hash:
                return False

        return True

    # Get blockchain list
    def get_chain(self):
        return [block.to_dict() for block in self.chain]

# Global blockchain instance
blockchain = Blockchain(difficulty=2)

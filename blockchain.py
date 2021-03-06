import hashlib
import json
import logging
import sys
import time

from ecdsa import NIST256p
from ecdsa import VerifyingKey

import utils

MINING_DIFFICULTY = 3
MINING_SENDER = 'THE BLOCKCHAIN'
MINING_REWARD = 1.0

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class BlockChain(object):

    def __init__(self, blockchain_address=None):
        self.transaction_pool = []
        self.chain = []
        self.create_block(0, self.hash({}))
        self.blockchain_address = blockchain_address

    def create_block(self, nonce, previous_hash):
        # ブロックの中身
        block = utils.sorted_dict_by_key({
            'timestamps': time.time(),
            # トランザクションプールのトランザクションを挿入
            'transactions': self.transaction_pool,
            'nonce': nonce,
            'previous_hash': previous_hash
        })
        # ブロックをブロックチェーンに追加
        self.chain.append(block)
        # トランザクションプール内のトランザクションは移行できたため中身をクリア
        self.transaction_pool = []
        return block

    def hash(self, block):
        sorted_block = json.dumps(block, sort_keys=True)
        return hashlib.sha256(sorted_block.encode()).hexdigest()

    def add_transaction(
            self, sender_blockchain_address, recipient_blockchain_address,
            value, sender_public_key=None, signature=None):
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': sender_blockchain_address,
            'recipient_blockchain_address': recipient_blockchain_address,
            'value': float(value)
        })

        # マイナーの処理時はトランザクションチェックを行わずにトランザクションプールに追加する
        if sender_blockchain_address == MINING_SENDER:
            self.transaction_pool.append(transaction)
            return True

        # トランザクションが改竄されていなければトランザクションプールに追加
        if self.verify_transaction_signature(sender_public_key, signature, transaction):
            if self.calculate_total_amount(sender_blockchain_address) < float(value):
                logger.error({'action': 'add_transaction', 'error': 'no_value'})
                return False

            self.transaction_pool.append(transaction)
            return True

        return False

    # トランザクションが改竄されていないか確認
    def verify_transaction_signature(
            self, sender_public_key, signature, transaction):
        sha256 = hashlib.sha256()
        sha256.update(str(transaction).encode('utf-8'))
        message = sha256.digest()
        signature_bytes = bytes().fromhex(signature)
        verifying_key = VerifyingKey.from_string(
            bytes().fromhex(sender_public_key), curve=NIST256p
        )
        verified_key = verifying_key.verify(signature_bytes, message)
        return verified_key

    def valid_proof(self, transactions, previous_hash, nonce, difficulty=MINING_DIFFICULTY):
        guess_block = utils.sorted_dict_by_key({
            'transactions': transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        })
        guess_hash = self.hash(guess_block)
        return guess_hash[:difficulty] == '0'*difficulty

    def proof_of_work(self):
        transactions = self.transaction_pool.copy()
        previous_hash = self.hash(self.chain[-1])
        nonce = 0
        while self.valid_proof(transactions, previous_hash, nonce) is False:
            nonce += 1
        return nonce

    def mining(self):
        # ブロックチェーンネットワークがマイナーに対してvalueを付与している部分
        self.add_transaction(
            sender_blockchain_address=MINING_SENDER,
            recipient_blockchain_address=self.blockchain_address,
            value=MINING_REWARD
        )
        # 本来はproof_of_workに10分かかるように設計する
        nonce = self.proof_of_work()
        # 一個前のブロックを使ったハッシュ値
        previous_hash = self.hash(self.chain[-1])
        self.create_block(nonce, previous_hash)
        logger.info({'action': 'mining', 'status': 'success'})
        return True

    def calculate_total_amount(self, blockchain_address):
        total_amount = 0.0
        for block in self.chain:
            for transaction in block['transactions']:
                value = float(transaction['value'])
                if blockchain_address == transaction['recipient_blockchain_address']:
                    total_amount += value
                if blockchain_address == transaction['sender_blockchain_address']:
                    total_amount -= value
        return total_amount

if __name__ == '__main__':
    my_blockchain_address = 'my_block_chain_address'
    block_chain = BlockChain(blockchain_address=my_blockchain_address)
    utils.pprint(block_chain.chain)

    # トランザクションプールにトランザクションの追加R
    block_chain.add_transaction('A', 'B', 1.0)
    block_chain.mining()
    utils.pprint(block_chain.chain)

    # トランザクションの追加
    block_chain.add_transaction('C', 'D', 2.0)
    block_chain.add_transaction('X', 'Y', 5.0)
    block_chain.mining()
    utils.pprint(block_chain.chain)

    print('my', block_chain.calculate_total_amount(my_blockchain_address))
    print('C', block_chain.calculate_total_amount('C'))
    print('D', block_chain.calculate_total_amount('D')) 

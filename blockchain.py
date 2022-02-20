import hashlib
import json
import logging
import sys
import time

import utils

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

class BlockChain(object):

    def __init__(self):
        self.transaction_pool = []
        self.chain = []
        self.create_block(0, self.hash({}))

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

    def add_transaction(self,
                        sender_blockchain_address,
                        recipient_blockchain_address,
                        value):
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': sender_blockchain_address,
            'recipient_blockchain_adress': recipient_blockchain_address,
            'value': float(value)
        })
        self.transaction_pool.append(transaction)
        return True

def pprint(chains):
    for i, chain in enumerate(chains):
        print(f'{"="*25} Chain {i} {"="*25}')
        for k, v in chain.items():
            if k == 'transactions':
                print(k)
                for d in v:
                    print(f'{"-"*40}')
                    for kk, vv in d.items():
                        print(f'{kk:30}{vv}')
            else:
                print(f'{k:15}{v}')
    print(f'{"*"*25}')

if __name__ == '__main__':
    block_chain = BlockChain()
    pprint(block_chain.chain)

    # トランザクションの追加
    block_chain.add_transaction('A', 'B', 1.0)
    # 一個前のブロックを使ったハッシュ値
    previous_hash = block_chain.hash(block_chain.chain[-1])
    block_chain.create_block(2, previous_hash)
    pprint(block_chain.chain)

    # トランザクションの追加
    block_chain.add_transaction('C', 'D', 2.0)
    block_chain.add_transaction('X', 'Y', 5.0)
    # 一個前のブロックを使ったハッシュ値
    previous_hash = block_chain.hash(block_chain.chain[-1])
    block_chain.create_block(3, previous_hash)
    pprint(block_chain.chain)

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

def pprint(chains):
    for i, chain in enumerate(chains):
        print(f'{"="*25} Chain {i} {"="*25}')
        for k, v in chain.items():
            print(f'{k:15}{v}')
    print(f'{"*"*25}')

if __name__ == '__main__':
    block_chain = BlockChain()
    pprint(block_chain.chain)
    # 一個前のブロックを使ったハッシュ値
    previous_hash = block_chain.hash(block_chain.chain[-1])
    block_chain.create_block(2, previous_hash)
    pprint(block_chain.chain)
    # 一個前のブロックを使ったハッシュ値
    previous_hash = block_chain.hash(block_chain.chain[-1])
    block_chain.create_block(3, previous_hash)
    pprint(block_chain.chain)

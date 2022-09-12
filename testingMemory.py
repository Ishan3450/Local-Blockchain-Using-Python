# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:46:44 2022

@author: ISHAN
"""

import hashlib
import datetime
import json
from flask import jsonify, Flask

class Blockchain:

    def __init__(self):
        self.chain = []
        # genesis block
        self.create_block(proof = 1, previous_hash = '0') 
        
    def create_block(self, proof, previous_hash):
        block = { 
            'index' : len(self.chain) + 1,
            'timestamp' : str(datetime.datetime.now()),
            'proof' : proof,
            'previous_hash' : previous_hash
            }
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
            
        return new_proof
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            current_block = chain[block_index]
            
            if current_block['previous_hash'] != self.hash(previous_block):
                return False
            
            current_block_proof = current_block['proof']
            previous_block_proof = previous_block['proof']
            
            hash_operation = hashlib.sha256(str(current_block_proof**2 - previous_block_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = current_block
            block_index += 1
        
        return True
    


app = Flask(__name__)

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_block_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_block_proof)
    previous_hash = blockchain.hash(previous_block)
    result_block = blockchain.create_block(proof, previous_hash)
    
    result = {
        'message' : 'Congratulations !! You successfully mined a block.',
        'index' : result_block['index'],
        'timestamp' : result_block['timestamp'],
        'proof' : result_block['proof'],
        'previous_hash' : result_block['previous_hash']
        }
    
    return jsonify(result), 200
    
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    result = {
        'length' : len(blockchain.chain),
        'chain' : blockchain.chain
        }
    return jsonify(result), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    valid_chain = blockchain.is_chain_valid(blockchain.chain)
    
    if valid_chain:
        response = {
            'message' : 'Ohh cool !! the blockchain is valid.',
            'status' : valid_chain
            }
    else:
        response = {
            'message' : 'Uhh ooh!! it seems that blockchain is not valid.',
            'status' : valid_chain
            }
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)
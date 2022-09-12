# Module 2 - Create a Cryptocurrency

# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 18:59:05 2022

@author: ISHAN
"""

# Part 1 - Create a Blockchain
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transaction = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
    
    def create_block(self, proof, previous_hash):
        block = {
                'index' : len(self.chain) + 1,
                'timestamp' : str(datetime.datetime.now()),
                'proof' : proof,
                'previous_hash' : previous_hash,
                'transactions' : self.transaction
            }
        
        self.trasaction = []
        self.chain.append(block);
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
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
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            current_block = chain[block_index]
            
            if current_block['previous_hash'] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            current_block_proof = current_block['proof']
            
            hash_operation = hashlib.sha256(str(current_block_proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = current_block
            block_index += 1
        
        return True
            
    
    def add_transaction(self, sender, receiver, amount):
        transaction_info = {
            'sender' : sender,
            'receiver' : receiver,
            'amount' : amount
            }
        self.transaction.append(transaction_info)
        previous_block = self.get_previous_block()
        
        return previous_block['index'] + 1
    
    def add_node(self, node_address):
        parsed_url = urlparse(node_address)
        # simply parsed_url will hace a dictionary having so many keys 
        # so we simply getting the netloc which is like 192.0.0.1:5000 so we simply get this part from the whole url
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        
        # longest_chain, we will get it by scanning the network
        longest_chain = None
        
        # max_length is the biggest length of the chain we are dealing with it right now
        max_length = len(self.chain)
        
        for node in network:
            # we will get the response from the mine_block method
            response = requests.get(f'http://{node}/get_chain')
            
            if response.status_code == 200:
                # length is the length of the current node running in the for loop
                length = response.json()['length']
                # chain of the current iterating node variable is used to check the chain is valid or not
                chain = response.json()['chain']
                
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    # replacing the current chain with the longest chain
                    longest_chain = chain
                    
        if longest_chain: 
            # or we can write as "if longest_chain != None:"
            # replacing the current chain with the longest chain from the nodes
            self.chain = longest_chain
            return True
        
        return False
            
                
             
    
        
# Part 2 - Mining our Blockchain


# Part 2.1 - Creating a Web Application using FLASK
      
app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
# app.debug = True

# Part 2.2 - Creating a Blockchain

blockchain = Blockchain()


# creating an address for the node for Port 5000
node_address = str(uuid4()).replace('-', '')

# Part 2.3 - Mining a new Block

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Ishan', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {
            'message' : 'Congratulations !! you have successfully mined a block.',
            'index' : block['index'],
            'timestamp' : block['timestamp'],
            'proof' : block['proof'],
            'previous_hash' : block['previous_hash'],
            'transactions' : block['transactions']
        }
    return jsonify(response), 200
            

            
# Part 2.4 -  Getting the full Blockchain

@app.route('/get_chain', methods = ['GET'])     
def get_chain():
    response = {
            'chain' : blockchain.chain,
            'length' : len(blockchain.chain)
        }
    
    return jsonify(response), 200

# parte 2.5 - Checking the blockchain is valid or not
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    
    if is_valid:
        response = {'message' : 'All good. Blockchain is valid.'}
    else:
        response = {'message' : 'Something is fishy !! Blockchain is not valid.'}
        
    return jsonify(response), 200


# adding a new transaction in the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    # below code will basically return the json file posted in the postman
    json = request.get_json()
    # transaction_keys is basically to check the keys from the json variable for valid request
    transaction_keys = ['sender', 'receiver', 'amount']
    
    # If all the keys in the transactions key list are not in the json file
    # basically below condition checks for like each keys in json variable is equal to the transaction_keys list
    if not all(keys in json for keys in transaction_keys):
        return 'Some keys in the transaction are missing !!', 400
    
    index = blockchain.add_transaction(json['sender'],json['receiver'],json['amount'])
    response = {
            'message' : f'The transaction will be added to the Block {index}'
        }
    
    # 201 http code is used for the success created acknowledgement
    return jsonify(response), 201

# Parte 3 - Decentralizing our blockchain

# Connecting new nodes

@app.route('connect_nodes', methods = ['POST'])
def connect_nodes():
    json = request.get_json()
    # here nodes stands for the key from the nodes.json file having values the ports
    nodes = json.get('nodes')
    
    if nodes is None:
        return 'No node !!', 400
    
    for node in nodes:
        blockchain.add_node(node)
    
    response = {
            'message' : 'All the nodes are now connected !! The Ishcoin blockchain now contains the following nodes:',
            'total_nodes' : list(blockchain.nodes)
        }
    
    return jsonify(response), 201
        

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_replaced = blockchain.replace_chain()
    
    if is_replaced:
        response = {
            'message' : 'The nodes had different chains so the chain was replaces by the longest one.',
            'new_chain' : blockchain.chain
            }
    else:
        response = {
            'message' : 'All good !! the chain is the longest one.',
            'actual_chain' : blockchain.chain
            }
        
    return jsonify(response), 200


# Running the application  
app.run(host = '0.0.0.0', port = 5000)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
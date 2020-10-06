import requests
import random
import json
import hashlib as hasher
import datetime as date
from flask import Flask
from flask import request
node = Flask(__name__)

# 블록 정의
class Block:
  def __init__(self, index, timestamp, data, previous_hash):
    self.index = index
    self.timestamp = timestamp
    self.data = data
    self.previous_hash = previous_hash
    self.hash = self.hash_block()

  def hash_block(self):
    sha = hasher.sha256()
    to_hash = str(self.index) + str(self.timestamp) + \
        str(self.data) + str(self.previous_hash)
    sha.update(to_hash.encode("utf-8"))
    return sha.hexdigest()

# 제네시스 블록
def create_genesis_block():
  return Block(0, date.datetime.now(), { "증명 정도": 9, "채굴": None}, "0")

miner_address = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"
# 블록체인의 복제 노드
blockchain = []
blockchain.append(create_genesis_block())
# 리스트에 있는 노드
this_nodes_transactions = []

peer_nodes = []
# A variable to deciding if we're mining or not
mining = True


@node.route('/txion', methods=['POST'])
def transaction():
  # On each new POST request,
  # we extract the transaction data
  new_txion = request.get_json()
  # Then we add the transaction to our list
  this_nodes_transactions.append(new_txion)
  # Because the transaction was successfully
  # submitted, we log it to our console
  print ("새 채굴")
  print ("FROM: {}".format(new_txion['from'].encode('UTF-8', 'replace')))
  print ("TO: {}".format(new_txion['to'].encode('UTF-8', 'replace')))
  print ("AMOUNT: {}\n".format(new_txion['amount']))
  # Then we let the client know it worked out
  return "채굴 성공!\n"


@node.route('/blocks', methods=['GET'])
def get_blocks():
  chain_to_send = blockchain
  # json 으로 convert
  for i in range(len(chain_to_send)):
    block = chain_to_send[i]
    block_index = str(block.index)
    block_timestamp = str(block.timestamp)
    block_data = str(block.data)
    block_hash = block.hash
    chain_to_send[i] = {
        "개요": block_index,
        "타임스탬프": block_timestamp,
        "데이터": block_data,
        "해쉬값": block_hash
    }
  chain_to_send = json.dumps(chain_to_send)
  return chain_to_send


def find_new_chains():
  # Get the blockchains of every
  # other node
  other_chains = []
  for node_url in peer_nodes:
    # Get their chains using a GET request
    block = requests.get(node_url + "/blocks").content
    # Convert the JSON object to a Python dictionary
    block = json.loads(block)
    # Add it to our list
    other_chains.append(block)
  return other_chains


def consensus(blockchain):
  # Get the blocks from other nodes
  other_chains = find_new_chains()
  # If our chain isn't longest,
  # then we store the longest chain
  longest_chain = blockchain
  for chain in other_chains:
    if len(longest_chain) < len(chain):
      longest_chain = chain
  # If the longest chain isn't ours,
  # then we stop mining and set
  # our chain to the longest one
  blockchain = longest_chain


def proof_of_work(last_proof):
  # Create a variable that we will use to find
  # our next proof of work
  incrementor = last_proof + 1
  # Keep incrementing the incrementor until
  # it's equal to a number divisible by 9
  # and the proof of work of the previous
  # block in the chain
  while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
    incrementor += 1
  # Once that number is found,
  # we can return it as a proof
  # of our work
  return incrementor


@node.route('/mine', methods=['GET'])
def mine():
  # Get the last proof of work
  last_block = blockchain[len(blockchain) - 1]
  last_proof = last_block.data['증명 정도']
  # Find the proof of work for
  # the current block being mined
  # Note: The program will hang here until a new
  #       proof of work is found
  proof = proof_of_work(last_proof)
  # Once we find a valid proof of work,
  # we know we can mine a block so
  # we reward the miner by adding a transaction
  this_nodes_transactions.append(
      {"from": "network", "to": miner_address, "amount": 1}
  )
  # Now we can gather the data needed
  # to create the new block
  new_block_data = {
      "증명 정도": proof,
      "transactions": list(this_nodes_transactions)
  }
  new_block_index = last_block.index + 1
  new_block_timestamp = this_timestamp = date.datetime.now()
  last_block_hash = last_block.hash
  # 채굴 리스트 초기화
  this_nodes_transactions[:] = []
 # 신규 블록
  mined_block = Block(
      new_block_index,
      new_block_timestamp,
      new_block_data,
      last_block_hash
  )
  blockchain.append(mined_block)
  # 이전 블록 해쉬 전송
  return json.dumps({
      "index": new_block_index,
      "timestamp": str(new_block_timestamp),
      "data": new_block_data,
      "hash": last_block_hash
  }) + "\n"

node.run()

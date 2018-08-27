# flask is a python web framework. it allows us to send and receive user requests
# with a minimal number of lines of non-web3py code. flask is beyond the scope of
# this tutorial so the flask code won't be commented. that way we can focus on
# how we're working with our smart contract
from flask import Flask, request, render_template

# solc is needed to compile our Solidity code
from solc import compile_source
import vyper
from vyper import compiler


# web3 is needed to interact with eth contracts
from web3 import Web3, HTTPProvider

# we'll use ConciseContract to interact with our specific instance of the contract
from web3.contract import ConciseContract

# initialize our flask app
app = Flask(__name__)

# declare the candidates we're allowing people to vote for.
# note that each name is in bytes because our contract variable
# candidateList is type bytes32[]

# open a connection to the local ethereum node
http_provider = HTTPProvider('http://localhost:7545')
web3 = Web3(http_provider)
eth_provider = Web3(http_provider).eth

# we'll use one of our default accounts to deploy from. every write to the chain requires a
# payment of ethereum called "gas". if we were running an actual test ethereum node locally,
# then we'd have to go on the test net and get some free ethereum to play with. that is beyond
# the scope of this tutorial so we're using a mini local node that has unlimited ethereum and
# the only chain we're using is our own local one
default_account = eth_provider.accounts[0]
print('Address of owner: ',default_account)
# every time we write to the chain it's considered a "transaction". every time a transaction
# is made we need to send with it at a minimum the info of the account that is paying for the gas
transaction_details = {
    'from': default_account,
}

# load our Solidity code into an object
with open('voting.sol') as file:
    source_code = file.readlines()

# compile the contract
compiled_code = compile_source(''.join(source_code))

# store contract_name so we keep our code DRY
contract_name = 'Voting'

#Deploy tokens

token_to_deploy = open('./vypercoin.vy','r')
token_read = token_to_deploy.read()
token_d = {'token_name':'DARF',
           'token_symbol':'DRF',
           'token_decimal':18,
           'token_initialSupply':1000000}
token_abi = compiler.mk_full_signature(token_read)
token_bytecode = '0x' + compiler.compile(token_read).hex()
token_factory = eth_provider.contract(
        abi=token_abi,
        bytecode=token_bytecode,
        )
token_constructor = token_factory.constructor(token_d['token_name'].encode('utf-8'),token_d['token_symbol'].encode('utf-8'),\
                                              token_d['token_decimal'],token_d['token_initialSupply'])
token_transaction_hash = token_constructor.transact(transaction_details)
transaction_receipt = eth_provider.getTransactionReceipt(token_transaction_hash)
token_address = transaction_receipt['contractAddress']
token_instance = eth_provider.contract(
        abi=token_abi,
        address=token_address,
        )
print(token_instance)
print('Token address:',token_address)

vyper_file = open('./postinvest.v.py','r')
vyper_text = vyper_file.read()
contract_abi = compiler.mk_full_signature(vyper_text)
contract_bytecode = '0x' + compiler.compile(vyper_text).hex()
# create a contract factory. the contract factory contains the information about the
# contract that we probably will not change later in the deployment script.
contract_factory = eth_provider.contract(
    abi=contract_abi,
    bytecode=contract_bytecode,
)
# here we pass in a list of smart contract constructor arguments. our contract constructor
# takes only one argument, a list of candidate names. the contract constructor contains
# information that we might want to change. below we pass in our list of voting candidates.
# the factory -> constructor design pattern gives us some flexibility when deploying contracts.
# if we wanted to deploy two contracts, each with different candidates, we could call the
# constructor() function twice, each time with different candidates.

contract_constructor = contract_factory.constructor(500,10,10,10,'0x00232f5C54daFd27532675D010aE8aCDe5C62696')
print('Contract ABI')
print(contract_abi)
print('Contract Bytecode')
print(contract_bytecode)

# here we deploy the smart contract. the bare minimum info we give about the deployment is which
# ethereum account is paying the gas to put the contract on the chain. the transact() function
# returns a transaction hash. this is like the id of the transaction on the chain

transaction_hash = contract_constructor.transact(transaction_details)
print(transaction_hash)

# if we want our frontend to use our deployed contract as it's backend, the frontend
# needs to know the address where the contract is located. we use the id of the transaction
# to get the full transaction details, then we get the contract address from there
transaction_receipt = eth_provider.getTransactionReceipt(transaction_hash)
contract_address = transaction_receipt['contractAddress']
print(contract_address)
contract_instance = eth_provider.contract(
    abi=contract_abi,
    address=contract_address,
    # when a contract instance is converted to python, we call the native solidity
    # functions like: contract_instance.call().someFunctionHere()
    # the .call() notation becomes repetitive so we can pass in ConciseContract as our
    # parent class, allowing us to make calls like: contract_instance.someFunctionHere()
    ContractFactoryClass=ConciseContract,
)



@app.route('/', methods=['GET', 'POST'])
def index():
    alert = ''
    candidates = {'first':23}
    get_info = contract_instance.get_ballance_of_depo()
    print(get_info)

    tx = token_instance.transact({'from': default_account}).transfer(contract_address, web3.toWei('10000','ether'))
    balance = token_instance.functions.balanceOf(default_account).call()
    symbol = token_instance.functions.symbol().call()
    print(balance)
    print(web3.toWei('10000','ether'))
    print(tx)
    print(symbol)

    return render_template('index.html', candidates=candidates, alert=alert,owner=default_account,token = token_address,smartAddress = contract_address)


if __name__ == '__main__':
    # set debug=True for easy development and experimentation
    # set use_reloader=False. when this is set to True it initializes the flask app twice. usually
    # this isn't a problem, but since we deploy our contract during initialization it ends up getting
    # deployed twice. when use_reloader is set to False it deploys only once but reloading is disabled
    app.run(debug=True, use_reloader=False)

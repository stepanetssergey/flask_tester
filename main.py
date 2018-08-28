# flask is a python web framework. it allows us to send and receive user requests
# with a minimal number of lines of non-web3py code. flask is beyond the scope of
# this tutorial so the flask code won't be commented. that way we can focus on
# how we're working with our smart contract
from flask import Flask, request, render_template

# solc is needed to compile our Solidity code
from solc import compile_source
import vyper
from vyper import compiler
from web3.auto import w3

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
transaction_receipt_token = eth_provider.getTransactionReceipt(token_transaction_hash)
token_address = transaction_receipt_token['contractAddress']
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

contract_constructor = contract_factory.constructor(500,10,10,10,token_address)
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
print('contract address:',contract_address)
contract_instance = eth_provider.contract(
    abi=contract_abi,
    address=contract_address,
    # when a contract instance is converted to python, we call the native solidity
    # functions like: contract_instance.call().someFunctionHere()
    # the .call() notation becomes repetitive so we can pass in ConciseContract as our
    # parent class, allowing us to make calls like: contract_instance.someFunctionHere()
    ContractFactoryClass=ConciseContract,
)
global contract_address_set
contract_address_set = contract_address
dict_values = {}
private_key = ''

@app.route('/setting', methods=['GET','POST'])
def setting():
    private_key_get = request.form.get('private_key')
    print(request.form.get('private_key'))
    if private_key_get is not None:
        private_key = private_key_get
        dict_values.update({'private_key':private_key})
        print(private_key)
    else:
        private_key = ''

    return render_template('settings.html', private_key=private_key)

@app.route('/', methods=['GET', 'POST'])
def index():
    get_info = contract_instance.get_ballance_of_depo()
    print(get_info)

    balance = token_instance.functions.balanceOf(default_account).call()
    symbol = token_instance.functions.symbol().call()
    print(balance)
    print(web3.toWei('10000','ether'))
    print(symbol)
    nonce = eth_provider.getTransactionCount(default_account)
    print(nonce)
    print('Ether to wei:',w3.toWei('1','ether'))
    print('Balance of contract:',token_instance.functions.balanceOf(contract_address).call())
    contract_address_from = web3.toChecksumAddress(contract_address)
    own_address = web3.toChecksumAddress(default_account)
    # address to '0x4776e07A2A155410F601e3e0bfBbA7242a35493a' 0x3143ae291f6f04d22affc9f66578eff22f47aef3

    txn = token_instance.functions.transfer(contract_address_from,w3.toWei('598.999','ether')).buildTransaction(
                                                              {
                                                               'chainId': 5777,
                                                               'gas': 1000000,
                                                               'gasPrice': w3.toWei('43', 'wei'),
                                                               'nonce': nonce, })
    print(txn)

    privat_key = 'ed17cbc7a34e2e9c487c36c02f75cf1d93569688caa69a44215c9c4bcf829d03'
    #privat_key = bytes(_key, 'utf-8')

    signed_txn = w3.eth.account.signTransaction(txn, private_key=privat_key)
    print(signed_txn)

    result = eth_provider.sendRawTransaction(signed_txn.rawTransaction)
    print(result)
    result_txn = w3.toHex(w3.sha3(signed_txn.rawTransaction))
    print(result_txn)


    return render_template('index.html', owner=default_account,token = token_address,smartAddress = contract_address)


if __name__ == '__main__':
    # set debug=True for easy development and experimentation
    # set use_reloader=False. when this is set to True it initializes the flask app twice. usually
    # this isn't a problem, but since we deploy our contract during initialization it ends up getting
    # deployed twice. when use_reloader is set to False it deploys only once but reloading is disabled
    app.run(debug=True, use_reloader=False)

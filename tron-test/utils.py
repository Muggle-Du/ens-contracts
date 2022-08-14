from tronpy import Tron, Contract
from tronpy.providers import HTTPProvider
import json

def label_hash(label):
    return keccak_256(codecs.encode(label, 'utf8')).digest()

client = Tron(HTTPProvider(endpoint_uri='http://localhost:26887'))

class Account():
    def __init__(self, private_key, address, hex):
        self.private_key = private_key
        self.address = address
        self.hex = hex

    def deploy(self, artifact_file_path, name, params):
        bytecode = ""
        abi = dict()
        with open(artifact_file_path, 'r') as f:
            data = json.load(f)
            abi = data['abi']
            for method_abi in abi:
                if method_abi['type'] == 'constructor':
                    method_abi['type'] = 'Constructor'
            bytecode = data['bytecode'][2:]

        contract = Contract(name=name, bytecode=bytecode, abi=abi)
        params = contract.constructor.encode_parameter(*params)
        contract.bytecode += params

        tx = (
            client.trx.deploy_contract(self.address, contract)
            .fee_limit(10_000_000_000)
            .build()
            .sign(self.private_key)
        )
        result = tx.broadcast().wait()
        assert result['receipt']['result'] == 'SUCCESS', f'failed to deploy the contract, tx result: {result}'
        print(f"successfully deployed {name}\n")
        return result['contract_address']

    def write_contract(self, contract, function_selector, params):
        contract = client.get_contract(contract)
        func = getattr(contract.functions, function_selector)
        tx = (
            func(*params)
            .with_owner(self.address)
            .fee_limit(10_000_000_000)
            .build()
            .sign(self.private_key)
        )
        result = tx.broadcast()
        assert result['result'] == True, f'failed to broadcast tx, tx result: {result}'
        receipt = result.wait()
        return True
    
    def read_contract(self, contract, function_selector, params):
        contract = client.get_contract(contract)
        func = getattr(contract.functions, function_selector)
        return func(*params)
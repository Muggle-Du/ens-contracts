from tronpy import Tron, Contract
from tronpy.keys import PrivateKey, to_base58check_address
from tronpy.providers import HTTPProvider
from namehash import namehash
from sha3 import keccak_256
import codecs
import json

client = Tron(HTTPProvider(endpoint_uri='http://localhost:26887'))
zero_address = to_base58check_address('0x0000000000000000000000000000000000000000')
zero_hash = "0x0000000000000000000000000000000000000000000000000000000000000000"

alice = {
    'address': 'TWubqyqYvPsmDDtCgKZfqPDtV9v1xBujSC',
    'hex': '41E5AC0BE0144561A37E23E06363BFB4B48E9BA9C0',
    'privateKey': '72622318FC143BD6D4D30F1421F8835D9ED0376B85F6780A52DABFAF291851E9',
    'publicKey': '04DE4C0EAD5E68019C2B15F320B1FD3E68E4F03A46F527CA11A549049B2FC920C216299F42EE139D31E9594DE0C7CAC4E1D76B554806229AB52B8744AACC69578E',
}
alice_priv_key = PrivateKey(bytes.fromhex(alice['privateKey']))

bob = {
    'address': 'TETodH2fmr4iUmkPgJwC98r2GHHvdVXEPS',
    'hex': '4131490D981123120A8061AC89046F694B2AB702AD',
    'privateKey': 'F1AF90763EC39E19D8E4139FDA20E6FCF6BFD042BC6BDE86E6FFEA98E953E3FF',
    'publicKey': '04FC44820944A54A358E9936624C1108E86ECE0D759DA26CCF0BFA2297B09CACD0CF52663BBCCF9061DAA9DBF04543E090D0EC27FEFBA357935338C23759D71C3D',
}
bob_priv_key = PrivateKey(bytes.fromhex(bob['privateKey']))

def label_hash(label):
    return keccak_256(codecs.encode(label, 'utf8')).digest()

bytecode = ""
abi = dict()
registry_path = '/home/toor/ens-tron/ens-contracts/artifacts/contracts/registry/ENSRegistry.sol/ENSRegistry.json'
with open(registry_path, 'r') as f:
    data = json.load(f)
    abi = data['abi']
    bytecode = data['bytecode'][2:]

ENSRegistry = Contract(name="ENSRegistry", bytecode=bytecode, abi=abi)

txn = (
    client.trx.deploy_contract(alice['address'], ENSRegistry)
    .fee_limit(10_000_000_000)
    .build()
    .sign(alice_priv_key)
)
print(txn)
result = txn.broadcast().wait()
print(result)
print('Created:', result['contract_address'])

#registry = client.get_contract(result['contract_address'])
registry = result['contract_address']

print("successfully deployed registry, now for resolver....\n\n\n")

resolver_path = '/home/toor/ens-tron/ens-contracts/artifacts/contracts/resolvers/PublicResolver.sol/PublicResolver.json'
with open(resolver_path, 'r') as f:
    data = json.load(f)
    abi = data['abi']
    bytecode = data['bytecode'][2:]

Resolver = Contract(name="Resolver", bytecode=bytecode, abi=abi)
params = Resolver.constructor.encode_parameter(registry, zero_address, alice['address'], zero_address)
Resolver.bytecode += params

txn = (
    client.trx.deploy_contract(alice['address'], Resolver)
    .fee_limit(10_000_000_000)
    .build()
    .sign(alice_priv_key)
)
print(txn)
result = txn.broadcast().wait()
print(result)
print('Created:', result['contract_address'])

# resolver = client.get_contract(result['contract_address'])
resolver = result['contract_address']

print("successfully deployed resolver, now for registrar....\n\n\n")

registrar_path = '/home/toor/ens-tron/ens-contracts/artifacts/contracts/registry/FIFSRegistrar.sol/FIFSRegistrar.json'
with open(registrar_path, 'r') as f:
    data = json.load(f)
    abi = data['abi']
    bytecode = data['bytecode'][2:]

Registrar = Contract(name="Registrar", bytecode=bytecode, abi=abi)
params = Registrar.constructor.encode_parameter(registry, namehash('test'))
Registrar.bytecode += params

txn = (
    client.trx.deploy_contract(alice['address'], Registrar)
    .fee_limit(10_000_000_000)
    .build()
    .sign(alice_priv_key)
)
print(txn)
result = txn.broadcast().wait()
print(result)
print('Created:', result['contract_address'])

# resolver = client.get_contract(result['contract_address'])
registrar = result['contract_address']

def set_subnode_owner():
    print('start to set subnode owner\n')
    contract = client.get_contract(registry)
    tx = (
        contract.functions.setSubnodeOwner(codecs.encode("", 'utf8'), label_hash('test'), registrar)
        .with_owner(alice['address'])
        .fee_limit(10_000_000_000)
        .build()
        .sign(alice_priv_key)
    )
    result = tx.broadcast()
    print(result)
    receipt = result.wait()
    print(receipt)
    print("fetch owner of 'test'\n")
    owner = contract.functions.owner(namehash('test'))
    print(owner)
    assert owner == registrar

set_subnode_owner()

def register():
    print('start to register\n')
    contract = client.get_contract(registrar)
    tx = (
        contract.functions.register(label_hash('bob'), bob['address'])
        .with_owner(bob['address'])
        .fee_limit(10_000_000_000)
        .build()
        .sign(bob_priv_key)
    )
    result = tx.broadcast()
    print(result)
    receipt = result.wait()
    print(receipt)
    print("fetch owner of 'bob.test'\n")
    contract = client.get_contract(registry)
    # owner = contract.functions.owner(namehash('test'))
    # print(owner)
    owner = contract.functions.owner(namehash('bob.test'))
    print(owner)

register()
from tronpy import Tron, Contract
from tronpy.keys import PrivateKey, to_base58check_address
from namehash import namehash
from sha3 import keccak_256
import codecs
import utils

# client = Tron(HTTPProvider(endpoint_uri='http://localhost:26887'))
zero_address = to_base58check_address('0x0000000000000000000000000000000000000000')
zero_hash = "0x0000000000000000000000000000000000000000000000000000000000000000"

alice_raw = {
    'address': 'TWubqyqYvPsmDDtCgKZfqPDtV9v1xBujSC',
    'hex': '41E5AC0BE0144561A37E23E06363BFB4B48E9BA9C0',
    'privateKey': '72622318FC143BD6D4D30F1421F8835D9ED0376B85F6780A52DABFAF291851E9',
    'publicKey': '04DE4C0EAD5E68019C2B15F320B1FD3E68E4F03A46F527CA11A549049B2FC920C216299F42EE139D31E9594DE0C7CAC4E1D76B554806229AB52B8744AACC69578E',
}
alice_priv_key = PrivateKey(bytes.fromhex(alice_raw['privateKey']))
alice = utils.Account(alice_priv_key, alice_raw['address'], alice_raw['hex'])

bob_raw = {
    'address': 'TETodH2fmr4iUmkPgJwC98r2GHHvdVXEPS',
    'hex': '4131490D981123120A8061AC89046F694B2AB702AD',
    'privateKey': 'F1AF90763EC39E19D8E4139FDA20E6FCF6BFD042BC6BDE86E6FFEA98E953E3FF',
    'publicKey': '04FC44820944A54A358E9936624C1108E86ECE0D759DA26CCF0BFA2297B09CACD0CF52663BBCCF9061DAA9DBF04543E090D0EC27FEFBA357935338C23759D71C3D',
}
bob_priv_key = PrivateKey(bytes.fromhex(bob_raw['privateKey']))
alice = utils.Account(bob_priv_key, bob_raw['address'], bob_raw['hex'])

registry_path = '/home/toor/ens-tron/ens-contracts/artifacts/contracts/registry/ENSRegistry.sol/ENSRegistry.json'
resolver_path = '/home/toor/ens-tron/ens-contracts/artifacts/contracts/resolvers/PublicResolver.sol/PublicResolver.json'
registrar_path = '/home/toor/ens-tron/ens-contracts/artifacts/contracts/registry/FIFSRegistrar.sol/FIFSRegistrar.json'

registry = alice.deploy(registry_path, 'ENSRegistry', [])
resolver = alice.deploy(resolver_path, 'Resolver', [registry, zero_address, alice.address, zero_address])
registrar = alice.deploy(registrar_path, 'Registrar', [registry, namehash('test')])

# set .test tld for registrar
alice.write_contract(registry, 'setSubnodeOwner', [codecs.encode("", 'utf8'), utils.label_hash('test'), registrar])
subnode_owner = alice.read_contract(registry, 'owner', [namehash('test')])
assert subnode_owner == registrar, f'failed to set .test tld for registrar'

# register bob.test for bob
bob.write_contract(registrar, 'register', [utils.label_hash('bob'), bob['address']])
name_owner = alice.read_contract(registry, 'owner', [namehash('bob.test')])
assert name_owner == bob.address, f'bob failed to register the bob.test name'

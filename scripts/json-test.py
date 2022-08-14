import json

with open('/home/toor/ens-tron/ens-contracts/artifacts/contracts/registry/ENSRegistry.sol/ENSRegistry.json', 'r') as f:
    data = json.load(f)
    print(data['bytecode']) 
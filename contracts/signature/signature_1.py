import os
import asyncio
import sys
import json

sys.path.append('./')

from utils import deploy_account, print_n_wait, mission_statement, get_evaluator, fund_account, get_client
from starknet_py.net.client import Client
from starkware.starknet.public.abi import get_selector_from_name
from starkware.crypto.signature.signature import sign
from starkware.crypto.signature.fast_pedersen_hash import pedersen_hash

with open("./hints.json", "r") as f:
  data = json.load(f)

async def main():
    mission_statement()
    print("\t 1) find the first two EIP numbers discussing account abstraction")
    print("\t 2) deploy account contract with an '__execute__' entrypoint")
    print("\t 3) use the private key to sign the values using the Stark curve")
    print("\t 4) invoke the validator check with the signature in the tx_info field\n")

    #
    # MISSION 1
    #
    INPUT_1 = 2938
    INPUT_2 = 4337
    print(
        "First account abstraction EIP: \n\thttps://eips.ethereum.org/EIPS/eip-{}"
        .format(INPUT_1))
    print(
        "Second account abstraction EIP: \n\thttps://eips.ethereum.org/EIPS/eip-{}\u001b[0m\n"
        .format(INPUT_2))

    #
    # MISSION 2
    #
    client = get_client()

    sig1, sig1_addr = await deploy_account(client, data['SIGNATURE_1'])

    reward_account = await fund_account(sig1_addr)
    if reward_account == "":
      print("Account must have ETH to cover transaction fees")
      return
      
    _, evaluator_address = await get_evaluator(client)
    
    #
    # MISSION 3
    #
    hash = pedersen_hash(INPUT_1, INPUT_2)
    hash_final = pedersen_hash(hash, sig1_addr)
    signature = sign(hash_final, data['PRIVATE_KEY'])

    prepared = sig1.functions["__execute__"].prepare(
        contract_address=evaluator_address,
        selector=get_selector_from_name("validate_signature_1"),
        calldata_len=3,
        calldata=[INPUT_1, INPUT_2, reward_account])
    
    #
    # MISSION 4
    #
    invocation = await prepared.invoke(signature=signature, max_fee=data['MAX_FEE'])

    await print_n_wait(client, invocation)


asyncio.run(main())

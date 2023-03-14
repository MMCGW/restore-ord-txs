import json
import subprocess
import sys


def run_ord(args: list):
    command = ['ord'] + args
    try:
        output_bytes = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        error_msg = e.output.decode().strip('error: ')
        print(error_msg)
        raise Exception(error_msg)

    output_str = output_bytes.decode('utf-8')

    return output_str


def run_bitcoin_cli(args: list):
    command = ['bitcoin-cli'] + args
    try:
        output_bytes = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        error_msg = e.output.decode().strip('error: ')
        print(error_msg)
        raise Exception(error_msg)

    output_str = output_bytes.decode('utf-8')

    return output_str


def get_cardinal_inputs(wallet_name: str, amount: float):
    unspents = run_bitcoin_cli([f'-rpcwallet={wallet_name}', 'listunspent'])
    unspents = json.loads(unspents)
    if wallet_name == 'ord':
        inscriptions = run_ord(['wallet', 'inscriptions'])
    else:
        inscriptions = run_ord(['--wallet', wallet_name, 'wallet', 'inscriptions'])
    inscriptions = json.loads(inscriptions)

    locations = []
    for i in inscriptions:
        locations.append(str(i['location'].split(":")[0]) + ':' + str(i['location'].split(":")[1]))

    cardinal_inputs = []
    _amount = 0
    for tx in unspents:
        utxo = str(tx['txid']) + ":" + str(tx['vout'])
        if utxo not in locations:  # check if its inscription
            if _amount < amount and int(tx['confirmations']) >= 1:
                cardinal_inputs.append({"txid": f"{tx['txid']}", "vout": int(tx['vout'])})
    return cardinal_inputs


def get_stuck_transaction_inouts(txid: str, wallet_name: str):

    get_tx = run_bitcoin_cli([f'-rpcwallet={wallet_name}', 'gettransaction', txid])
    tx = json.loads(get_tx)
    tx_hex = tx['hex']

    decode_hex = run_bitcoin_cli([f'-rpcwallet={wallet_name}', 'decoderawtransaction', f"{tx_hex}"])
    decode_hex = json.loads(decode_hex)

    inputs = []
    for item in decode_hex['vin']:
        inputs.append({"txid": item['txid'], "vout": item['vout']})

    output_amounts = []
    for item in decode_hex['vout']:
        output_amounts.append(float(item['value']))

    return inputs, output_amounts


def get_new_address(wallet_name: str):
    if wallet_name == 'ord':
        wallet_address = run_ord(['wallet', 'receive'])
    else:
        wallet_address = run_ord(['--wallet', f'{wallet_name}', 'wallet', 'receive'])

    wallet_address = json.loads(wallet_address)
    return wallet_address["address"]


def has_min_funds(wallet_name: str):
    if wallet_name == 'ord':
        cardinal = run_ord(['wallet', 'balance'])
    else:
        cardinal = run_ord(['--wallet', f'{wallet_name}', 'wallet', 'balance'])
    cardinal = json.loads(cardinal)

    if int(cardinal['cardinal']) >= 15000:
        return True
    else:
        return False


def restore_tx(wallet_name: str, txid: str, fee_rate: int, fee_amount):
    stuck_inouts = get_stuck_transaction_inouts(txid, wallet_name)
    inputs = stuck_inouts[0]
    fee_inputs = get_cardinal_inputs(wallet_name, fee_amount)
    for item in fee_inputs:
        inputs.append(item)

    recipients = []
    for output_amount in stuck_inouts[1]:
        recipients.append({f"{get_new_address(wallet_name)}": output_amount})

    if has_min_funds(wallet_name):
        recipients.append({f"{get_new_address(wallet_name)}": fee_amount})

    inputs = json.dumps(inputs)
    outputs = json.dumps(recipients)
    options = json.dumps({"fee_rate": fee_rate,
                          "subtractFeeFromOutputs": [len(recipients) - 1],
                          "changeAddress": get_new_address(wallet_name),
                          "changePosition": len(recipients)})
    rawtxn = run_bitcoin_cli([f'-rpcwallet={wallet_name}', 'walletcreatefundedpsbt', f"{inputs}", f'{outputs}', '0', f"{options}"])
    rawtxn = json.loads(rawtxn)
    process = run_bitcoin_cli([f'-rpcwallet={wallet_name}', 'walletprocesspsbt', rawtxn['psbt']])
    process = json.loads(process)
    finalizes = run_bitcoin_cli([f'-rpcwallet={wallet_name}', 'finalizepsbt', process['psbt']])
    finalizes = json.loads(finalizes)
    print(f'Can complete? {finalizes["complete"]}')
    broadcast = run_bitcoin_cli([f'-rpcwallet={wallet_name}', 'sendrawtransaction', finalizes['hex']])
    print(f'New Txid: {broadcast}')


if __name__ == '__main__':
    args = sys.argv[1:]
    wallet_name = args[0]
    txid = args[1]
    fee_rate = args[2]
    try:
        fee_amount = args[3]
    except Exception:
        fee_amount = 0.00015

    restore_tx(wallet_name, txid, int(fee_rate), fee_amount)


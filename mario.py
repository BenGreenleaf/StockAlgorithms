key = '0x1f46cb1fa5889b308e1847c881d1905c754077c8618e948679ad83a4fa0b210e'

from hyperliquid.utils import constants

import eth_account
from eth_account.signers.local import LocalAccount
import math

from hyperliquid.exchange import Exchange
from hyperliquid.info import Info

from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/', methods=['POST'])

def webhook():
    if request.method == 'POST':
        try:
            data = str(request.data)

            if data == "b'long'":
                closeTrade()
                openTrade(True)
            elif data == "b'short'":
                closeTrade()
                openTrade(False)

            return 'success', 200
        except:
            print("Data Interpretation Error")
            
    else:
        print(request.method)
        abort(400)


def setup(base_url=None, skip_ws=False):
    account: LocalAccount = eth_account.Account.from_key(key)
    address = '0xAd06A83dc090C8d37Fd8c22769AE3531c3a6B2AF'
    if address == "":
        address = account.address
    print("Running with account address:", address)
    if address != account.address:
        print("Running with agent address:", account.address)
    info = Info(base_url, skip_ws)
    user_state = info.user_state(address)
    margin_summary = user_state["marginSummary"]
    accountValue = float(margin_summary["accountValue"])
    if float(margin_summary["accountValue"]) == 0:
        print("Not running the example because the provided account has no equity.")
        url = info.base_url.split(".", 1)[1]
        error_string = f"No accountValue:\nIf you think this is a mistake, make sure that {address} has a balance on {url}.\nIf address shown is your API wallet address, update the config to specify the address of your account, not the address of the API wallet."
        raise Exception(error_string)
    exchange = Exchange(account, base_url, address=address)
    print(user_state)
    return address, info, exchange, accountValue

def openTrade(is_buy):
    address, info, exchange, val = setup(constants.TESTNET_API_URL, skip_ws=True)
    coin = "SOL"
    sz = 1

    data = float(info.l2_snapshot(coin)['levels'][0][0]['px'])
    sz = math.floor((val/data)*100)/100
    
    order_result = exchange.market_open(coin, is_buy, sz, None)


def closeTrade():
    try:
        address, info, exchange, val = setup(constants.TESTNET_API_URL, skip_ws=True)
        coin = "SOL"
        sz = 1

        data = float(info.l2_snapshot(coin)['levels'][0][0]['px'])
        sz = math.floor((val/data)*100)/100
        
        order_result = exchange.market_close(coin, sz, None)
    except:
        print("Error Closing")
        pass

def main():
    address, info, exchange, val = setup(constants.TESTNET_API_URL, skip_ws=True)
    coin = "SOL"
    is_buy = True
    sz = 0.2
    bpx = 169
    spx = 3419.3

    print(f"We try to Market {'Buy' if is_buy else 'Sell'} {sz} {coin}.")
    #print(round(bpx*0.99,2))
    order_result = exchange.market_open(coin, is_buy, sz, None)
    #order_result = exchange.order(coin, is_buy, sz, bpx, {'trigger':{'isMarket':True, 'tpsl':'sl', 'triggerPx': round(bpx*0.99,2)}})
    '''if order_result["status"] == "ok":
        for status in order_result["response"]["data"]["statuses"]:
            try:
                filled = status["filled"]
                print(f'Order #{filled["oid"]} filled {filled["totalSz"]} @{filled["avgPx"]}')
            except KeyError:
                print(f'Error: {status["error"]}')

        print("We wait for 2s before closing")
        time.sleep(10)

        print(f"We try to Market Close all {coin}.")
        order_result = None
        while order_result == None:
            print("Attempt")
            order_result = exchange.market_close(coin, sz, None)
        if order_result is not None and order_result["status"] == "ok":
            for status in order_result["response"]["data"]["statuses"]:
                try:
                    filled = status["filled"]
                    print(f'Order #{filled["oid"]} filled {filled["totalSz"]} @{filled["avgPx"]}')
                except KeyError:
                    print(status)
                    print(f'Error: {status["error"]}')
'''

if __name__ == '__main__':
    app.run(port=80)
import json

import eth_account
from eth_account.signers.local import LocalAccount
import websockets, asyncio
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

import time

leverage = 30

account: LocalAccount = eth_account.Account.from_key("0xd95bf81dc06a67fe753cbee57bbc2e8a1f83d82e9c5d8f976c6adbe9265da11a")
print("Running with account address:", account.address)
info = Info(account, constants.TESTNET_API_URL)
exchange = Exchange(account, constants.TESTNET_API_URL)

print(exchange.update_leverage(leverage, "ETH"))

inTrade = False

upperTps = []
lowerTps = []


async def subscribe_to_market_data():
    async with websockets.connect("wss://api.hyperliquid-testnet.xyz/ws") as ws:
        subscription_message = {
            "method": "subscribe",
            "subscription": {
                "type": "l2Book",
                "coin": "ETH",
            }
        }

        await ws.send(json.dumps(subscription_message))

        async for message in ws:
            message_data = json.loads(message)
            if message_data['channel'] == 'subscriptionResponse':
                print("Subscription Successful")
            elif message_data['channel'] == 'l2Book':
                #print("Order Book Update: ", message_data['data'])
                sells = message_data['data']['levels'][0][0]
                buys = message_data['data']['levels'][1][0]

                sPrice = round(float(sells['px'])-0.2,1)
                bPrice = round(float(buys['px'])+0.2,1)

                if inTrade == False:

                    upperTp = round(bPrice * 1.0015,1)
                    upperSl = round(bPrice * 1.001,1)

                    lowerTp = round(sPrice * (1-0.0015),1)
                    lowerSl = round(sPrice * (1-0.001),1)

                    inTrade == True

                    upperTps.append(upperTp)
                    lowerTps.append(lowerTp)
                    await trade(bPrice, upperTp, upperSl, sPrice, lowerTp, lowerSl)

                toSells = []
                toBuys = []
                for i in upperTps:
                    if sPrice >= i:
                        toSells.append(i)
                        print("TP IS "+str(i), "CLOSE LONG FOR "+str(sPrice))
                
                for i in lowerTps:
                    if bPrice <= i:
                        toBuys.append(i)
                        print("TP IS "+str(i), "CLOSE SHORT FOR "+str(sPrice))

                for i in toSells:
                    await individualTradeClose(False, i)
                    toSells.remove(i)
                    upperTps.remove(i)

                for i in toBuys:
                    await individualTradeClose(True, i)
                    toBuys.remove(i)
                    lowerTps.remove(i)
                
            else:
                pass

async def individualTradeClose(isBuy, price):
    order_result1 = exchange.order("ETH", isBuy, 0.005, price, {"limit": {"tif": "Gtc"}}, True)
    print(order_result1, "TAKE PROFIT", isBuy)


async def trade(buy, upperProfit, upperStop, sell, lowerProfit, lowerStop):
    print(buy, upperProfit, upperStop, sell, lowerProfit, lowerStop)
    order_result1 = exchange.order("ETH", True, 0.005, buy, {"limit": {"tif": "Ioc"}})
    order_result2 = exchange.order("ETH", False, 0.005, sell, {"limit": {"tif": "Ioc"}})
    print(order_result1, order_result2)
    print("\n")

    fail1 = False
    fail2 = False

    if 'error' in order_result1['response']['data']['statuses'][0].keys():
        fail1 = True
    if 'error' in order_result2['response']['data']['statuses'][0].keys():
        fail2 = True

    if fail1 == True and fail2 == False:
        res = exchange.order("ETH", False, 0.005, sell-1, {"limit": {"tif": "Gtc"}}, True)
        print("Buy Failed")
        print(res)
    
    if fail1 == False and fail2 == True:
        res = exchange.order("ETH", True, 0.005, sell+1, {"limit": {"tif": "Gtc"}}, True)
        print("Sell Failed")
        print(res)

    elif fail1 == True and fail2 == True:
        print("Both Failed")

    else:
        res2 = exchange.order("ETH", False, 0.005, upperStop, {"limit": {"tif": "Gtc"}}, True)

        res4 = exchange.order("ETH", True, 0.005, lowerStop, {"limit": {"tif": "Gtc"}}, True)
        print(res2, res4, "STOP LOSSES")


asyncio.get_event_loop().run_until_complete(subscribe_to_market_data())    

#g_b | REAL INFO
#0xa1EcDBE8F4B87F239baf1CfC31f1f653dfb7cD50
#0x613cc42e6d06c15f585c49a06078c4914b3c0289cb2afbdc822b7eac755944ed

#g_b_test
#0x90b997D02eb99B4739fc1aae84a2f8F5780Ea206
#0xd95bf81dc06a67fe753cbee57bbc2e8a1f83d82e9c5d8f976c6adbe9265da11a


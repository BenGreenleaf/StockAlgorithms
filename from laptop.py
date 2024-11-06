from alpaca.trading.client import TradingClient
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates

leverage = 100

key = "PKU54WYBEYN4XNBRZBEQ"
secret = "Gd4cBZwOg0x3IiOBHFYv9MlwXupbSNNDDMRnA7LA"

trading_client = TradingClient(key, secret, paper=True)
data_client = CryptoHistoricalDataClient(api_key=key, secret_key=secret)


request_params = CryptoBarsRequest(
                        symbol_or_symbols=["BTC/USD"],
                        timeframe=TimeFrame(15, TimeFrameUnit.Minute),
                        start=(datetime.datetime.now()- datetime.timedelta(days=(15))) #455 Simulation is based off 15 days of analytical analysis
                 )

bars = data_client.get_crypto_bars(request_params)
print(bars)
l = bars["BTC/USD"]

fee = 0.02/100

def simulation(point, offset):
    p = 0
    avgDiff = 0
    avgDistance = 0
    n = 0
    ws = 0
    ls = 0
    change = True
    for i in l:
        try:
            if change == True:
                open = i.open
                upperTp = open+offset+point
                upperSl = open+offset

                lowerSl = open-offset
                lowerTp = open-offset-point

            if i.high >= upperTp and i.low > lowerSl:
                ws += 1
                p += ((upperTp-open)-(open-lowerSl))/open
                change = True

            elif i.low <= lowerTp and i.high < upperSl:
                ws += 1
                p += ((open-lowerTp)-(upperSl-open))/open
                change = True

            elif (i.high > upperSl and i.low < lowerSl):
                ls += 1
                p -= ((upperTp-lowerSl)/open)
                change = True
            else:
                change = False

            if change == True:
                p -= fee

            avgDiff += abs((i.high-i.open)-(i.open-i.low))
            avgDistance += (i.high-i.open)+(i.open-i.low)
            n+=1
        except Exception as e:
            print(e)

    avgDiff = avgDiff/n
    avgDistance = avgDistance/(n*2)
    winRate = ws/(ws+ls)
    winRate = winRate * 100
    return(p, winRate)

max = -111111
bestStrat = []

for i in range(0, 500):
    i = (i/5)+80
    for j in range(0, 3000):
        j = j/10
        res, winRate = simulation(j, i)
        print(i, j, res, winRate)
        if res > max:
            max = res
            bestStrat = [i, j, winRate]

print(max, bestStrat)

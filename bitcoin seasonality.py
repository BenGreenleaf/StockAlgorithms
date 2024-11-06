from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetAssetsRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import datetime, alpaca
import matplotlib.pyplot as plt
import pandas as pd
import statistics, time

key = "PKDM3BFYPYB4G72X1764"
secret = "75nZSolJ51hxqSYRErjaORKi933H8gmRSCVyAXqm"

data_client = alpaca.data.historical.StockHistoricalDataClient(api_key=key, secret_key=secret)

request_params = alpaca.data.requests.StockBarsRequest(
                    symbol_or_symbols=["SPY"],
                    timeframe=TimeFrame(15, TimeFrameUnit.Minute),
                    start=datetime.datetime(2023,1,1),
                    end=datetime.datetime(2023, 12, 23)
)

bars = data_client.get_stock_bars(request_params)
l = bars["SPY"]

print(len(l))
print("Data Got")

def sim(a, b, bollingerLength, bollingerHeight):

    openTradesMax = 0
    tps = []
    sls = []
    avgL = []
    avg = 0
    p = 0
    ws = 0
    ls = 0

    for i in l:

        avgL.append(i.close)
        bbLower = -1
        if len(avgL) > bollingerLength:
            avgL.pop(0)
            avg = sum(avgL)/len(avgL)
            bbLower = avg - (bollingerHeight*statistics.stdev(avgL))


        if i.close < bbLower:
            tp = i.close*(1+(a/100))
            sl = i.close*(1-(b/100))
            tps.append(tp)
            sls.append(sl)

        
        removedtp = []
        removedsl = []
        for j in range(0,len(tps)):
            if i.high > tps[j]:
                removedtp.append(tps[j])
                removedsl.append(sls[j])
                p += a
                ws += 1

        for j in removedtp:
            tps.remove(j)
        for j in removedsl:
            sls.remove(j)

        removedtp = []
        removedsl = []
        for j in range(0,len(sls)):
            if i.low < sls[j]:
                removedtp.append(tps[j])
                removedsl.append(sls[j])
                p -= b
                ls += 1

        for j in removedtp:
            tps.remove(j)
        for j in removedsl:
            sls.remove(j)

        if len(tps) > openTradesMax:
            openTradesMax = len(tps)

    if ws == 0:
        wRate = 0
    else:
        wRate = (ws/(ws+ls))

    if openTradesMax > 0:
        p = p/openTradesMax

    return(p, openTradesMax, wRate, ws, ls)

max = 0
best = []


for k in range(10, 20):
    k = k/10
    t = time.time()
    for m in range(10,101):
        m = m/10

        for n in range(1, 11):
            n = n*10

            for o in range(1,5):
                res, tradeNum, wRate, ws, ls = sim(k,m, n, o)
                if res > max:
                    max = res
                    best = [k,m, n, o, tradeNum, wRate, ws, ls]

                    print(max, best)
            
        print(m)
    print(time.time()-t)
    print(str(k*10)+"%", max, best)
    
print(best, max)

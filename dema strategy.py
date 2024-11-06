import csv
import re
from functools import reduce
from dateutil import parser
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetAssetsRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

key = "PKW3R22AFALB6UG4TV4R"
secret = "syAFNJBlMzv7F882RAwa4KdPGRc7aq0pteXcposi"

data_client = CryptoHistoricalDataClient(api_key=key, secret_key=secret)

request_params = CryptoBarsRequest(
                        symbol_or_symbols=["ETH/USD"],
                        timeframe=TimeFrame(3, TimeFrameUnit.Minute),
                        start=datetime(2023, 1, 1)
                 )

bars = data_client.get_crypto_bars(request_params)['ETH/USD']

avgHeight = 0
avgBreak = 0
slbreak = 0
proportion = 0.25

portfolio = 100

inTrade = False

slBreach = False
tpBreach = False
entry = 0

xs = []
ys = []
n = 0

avgChange = 0

print(proportion*(2.41/2) - (proportion-0.2)*(2.41/2))

for i in bars:
    n += 1
    avgHeight += i.high - i.low
    if inTrade == False:
        entry = i.open
        breakup = i.open + proportion*(2.41/2)
        breakdown = i.open - proportion*(2.41/2)

        slbreakup = i.open + (proportion-0.2)*(2.41/2)
        slbreakdown = i.open - (proportion-0.2)*(2.41/2)

    if i.high > breakup or i.low < breakdown:
        avgBreak += 1
        tpBreach = True
        if i.high > breakup:
            portfolio += ((breakup - entry)/entry)*portfolio
        else:
            portfolio += ((entry - breakdown)/entry)*portfolio

    if i.high > slbreakup or i.low < slbreakdown:
        slbreak += 1
        slBreach = True
        if i.high > slbreakup:
            portfolio -= ((slbreakup - entry)/entry)*portfolio
        else:
            portfolio -= ((entry - slbreakdown)/entry)*portfolio

    if tpBreach == True and slBreach == True:
        inTrade = False
        slBreach = False
        tpBreach = False

    xs.append(n/480)
    ys.append(portfolio)


avgHeight = avgHeight/len(bars)
avgBreak = (avgBreak/len(bars))*100
slbreak = (slbreak/len(bars))*100
print(avgHeight, avgBreak, (slbreak-avgBreak), len(bars))

plt.plot(xs, ys)
plt.show()
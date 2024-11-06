from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import datetime
import matplotlib.pyplot as plt
import numpy as np 

key = "PKTMWCAGZ0U9XTS7DKBO"
secret = "aptQgqeZRcH1ARtUdcAS2GmMnjzdPXm8lPs7IfIM"

data_client = StockHistoricalDataClient(api_key=key, secret_key=secret)
ticker = 'TSLA'
# Change the symbol to TSLA
request_params = StockBarsRequest(
    symbol_or_symbols=[ticker],
    timeframe=TimeFrame(15, TimeFrameUnit.Minute),
    start=datetime.datetime(2022, 12, 20),
    end=datetime.datetime(2023, 12, 20)
)

bars = data_client.get_stock_bars(request_params)
bars = bars[ticker]

# Remove consecutive bars with the same closing price
bars = [bar for i, bar in enumerate(bars) if i == 0 or bar.close != bars[i - 1].close]

# Extract closing prices and dates from the bars object
closing_prices = [bar.close for bar in bars]
window = []
SMA = []
STD = []
UpperBand = []
LowerBand = []
Multiplier = 2
for x in closing_prices:
    window.append(x)
    if(len(window) > 20):
        window.pop(0)
    SMA.append(np.mean(window))  # Use numpy's mean function for efficiency
    STD.append(np.std(window))
    UpperBand.append(SMA[-1] + (Multiplier * STD[-1]))
    LowerBand.append(SMA[-1] - (Multiplier * STD[-1]))
breakout = 0
opportunities = []
orders = []
closed = []
peak = 0
portfolio = 20000
restrictedPortfolio = False
restrictedStart = 0 
restrictedEnd = 0  #Capital value available at the end
initial = portfolio
limiting = False
# Iterating through all our bars
for x in range(0,len(closing_prices)):
    if len(orders) > peak:
        peak = len(orders)
    for y in reversed(range(len(orders))):
        # Sell if we have exceeded initial SMA and current price is within bands
        if closing_prices[x] > orders[y]['sma'] and closing_prices[x] > LowerBand[x]:
            if not restrictedPortfolio: 
                restrictedEnd += closing_prices[x]
            else:
                portfolio+=closing_prices[x]
            # Append it as a closed position
            closed.append({'enter': orders[y]['price'], 'exit': closing_prices[x]})
            # Remove our position
            orders.pop(y)

    # Check if we have an upper breakout
    if closing_prices[x] > UpperBand[x]:
        # print(f'Breakout X from UpperBand Price: $ {closing_prices[x]} UpperBand: ${UpperBand[x]}')
        breakout+=1
        opportunities.append(bars[x])
    # Check if we have a lower breakout
    elif closing_prices[x] < LowerBand[x]:
        if portfolio > closing_prices[x] and restrictedPortfolio:
            portfolio -= closing_prices[x]
            orders.append({ 'price': closing_prices[x], 'sma': SMA[x] })
        elif not restrictedPortfolio:
            if restrictedEnd < closing_prices[x]:
                restrictedStart += closing_prices[x]
            else:
                restrictedEnd -= closing_prices[x]
            orders.append({ 'price': closing_prices[x], 'sma': SMA[x] })
        else: 
            limiting = True
        # print(f'Breakout X from LowerBand Price: ${closing_prices[x]} LowerBand: ${LowerBand[x]}')
        breakout+=1
        opportunities.append(bars[x])
openvalue = 0
for x in range(0,len(orders)):
    openvalue+=orders[x]['price']
if restrictedPortfolio:
    print(f'Limiting: {limiting}')
    print(f'Portfolio: ${portfolio}')
    print(f'ROI: {((100/initial)*(openvalue+portfolio))-100}%')
else:
    print(f'Portfolio: ${restrictedEnd}')
    print(f'ROI: {((100/restrictedStart)*(restrictedEnd+openvalue))-100}%')
print(f'Open Value: ${openvalue}')
print(f'Peak Positions: {peak}')
# print(f'Closed Positions: {closed}')
# print(f'Active Positions: {orders}')
print(f'Breakout Count: {breakout}')
for x in range(0,len(opportunities)):
    opportunities[x] = opportunities[x].timestamp.date()
dates = []
for x in range(0, len(opportunities)):
    if opportunities[x] not in dates:
        dates.append(opportunities[x])
print(len(dates))
# Plot bars
plt.plot(closing_prices)
plt.plot(SMA)
plt.plot(UpperBand)
plt.plot(LowerBand)
# Set labels and title
plt.xlabel('Bar Number')
plt.ylabel('Closing Price')
plt.title('TSLA Stock Closing Prices')

# Show the plot
plt.show()

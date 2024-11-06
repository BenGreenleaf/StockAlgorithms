from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
import time, datetime
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, OrderClass, OrderType, TimeInForce
from alpaca.data.requests import StockLatestTradeRequest

# paper=True enables paper trading
trading_client = TradingClient('PKMTEPCJXNNDHU42DGLB', 'HxJqXWGajp0fZveuUd1jL5Bi139iPltmWTtYdcUP', paper=True)
data_client = StockHistoricalDataClient('PKMTEPCJXNNDHU42DGLB', 'HxJqXWGajp0fZveuUd1jL5Bi139iPltmWTtYdcUP')


DRIVER_PATH = 'D:/Downloads/chromedriver_win32/chromedriver.exe'

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])


driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)


def getChanges():

    driver.get('https://hedgefollow.com/insider-trading-tracker')

    time.sleep(1)

    click = driver.find_element(By.CSS_SELECTOR, '#dgHolders > thead > tr > th:nth-child(6)')
    click.click()

    time.sleep(1)

    symbols = {}
    table_id = driver.find_element(By.CSS_SELECTOR, '#dgHolders > tbody')
    rows = table_id.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
    for row in rows:
        # Get the columns (all the column 2)        
        col = row.find_elements(By.TAG_NAME, "td") #note: index start from 0, 1 is col 2
        
        symbol = col[0].text
        manager = col[1].find_element(By.TAG_NAME, 'a').text
        type = col[2].text
        transactionValue = col[5].text
        date = col[-1].text

        transactionValue = transactionValue.strip("$M")
        transactionValue = float(transactionValue)*1000000

        ds = date.split("-")
        date = datetime.date(int(ds[0]), int(ds[1]), int(ds[2]))

        ddiff = (datetime.date.today()-date).days

        dt = datetime.datetime.now().weekday()
        
        if dt == 0:
            ddiff -= 3
        elif dt == 5:
            ddiff -= 1
        elif dt == 6:
            ddiff -= 2

        if ddiff == 0:
            try:
                symbols[symbol].append({'symbol':symbol, 'insider':manager, 'type':type, 'value':transactionValue, 'date':date})
            except:
                symbols[symbol] = [{'symbol':symbol, 'insider':manager, 'type':type, 'value':transactionValue, 'date':date}]
    
    return(symbols)

resp = getChanges()
print(resp)

for i in range(0,len(resp)):
    symbol = list(resp.keys())[i]
    val = list(resp.values())[i]

    total = 0
    for j in val:
        if j['type'] == "Buy":
            total += j['value']
        if j['type'] == "Sell":
            total -= j['value']

    if total < 0:
        type = "SELL"
    elif total >= 0:
        type = "BUY"

    try:

        multisymbol_request_params = StockLatestTradeRequest(symbol_or_symbols=[symbol])
        price = data_client.get_stock_latest_trade(multisymbol_request_params)[symbol].price

        if type == "SELL":
            type = OrderSide.SELL
            sl = round(price*1.01, 2)
            tp = round(price*0.985, 2)
        elif type == "BUY":
            type = OrderSide.BUY
            tp = round(price*1.015,2)
            sl = round(price*0.99, 2)

        market_order_data = MarketOrderRequest(
                            symbol=symbol,
                            side=type,
                            type=OrderType('market'),
                            qty=1,
                            time_in_force=TimeInForce('gtc'),
                            take_profit=TakeProfitRequest(limit_price=tp),
                            stop_loss=StopLossRequest(stop_price=sl),
                            order_class=OrderClass('bracket'),
                            )
    

        # Market order
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                    )
    
    except Exception as e:
        print(e)
        print(symbol+" Failed")
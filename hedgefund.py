from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
import time
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# paper=True enables paper trading
trading_client = TradingClient('PK4UXGAUNUFV5HQZLBW8', 'uezBgAciDJ40S3eGRNvDOoKVG4g8cTcPBrmbDhfo', paper=True)


DRIVER_PATH = 'D:/Downloads/chromedriver_win32/chromedriver.exe'

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])


driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)


def getChanges():

    driver.get('https://hedgefollow.com/latest-activity.php')

    time.sleep(1)

    table = driver.find_element(By.XPATH, '/html/body/section/div/div[1]/div[2]/div[1]/table/tbody')

    '''for row in table.find_elements(By.CLASS_NAME, 'tr'):
        print(row)
        for cell in row.find_elements(By.CLASS_NAME, 'td'):
            print(cell)
            print("a")'''


    symbols = {}
    table_id = driver.find_element(By.CSS_SELECTOR, '#hedge_fund_tracker > tbody')
    rows = table_id.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
    for row in rows:
        # Get the columns (all the column 2)        
        col = row.find_elements(By.TAG_NAME, "td") #note: index start from 0, 1 is col 2
        
        hedgefund = col[0].text
        manager = col[1].text
        symbol = col[2].text
        perOfPortfolio = col[3].text
        change = col[4].text

        try:
            percent = change.split('(')
            total = percent[1]

            total = total.replace(')', '') 

            if 'M' in total:
                total = total.replace('M', '') 
                total = float(total)*1000000
            elif 'k' in total:
                total = total.replace('k', '')
                total = float(total)*1000

        except:
            total = 0
        
        symbols[symbol] = total
    
    return(symbols)

resp = getChanges()
print(resp)

time.sleep(500)
for i in range(0,len(resp)):
    symbol = list(resp.keys())[i]
    val = list(resp.values())[i]
    
    if val > 0:

        try:

            market_order_data = MarketOrderRequest(
                                symbol=symbol,
                                notional=val,
                                side=OrderSide.BUY,
                                time_in_force=TimeInForce.DAY
                                )

            # Market order
            market_order = trading_client.submit_order(
                            order_data=market_order_data
                        )
        
        except:

            print(symbol+" Failed")
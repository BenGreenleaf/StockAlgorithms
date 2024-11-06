from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass, OrderType

key = "PKW3R22AFALB6UG4TV4R"
secret = "syAFNJBlMzv7F882RAwa4KdPGRc7aq0pteXcposi"

trading_client = TradingClient(key, secret)
data_client = StockHistoricalDataClient(key, secret)

multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=["AAPL"])

latest_multisymbol_quotes = data_client.get_stock_latest_quote(multisymbol_request_params)

ask = latest_multisymbol_quotes["AAPL"].ask_price
bid = latest_multisymbol_quotes["AAPL"].bid_price

print(latest_multisymbol_quotes)
print(ask,bid)

# preparing order data
market_order_data_buy = MarketOrderRequest(
                      symbol="AAPL",
                      qty=1,
                      side=OrderSide.BUY,
                      type=OrderType.MARKET,
                      time_in_force = TimeInForce.DAY,
                      order_class=OrderClass.BRACKET,
                      take_profit=TakeProfitRequest(limit_price=round(ask+0.15,2)),
                      stop_loss=StopLossRequest(stop_price=round(ask-0.10,2))
                  )

market_order_data_sell = MarketOrderRequest(
                      symbol="AAPL",
                      qty=1,
                      side=OrderSide.SELL,
                      type=OrderType.MARKET,
                      time_in_force = TimeInForce.DAY,
                      order_class=OrderClass.BRACKET,
                      take_profit=TakeProfitRequest(limit_price=round(bid-0.15,2)),
                      stop_loss=StopLossRequest(stop_price=round(bid+0.10,2))
                  )

# Market order
market_order_buy = trading_client.submit_order(
                order_data=market_order_data_buy
                )
market_order_sell = trading_client.submit_order(
                order_data=market_order_data_sell
                )

print(market_order_buy, market_order_sell)
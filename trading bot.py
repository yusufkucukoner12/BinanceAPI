import requests
import time
import hashlib
import hmac
import websocket 
import json
from urllib.parse import urlencode

class Trade:
    stop_orders = []
    order_id = ""


    def __init__(self, symbol, side, type, quantity,  leverage, in_price, margin_type, close_position):
        self.symbol = symbol
        self.side = side
        self.leverage = leverage 
        self.quantity = quantity
        self.in_price = in_price
        self.margin_type = margin_type
        self.close_position = close_position
        self.type = type
        
        
        response = requests.get('https://fapi.binance.com/fapi/v1/exchangeInfo')
        data = response.json()

        symbol = 'KAVAUSDT'  

        for symbol_info in data['symbols']:
            if symbol_info['symbol'] == symbol:
                self.price_precision = symbol_info['pricePrecision']
                self.quantity_precision = symbol_info['quantityPrecision']
                break


class User:
    def __init__(self, BASE_URL, API_KEY, SECRET_KEY):
        self.BASE_URL = BASE_URL
        self.api_key = API_KEY
        self.secret_key = SECRET_KEY


class Stop:
    def __init__(self, order_id,stop_prices,trigger_prices):
        self.order_id = order_id
        self.trigger_prices = trigger_prices
        self.stop_prices = stop_prices

def create_order(user,trade):
    endpoint = f'{user.BASE_URL}/fapi/v1/order'
    params = {
        'symbol': trade.symbol,
        'side': trade.side,
        'type': 'LIMIT',
        'quantity': round(trade.quantity*trade.leverage/trade.in_price,trade.quantity_precision),
        'price' : round(trade.in_price, trade.price_precision),
        'leverage': trade.leverage,
        'marginType' : trade.margin_type,
        'timestamp': int(time.time() * 1000),
        'timeinforce' : 'GTC'
    
    }
    sign = hmac.new(user.secret_key.encode('utf-8'), urlencode(params).encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {'X-MBX-APIKEY': user.api_key}
    params['signature'] = sign

    response = requests.post(endpoint, headers=headers, params=params)

    
    return response.json()

def stop_order(user,trade,stop_price,percentage,side):
    endpoint = f'{user.BASE_URL}/fapi/v1/order'
    
    gettingOut = round(trade.quantity*trade.leverage/trade.in_price, trade.quantity_precision)
    params = {
        'symbol': trade.symbol,
        'side': side,
        'type': 'STOP_MARKET',
        'quantity': gettingOut*percentage/100, 
        'stopPrice' : stop_price,
        'leverage': trade.leverage,
        'marginType' : trade.margin_type,  
        'timestamp': int(time.time() * 1000),
        'timeinforce' : 'GTC',
        'closePosition' : False,
        'activationPrice' : 1
    }
    sign = hmac.new(user.secret_key.encode('utf-8'), urlencode(params).encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {'X-MBX-APIKEY': user.api_key}
    params['signature'] = sign

    response1 = requests.post(endpoint, headers=headers, params=params)
    return response1.json()


def cancel_order(user,trade,stop):

    endpoint = f'{user.BASE_URL}/fapi/v1/order'
    params = {
        'symbol': trade.symbol,
        'orderId': stop.order_id,
        'timestamp': int(time.time() * 1000),
    }
    query_string = urlencode(params)
    signature = hmac.new(user.secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {'X-MBX-APIKEY': user.api_key}
    params['signature'] = signature

    response = requests.delete(endpoint, headers=headers, params=params)
    return response.json()

def change_stop(current_price, trade,user):
    for stop in trade.stop_orders:
        if(trade.side == "BUY"):
            if(current_price > stop.trigger_prices[0]):
                response4 = cancel_order(user,trade,stop)

                while("orderId" not in response4):
                    response4 = cancel_order(user,trade,stop)
                response3 = stop_order(user,trade,stop.stop_prices[0],10,"SELL")
                while("orderId" not in response3): 
                    response3 = stop_order(user,trade,stop.stop_prices[0],10,"SELL")
                
                stop.order_id = response3['orderId']

                del stop.trigger_prices[0]
                del stop.stop_prices[0] 
        elif(trade.side == "SELL"):
            if(current_price < stop.trigger_prices[0]):

                response4 = cancel_order(user,trade,stop)
                while("orderId" not in response4):
                    response4 = cancel_order(user,trade,stop)

                response3 = stop_order(user,trade,stop.stop_prices[0],10,"BUY")

                while("orderId" not in response3): 
                    response3 = stop_order(user,trade,stop.stop_prices[0],10,"BUY")
                
                stop.order_id = response3['orderId']
                del stop.trigger_prices[0]
                del stop.stop_prices[0]     

API_KEY = ""
SECRET_KEY = ""

trade = Trade("KAVAUSDT", "SELL", "LIMIT",3, 10, 0.8, "ISOLATED", False)
user = User('https://fapi.binance.com', API_KEY, SECRET_KEY)
response = create_order(user,trade)

while('orderId' not in response):
    response = create_order(user,trade)
    print(response)
trade.order_id = response['orderId']

response2 = stop_order(user,trade,0.9,100,"BUY")
while('orderId' not in response2):
    response2 = stop_order(user,trade,0.9,100,"BUY")
    print(response2)
stops = Stop(response2['orderId'],[],[])
came = False
trigger_price = 0.5


def on_message(ws, message):
    data = json.loads(message)
    current_price = float(data['c'])

    if(not came):
        if(trade.side == "BUY"):
            if(current_price < trigger_price):
                came = True
        if(trade.side == "SELL"):
            if(current_price > trigger_price):
                came = True        
    
    if(came):
        print(current_price)
        change_stop(current_price,trade,user)
    
        


def on_error(ws, error):
    print(f"Error: {error}")
    ws.run_forever()



def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed.")

socket_url = f'wss://fstream.binance.com/ws/{trade.symbol.lower()}@ticker'

ws = websocket.WebSocketApp(socket_url, on_message=on_message, on_error=on_error, on_close=on_close)
print("WebSocket started.")
ws.run_forever()

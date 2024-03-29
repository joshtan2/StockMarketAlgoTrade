from wsgiref import headers
from config import *
import requests,json
import time
from datetime import datetime
# import pyt
APCA_API_BASE_URL="https://paper-api.alpaca.markets/"
ORDERS_URL = APCA_API_BASE_URL+"v2/orders"
ACCOUNT_URL = APCA_API_BASE_URL+"v2/account"

headers = {
    "APCA-API-KEY-ID": alpacaAPI,
    "APCA-API-SECRET-KEY": alpacaSecret
}

POLYGONAPI  = polygonAPI
POLYGON_URL = "https://api.polygon.io/v2/aggs/ticker/SPY/range/1/day/2020-06-01/2020-06-17?apiKey=" + POLYGONAPI
RAPIDAPI_URL = "https://twelve-data1.p.rapidapi.com/price"
ALPHA_VENTURE_URL = "https://alpha-vantage.p.rapidapi.com/query"
rapid_headers = {
	"X-RapidAPI-Host": "twelve-data1.p.rapidapi.com",
	"X-RapidAPI-Key": rapidAPI
}

prices = []
MAs= []
EMAs = []
def get_account():
    request = requests.get(ACCOUNT_URL,headers = headers)
    return json.loads(request.content)

def get_orders():
    request = requests.get(ORDERS_URL,headers=headers)
    return json.loads(request.content)

def delete_order(id):
    url = ORDERS_URL + "/"+ id
    request = requests.delete(url,headers=headers)
    return request

def get_order(orderID):
    url = ORDERS_URL + "/"+ orderID
    request = requests.get(url,headers=headers)
    return json.loads(request.content)

def buy_order(symbol,qty,side,type,time_in_force):
    body = {
        "symbol":symbol,
        "qty":qty,  # fractional shares
        "side":side,
        "type": type,
        "time_in_force":time_in_force,
    }

    request = requests.post(ORDERS_URL,json =body ,headers = headers)
    return json.loads(request.content)

timeperiod = 5

def updateStats(EMA,MA,buying,orderID):
    #checks if the avg price filled is not null so we know the order was successful

    # response = get_order(orderID)


    # avgPrice,qty = response["filled_avg_price"],response["qty"]

    # while avgPrice is None:
    #     print("order has not been filled yet waiting antoher 15 seconds")
    #     time.sleep(15000)
    #     avgPrice,qty = response["filled_avg_price"],response["qty"]
       
    # if buying:
    #     #this means we bought a stock
    #     print("Bought stock @: {} and qty: {}".format(avgPrice,qty))
    # else:
    #     #this means we sold the stock
    #     print("Sold stock @: {} and qty: {}".format(avgPrice,qty))
    #     orderID = None
    buying = not buying
    MA = calculate_MA(timeperiod)
    EMA = calculate_EMA(prices,timeperiod,2,MA)
    return EMA,MA,buying,orderID

def calculate_EMA(prices, timeperiod,smoothing, MA):
    smoothing
    if len(EMAs) == 0:
        ema = MA
    else:
        K = ((smoothing) /(timeperiod+1))
        ema = (prices[-1])*K + (EMAs[-1])* (1.00-K)
    return float(ema)

def calculate_MA(timeperiod):

    #take the time period of minutes and calculate the avg from adding up all the prices
    # time.sleep(60)
    querystring = {"symbol":"AMZN","outputsize":"30","format":"json"}
    response = requests.request("GET", RAPIDAPI_URL, headers= rapid_headers, params=querystring)
    response = json.loads(response.text)["price"]
    prices.append(float(response))
    while len (prices) < timeperiod:
        print("not enough prices will wait a minute to get another price to add")
        print(prices)
        time.sleep(60)
        response = requests.request("GET", RAPIDAPI_URL, headers= rapid_headers, params=querystring)
        response = json.loads(response.text)["price"]
        prices.append(float(response))       
    while len(prices) > timeperiod:
        print("Too many prices and need to remove one")
        print(prices)
        prices.pop(0)

    print("Finished looping")
    print(prices)
    MA = sum(prices) / timeperiod
    return (MA)

marketopen = True
buying = True
orderID = None

MA = calculate_MA(timeperiod)
EMA = calculate_EMA(prices, timeperiod, 2, MA)
print("MA is : " + str(MA))
print("EMA is: " + str(EMA))
MAs.append(MA)
EMAs.append(EMA)
print(MAs)
print(EMAs)

while marketopen:
    print("inside loop")
    time.sleep(60)
    EMA,MA,buying,orderID = updateStats(EMA,MA,buying,"")
    print("MA is : " + str(MA))
    print("EMA is: " + str(EMA))
    MAs.append(MA)
    EMAs.append(EMA)
    while len(MAs) > timeperiod:
        MAs.pop(0)
    while len(EMAs) > timeperiod:
        EMAs.pop(0)
    print(MAs)
    print(EMAs)

#     if buying and orderID is None:
#         if EMA > MA:
#             response = buy_order('SPY', 1,"buy","market",'gtc')
#             buyID = response['id']
#             print('submitted buy request')
#             buying = False
#     else:
#         # Now we want to sell the stock when the conditions are met
#         if EMA < MA:
#             response = buy_order('SPY',1,"sell","market","gtc")
#             print('submitted sell request')

#     #waits 20 seconds then will check my order if the buyID has been sold or bought
#     print("waiting 20 seconds")
#     time.sleep(20000)


    






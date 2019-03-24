"""
This script plots EMAs
"""


from binance.client import Client
import numpy as np
import pandas as pd
import matplotlib
import talib
from fnmatch import fnmatch
from operator import itemgetter
import time
import datetime
import matplotlib.pyplot as plt


api_key='XXXX'
api_secret='XXXXX'
client = Client(api_key, api_secret)

pricelist = client.get_ticker()
price_btc = sorted([j for j in pricelist if fnmatch(j['symbol'], '*BTC')], key=itemgetter('symbol'))
coins_upper=[0]*(len(price_btc))
i=0
for item in price_btc:
    coins_upper[i] = price_btc[i]['symbol']
    i+=1

pair = (input("Input symbol (i.e., 'ETH'): ")).upper() + 'BTC'
tit2=['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteVolume', 'TradeNumber', 'NA1', 'NA2', 'NA3']
kline = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1HOUR, "1 week ago")
df = pd.DataFrame(kline, columns=tit2)
df = df.apply(pd.to_numeric, errors='ignore')
df['OpenTime']=pd.to_datetime(df['OpenTime'])

short_ema=talib.EMA(df['Close'],7) # Change the short EMA period
df['emaShort']=short_ema
long_ema=talib.EMA(df['Close'],28) # Change the long EMA period
df['emaLong']=long_ema

df.plot(x="OpenTime", y=["Close", "emaShort", "emaLong"])
plt.show()

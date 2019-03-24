"""
This PoC plots the kindles of the last year, volume included
"""

from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
from twisted.internet import reactor
import time
import matplotlib.pyplot as plt
import datetime
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import talib
import matplotlib.gridspec as gridspec


api_key='XXX'
api_secret='XXX'
client = Client(api_key, api_secret)

pair = (input("Input the coin, 'i.e.: ETH'): ") or 'ETH').upper() + 'BTC'


kline_1w = np.array(client.get_historical_klines(pair, '1d', "1 year ago"))
df_1w = pd.DataFrame(kline_1w.reshape(-1,12),dtype=float, columns = ('Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'))

ohlc = df_1w[['Close Time', 'Open', 'High', 'Low', 'Close']].copy()
ohlc['Close Time'] = pd.to_datetime(ohlc['Close Time'], unit='ms')
ohlc['Close Time'] = ohlc['Close Time'].apply(mdates.date2num)
ohlc['Volume'] = df_1w["Volume"]
ohlc['Volume SMA']=talib.SMA(ohlc['Volume'])
ohlc['emaShort'] = talib.EMA(ohlc['Close'],13)
ohlc['emaLong'] = talib.EMA(ohlc['Close'],34)

#ohlc=ohlc.tail(100) # Just for selecting a range

# Plot graph
plt.figure(1, figsize=(20,10))
gs = gridspec.GridSpec(4,1)
top = plt.subplot(gs[:3, :])
candlestick_ohlc(top, ohlc.values, width=1/(130), colorup='green', colordown='red') #0.8*1/(24*18)
top.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M %d/%m/%Y'))
top.plot(ohlc['Close Time'], ohlc['emaShort'], color = 'cyan', label = 'Short EMA (13)')
top.plot(ohlc['Close Time'], ohlc['emaLong'], color = 'blue', label = 'Long EMA (34)')
bottom = plt.subplot(gs[3, :])
#bottom.plot(ohlc['Close Time'], ohlc['Volume'], color = 'blue', label = 'Volume')
bars = plt.bar(ohlc['Close Time'], ohlc['Volume'], width=1/(130), color = 'green', label = 'Volume')
#Change bar color to red when appropiate
j=1
for i, bar in enumerate(bars):
    if i == 0:
        continue
    if ohlc.iloc[j]['Close'] < ohlc.iloc[j]['Open']:
        bar.set_facecolor('r')
    j=j+1
bottom.plot(ohlc['Close Time'], ohlc['Volume SMA'], color = 'blue', label = 'Volume SMA')
bottom.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
top.set_title('15-minute Candles  ' + str(pair))
top.set_ylabel('Closing Price')
bottom.set_ylabel('Volume')
plt.show()

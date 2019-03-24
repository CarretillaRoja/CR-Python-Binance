"""

RSI notifier

This piece of code tracks RSI of the Binance BTC pairs. You can specify both RSI thresholds, as well as the timeframe.
-

As you know, there is a risk (which I am not responsible of!) when the price goes down from the beggining.
If the price raises the same amount you specified for the SL, you are covered and everything will be gains.

This is a PoC, just a simulation, it does not trade with your tokens nor send them anywhere.

If you feel this code worthy, donations are appreciated:
- ETH: 0x56daD39CCd190D343682a903e0793E7427ECF287
- LTC: MUP3PcZ2QXgJ7CC1cmKTt7jEZDcQPcjcNu

"""


from binance.client import Client
import time
import datetime
import pandas as pd
import numpy as np
import talib
from fnmatch import fnmatch
from operator import itemgetter
from tqdm import tqdm, trange
import os
import telegram

class color:
   RED = '\033[91m'
   END = '\033[0m'

os.system('clear')

print ('Connecting to Binance... ', end='', flush=True)
api_key='XXXX'
api_secret='XXXX'
client = Client(api_key, api_secret)
print ('OK!\n')

#bot = telegram.Bot(token='XXXX:XXXX') # Uncomment to enable Telegram notification

RSI_sup = 70
RSI_inf = 30
timeframe = '4h'
minvol = 100

print ('Fetching coin list... ', end='', flush=True)
pricelist = client.get_ticker()
pricelist_btc = sorted([j for j in pricelist if fnmatch(j['symbol'], '*BTC')], key=itemgetter('symbol')) # Filtramos a los pares de BTC
pricelist_btc[:] = [d for d in pricelist_btc if d.get('lastPrice') != '0.00000000']
pricelist_btc[:] = [d for d in pricelist_btc if d.get('symbol') != 'BCCBTC']
pricelist_btc[:] = [d for d in pricelist_btc if float(d.get('quoteVolume')) > minvol]
print ('OK!\n')

coins_upper=[0]*(len(pricelist_btc))
progressbar=tqdm(range(len(pricelist_btc)), ascii=False, dynamic_ncols=True, leave=False, unit_scale=True)
i=0
for item in progressbar:
    coins_upper[i] = pricelist_btc[i]['symbol']
    progressbar.set_description('Listing {}'.format(pricelist_btc[i]['symbol']))
    i+=1
    time.sleep(0.005)
print ('Listed %s/%s coins.\n' % (len(coins_upper), len(coins_upper)))

print ('Minimun Volume = %d BTC' % minvol)
print ('Timeframe = %s' % timeframe)
print ('RSI thresholds: %d - %d\n' % (RSI_sup, RSI_inf))

while True:
    df = {}
    for name in coins_upper:
        df[name] = pd.DataFrame(np.array(client.get_historical_klines(name, timeframe, "1 week ago")).reshape(-1,12),dtype=float, columns = ('Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'))
        df[name] = df[name].apply(pd.to_numeric, errors='ignore')
        df[name]['RSI'] = talib.RSI(df[name]['Close'], timeperiod=14)
        last_RSI = float(df[name]['RSI'].tail(1))
        if last_RSI > RSI_sup:
            message = ('%s%.19s | %9s | RSI %2.0f%s' % (color.RED, datetime.datetime.now(), name, last_RSI, color.END))
            print (message)
            #bot.sendMessage(chat_id=XXXX, text=message) # Uncomment to enable Telegram notification
        elif (last_RSI < RSI_inf and last_RSI > 0):
            message = ('%s%.19s | %9s | RSI %2.0f%s' % (color.GREEN, datetime.datetime.now(), name, last_RSI, color.END))
            print (message)
            #bot.sendMessage(chat_id=XXXX, text=message) # Uncomment to enable Telegram notification

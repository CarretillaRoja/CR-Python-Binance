"""

X.A.V.I is a simulation PoC to see wether or not it makes sense to buy tokens after a little pump of X% and sell it after a fixed period of time.

"""


from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
from twisted.internet import reactor
import time
import datetime
from tqdm import tqdm, trange
from fnmatch import fnmatch
from operator import itemgetter
import pandas as pd
import numpy as np
import talib
from io import StringIO
from tabulate import tabulate
import os

os.system('clear')

###################################
# PARAMETERS           #
########################################################################################
ventana = 5        # TIME WINDOW (IN SECONDS) TO WATCH FOR PUMPS                       #
aumento = 1.01     # PUMP AMPLITUDE (1.01 MEANS 1%, 1.15 MEANS 15%)                    #
tiempo_venta = 30  # TIME ELAPSED BETWEEN BUY AL SELL                                  #
BTC_bank = 0.02    # BTC AMOUNT TO SIMULATE                                            #
########################################################################################

api_key='XXXX'
api_secret='XXXX'
print('Connecing to Binance...', end='', flush=True)
client = Client(api_key, api_secret)
print ('OK!\n')

print ('Fetching coin list... ', end='', flush=True)
pricelist = client.get_ticker() # Obtenemos todos los pares
pricelist_btc = sorted([j for j in pricelist if fnmatch(j['symbol'], '*BTC')], key=itemgetter('symbol')) # Filtramos a los pares de BTC
pricelist_btc[:] = [d for d in pricelist_btc if d.get('lastPrice') != '0.00000000']
pricelist_btc[:] = [d for d in pricelist_btc if float(d.get('lastPrice')) > 0.00000100]
print ('OK!\n')

# Uppercase coin symbol matrix
coins_upper=[0]*(len(pricelist_btc))
progressbar=tqdm(range(len(pricelist_btc)), ascii=False, dynamic_ncols=True, leave=False, unit_scale=True)
i=0
for item in progressbar:
    coins_upper[i] = pricelist_btc[i]['symbol']
    progressbar.set_description('Listing {}'.format(pricelist_btc[i]['symbol']))
    i+=1
    time.sleep(0.005)
print ('Listed %s/%s coins.\n' % (len(pricelist_btc), len(pricelist_btc)))

# Trade matrix used on the websockets
coins_list=[x.lower() for x in coins_upper]
coins_list=[s + '@ticker' for s in coins_list]

titles_trade = ['Date', 'Symbol', 'Price', 'Trades']
df_trade = pd.DataFrame(columns = titles_trade)

titles_ticker = ['Date', 'Symbol', 'Price', 'Volume']
df_ticker = pd.DataFrame(columns = titles_ticker)

compra = 0
comprado = False
tiempo_compra = ''
symbol_compra = ''

def process_message(msg):
    global df_trade
    global df_ticker
    global compra
    global comprado
    global tiempo_compra
    global tiempo_venta
    global ventana
    global symbol_compra
    global BTC_bank

    data = msg ['data']
    id = data['s']
    start_date = datetime.datetime.now() - datetime.timedelta(seconds = ventana)
    end_date = datetime.datetime.now()
    df_ticker = df_ticker.append(pd.Series([datetime.datetime.fromtimestamp(round(data['E'] / 1000,0)), id, float(data['c']), float(data['q'])], titles_ticker), ignore_index=True, sort = True)
    df_ticker = df_ticker.loc[(df_ticker['Date'] > start_date) & (df_ticker['Date'] <= end_date)]

    if compra == 0:
        if len(df_ticker[df_ticker.Symbol == id]) > 0:
            if float(data['c']) > df_ticker[df_ticker.Symbol == id].loc[df_ticker[df_ticker.Symbol == id].index[-1],'Price']:
                if float(data['c']) >= (1.01 * df_ticker[df_ticker.Symbol == id].loc[df_ticker[df_ticker.Symbol == id].index[0],'Price']):
                    #units = round(BTC_bank / float(data['c']),2)
                    print ('%s' % (datetime.datetime.now()))
                    print ('BUYING %s at %10.8f' % (id, float(data['c'])))
                    print ('Waiting %d seconds to sell' % (tiempo_venta))
                    compra = float(data['c'])
                    symbol_compra = id
                    comprado = True
                    tiempo_compra = datetime.datetime.now() + datetime.timedelta(seconds = tiempo_venta)

    if id == symbol_compra:

        if compra != 0:
            pass
            #print ('%19s | %9s | P: %10.8f' % (datetime.datetime.fromtimestamp(data['E'] / 1e3).strftime("%Y-%m-%d %H:%M:%S"), id, float(data['c'])))

        if comprado == True:
            if datetime.datetime.now() > tiempo_compra: # Hace que se detenga y se reinicie cada X tiempo
                venta = float(data['c'])
                beneficio = 100 * ((venta / compra) -1)
                BTC_bank = BTC_bank * venta / compra
                print ('Sold at %10.8f --> Profit of %.2f %%' % (venta, beneficio))
                print ('Balance: %f BTC\n' % (BTC_bank))
                compra = 0
                comprado = False
                tiempo_compra = ''
                symbol_compra = ''


bm = BinanceSocketManager(client)
conn_key = bm.start_multiplex_socket(coins_list, process_message)
bm.start()
print ('Buying coins pumping %.2f%% in less than %d seconds and selling them after %d seconds...\n' % ((aumento-1)*100, ventana, tiempo_venta))
print ('Starting. Balance: %f BTC\n' % (BTC_bank))

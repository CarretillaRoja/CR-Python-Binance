"""

PoC in which it prints coins buys al sells

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


# Connecting to Binance
api_key='XXX'
api_secret='XXX'
client = Client(api_key, api_secret)

# Get pair list
print ('Fetching coin list... ', end="", flush=True)
pricelist = client.get_ticker()
pricelist_btc = sorted([j for j in pricelist if fnmatch(j['symbol'], '*BTC')], key=itemgetter('symbol'))

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
coins_trade=[s + '@trade' for s in coins_list]

# Restarts webthe socket
def clock_reset():
    global stop
    stop = (datetime.datetime.now() + datetime.timedelta(hours=1)) ### CHANGE SOCKET RESTARTING PERIOD

def process_message(msg):

    trade = msg ['data']

    if trade['m'] == True:
        mov = 'SOLD'
    else:
        mov = 'BOUGHT'
    print ("%19s | %9s | Price (%10.8f) | %.2f coins have been %s " % (datetime.datetime.fromtimestamp(trade['T'] / 1e3).strftime("%Y-%m-%d %H:%M:%S"), trade['s'], float(trade['p']), float(trade['q']), mov))

    # Restarts the websocket
    if datetime.datetime.now() > stop:
        print('Closing socket...\n')
        bm.close()
        print('Refresing info...')
        time.sleep(5)
        print('\nRestarting socket...')
        bm.start_aggtrade_socket('ETHBTC', process_message)
        clock_reset()


clock_reset()
bm = BinanceSocketManager(client)
bm.start_multiplex_socket(coins_trade, process_message)
bm.start()


"""
Trade websocket answer
{
  "e": "trade",     // Event type
  "E": 123456789,   // Event time
  "s": "BNBBTC",    // Symbol
  "t": 12345,       // Trade ID
  "p": "0.001",     // Price
  "q": "100",       // Quantity
  "b": 88,          // Buyer order ID
  "a": 50,          // Seller order ID
  "T": 123456785,   // Trade time
  "m": true,        // Is the buyer the market maker? --> TRUE: sell // FALSE: buy
  "M": true         // Ignore
}
"""

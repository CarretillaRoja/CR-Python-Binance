from binance.client import Client
from binance.websockets import BinanceSocketManager
import datetime

api_key=''
api_secret=''
client = Client(api_key, api_secret)

def process_message(message):
    datos=message['data']
    print("got ticker message: {}".format(datos['s'])) 
    #
    # Here main code
    #
    if datetime.datetime.now() > stop:
        print('closing socket')
        bm.close()
        bm.start_multiplex_socket(coins_lower, process_message)
        clock_reset()

def clock_reset():
    global stop
    stop = (datetime.datetime.now() + datetime.timedelta(seconds=15)) 

coins_lower=['xlmbtc@trade', 'xrpbtc@trade', 'ethbtc@trade']

clock_reset()
bm = BinanceSocketManager(client)
bm.start_multiplex_socket(coins_lower, process_message)
bm.start()
bm.close()
bm.start_multiplex_socket(coins_lower, process_message)

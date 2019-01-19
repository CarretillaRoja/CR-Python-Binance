"""

WALLET PROTECTOR

This piece of code tracks the specified coins into your wallet, so you can specify a trailing stop-loss. It behaves this way:
- You input a % for the trailing stop-loss
- If the price dips to that point, it lets you know
- If the price goes up, it raises the stop-loss
- When eventually the price goes down again and reaches the SL, it lets you know

As you know, there is a risk (which I am not responsible of!) when the price goes down from the beggining.
If the price raises the same amount you specified for the SL, you are covered and everything will be gains.

This is a PoC, just a simulation, it does not trade with your tokens nor send them anywhere.

If you feel this code worthy, donations are appreciated:
- ETH: 0x56daD39CCd190D343682a903e0793E7427ECF287
- LTC: MUP3PcZ2QXgJ7CC1cmKTt7jEZDcQPcjcNu

"""

from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
from twisted.internet import reactor
from operator import itemgetter
from fnmatch import fnmatch
from tabulate import tabulate
import time
import datetime
import os
import sys
import pandas as pd
import telegram

# Clears the screen
width = os.get_terminal_size().columns
os.system('clear')

# Welcome message
print('\n')
print(' /$$      /$$           /$$ /$$             /$$    '.center(width))
print('| $$  /$ | $$          | $$| $$            | $$    '.center(width))
print('| $$ /$$$| $$  /$$$$$$ | $$| $$  /$$$$$$  /$$$$$$  '.center(width))
print('| $$/$$ $$ $$ |____  $$| $$| $$ /$$__  $$|_  $$_/  '.center(width))
print('| $$$$_  $$$$  /$$$$$$$| $$| $$| $$$$$$$$  | $$    '.center(width))
print('| $$$/ \  $$$ /$$__  $$| $$| $$| $$_____/  | $$ /$$'.center(width))
print('| $$/   \  $$|  $$$$$$$| $$| $$|  $$$$$$$  |  $$$$/'.center(width))
print('|__/     \__/ \_______/|__/|__/ \_______/   \___/  '.center(width))
print(''.center(width))
print(' /$$$$$$$                       /$$                           /$$                        '.center(width))
print('| $$__  $$                     | $$                          | $$                        '.center(width))
print('| $$  \ $$ /$$$$$$   /$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$$ /$$$$$$    /$$$$$$   /$$$$$$ '.center(width))
print('| $$$$$$$//$$__  $$ /$$__  $$|_  $$_/   /$$__  $$ /$$_____/|_  $$_/   /$$__  $$ /$$__  $$'.center(width))
print('| $$____/| $$  \__/| $$  \ $$  | $$    | $$$$$$$$| $$        | $$    | $$  \ $$| $$  \__/'.center(width))
print('| $$     | $$      | $$  | $$  | $$ /$$| $$_____/| $$        | $$ /$$| $$  | $$| $$      '.center(width))
print('| $$     | $$      |  $$$$$$/  |  $$$$/|  $$$$$$$|  $$$$$$$  |  $$$$/|  $$$$$$/| $$      '.center(width))
print('|__/     |__/       \______/    \___/   \_______/ \_______/   \___/   \______/ |__/      '.center(width))
print('')
print('Simulation edition (v1c)\n'.center(width))


# Binance and Telegram clients
api_key='XXXX'
api_secret='XXXX'
client = Client(api_key, api_secret)
bot = telegram.Bot(token='XXXX:XXXX') # Uncomment to enable Telegram notification

# BTC Balance
pricelist = sorted(client.get_ticker(), key=itemgetter('symbol'))
BTC_available = float(client.get_asset_balance(asset='BTC')['free'])


# Shows the wallet
bal_text = sorted([d for d in client.get_account()['balances'] if d['free'] != '0.00000000'or d['locked'] != '0.00000000'], key=itemgetter('asset'))
print('\nYour wallet:')
total = 0
for i in range(0, len(bal_text)):
    print('{0:9s} | Free: {1:15s} | Locked: {2:15s}'.format(bal_text[i]['asset'], bal_text[i]['free'], bal_text[i]['locked']))
    if bal_text[i]['asset'] == 'BTC':
        total = total + float(bal_text[i]['free']) + float(bal_text[i]['locked'])
    else:
        coin_temp = list(filter(lambda person: person['symbol'] == (bal_text[i]['asset'] + 'BTC'), pricelist))
        coin_temp = float(coin_temp[0]['lastPrice'])
        total = total + (coin_temp * (float(bal_text[i]['free']) + float(bal_text[i]['locked'])))
print('----------------------')
print('TOTAL = %.8f BTC\n' % total)


# Evaluate decimal positions
def precision_par(par):
    BinanceTickInfo = {'ADABTC': 1e-08, 'ADXBTC': 1e-08, 'AEBTC': 1e-07, 'AGIBTC': 1e-08, 'AIONBTC': 1e-07, 'AMBBTC': 1e-08, 'APPCBTC': 1e-08, 'ARDRBTC': 1e-08, 'ARKBTC': 1e-07, 'ARNBTC': 1e-08, 'ASTBTC': 1e-08, 'BATBTC': 1e-08, 'BCDBTC': 1e-06, 'BCHABCBTC': 1e-06, 'BCHSVBTC': 1e-06, 'BCNBTC': 1e-08, 'BCPTBTC': 1e-08, 'BLZBTC': 1e-08, 'BNBBTC': 1e-08, 'BNTBTC': 1e-08, 'BQXBTC': 1e-08, 'BRDBTC': 1e-08, 'BTGBTC': 1e-06, 'BTSBTC': 1e-08, 'CDTBTC': 1e-08, 'CHATBTC': 1e-08, 'CLOAKBTC': 1e-07, 'CMTBTC': 1e-08, 'CNDBTC': 1e-08, 'CTRBTC': 1e-08, 'CVCBTC': 1e-08, 'DASHBTC': 1e-06, 'DATABTC': 1e-08, 'DCRBTC': 1e-06, 'DENTBTC': 1e-08, 'DGDBTC': 1e-06, 'DLTBTC': 1e-08, 'DNTBTC': 1e-08, 'DOCKBTC': 1e-08, 'EDOBTC': 1e-07, 'ELFBTC': 1e-08, 'ENGBTC': 1e-08, 'ENJBTC': 1e-08, 'EOSBTC': 1e-07, 'ETCBTC': 1e-06, 'ETHBTC': 1e-06, 'EVXBTC': 1e-08, 'FUELBTC': 1e-08, 'FUNBTC': 1e-08, 'GASBTC': 1e-06, 'GNTBTC': 1e-08, 'GOBTC': 1e-08, 'GRSBTC': 1e-08, 'GTOBTC': 1e-08, 'GVTBTC': 1e-07, 'GXSBTC': 1e-07, 'HOTBTC': 1e-08, 'HSRBTC': 1e-06, 'ICNBTC': 1e-08, 'ICXBTC': 1e-07, 'INSBTC': 1e-07, 'IOSTBTC': 1e-08, 'IOTABTC': 1e-08, 'IOTXBTC': 1e-08, 'KEYBTC': 1e-08, 'KMDBTC': 1e-07, 'KNCBTC': 1e-08, 'LENDBTC': 1e-08, 'LINKBTC': 1e-08, 'LOOMBTC': 1e-08, 'LRCBTC': 1e-08, 'LSKBTC': 1e-07, 'LTCBTC': 1e-06, 'LUNBTC': 1e-07, 'MANABTC': 1e-08, 'MCOBTC': 1e-06, 'MDABTC': 1e-08, 'MFTBTC': 1e-08, 'MITHBTC': 1e-08, 'MODBTC': 1e-07, 'MTHBTC': 1e-08, 'MTLBTC': 1e-06, 'NANOBTC': 1e-07, 'NASBTC': 1e-07, 'NAVBTC': 1e-07, 'NCASHBTC': 1e-08, 'NEBLBTC': 1e-07, 'NEOBTC': 1e-06, 'NPXSBTC': 1e-08, 'NULSBTC': 1e-08, 'NXSBTC': 1e-07, 'OAXBTC': 1e-08, 'OMGBTC': 1e-06, 'ONTBTC': 1e-08, 'OSTBTC': 1e-08, 'PHXBTC': 1e-08, 'PIVXBTC': 1e-07, 'POABTC': 1e-08, 'POEBTC': 1e-08, 'POLYBTC': 1e-08, 'POWRBTC': 1e-08, 'PPTBTC': 1e-07, 'QKCBTC': 1e-08, 'QLCBTC': 1e-08, 'QSPBTC': 1e-08, 'QTUMBTC': 1e-06, 'RCNBTC': 1e-08, 'RDNBTC': 1e-08, 'RENBTC': 1e-08, 'REPBTC': 1e-06, 'REQBTC': 1e-08, 'RLCBTC': 1e-07, 'RVNBTC': 1e-08, 'SALTBTC': 1e-06, 'SCBTC': 1e-08, 'SNGLSBTC': 1e-08, 'SNMBTC': 1e-08, 'SNTBTC': 1e-08, 'STEEMBTC': 1e-07, 'STORJBTC': 1e-08, 'STORMBTC': 1e-08, 'STRATBTC': 1e-06, 'SUBBTC': 1e-08, 'SYSBTC': 1e-08, 'THETABTC': 1e-08, 'TNBBTC': 1e-08, 'TNTBTC': 1e-08, 'TRIGBTC': 1e-07, 'TRXBTC': 1e-08, 'TUSDBTC': 1e-08, 'VETBTC': 1e-08, 'VIABTC': 1e-07, 'VIBBTC': 1e-08, 'VIBEBTC': 1e-08, 'WABIBTC': 1e-08, 'WANBTC': 1e-08, 'WAVESBTC': 1e-07, 'WINGSBTC': 1e-08, 'WPRBTC': 1e-08, 'WTCBTC': 1e-08, 'XEMBTC': 1e-08, 'XLMBTC': 1e-08, 'XMRBTC': 1e-06, 'XRPBTC': 1e-08, 'XVGBTC': 1e-08, 'XZCBTC': 1e-06, 'YOYOBTC': 1e-08, 'ZECBTC': 1e-06, 'ZENBTC': 1e-06, 'ZILBTC': 1e-08, 'ZRXBTC': 1e-08}
    prec = int(str(BinanceTickInfo[par])[-1])
    return prec

menu_option = '1'

# Menu option 1
if menu_option == "1":
    values = (input("Input symbols, separated by commas (i.e.: bnb, trx, xvg): "))
    coins_lower = values.split(", ")
    coins_lower = [x + 'btc'  for x in coins_lower]
    coins_upper = [x.upper() for x in coins_lower]
    coins_list = [x + '@aggTrade'  for x in coins_lower]
    titles = ['Symbol', 'Amount', 'BuyPrice', 'LastPrice', 'BestPrice', 'SL_SELL_float', 'SL_SELL_str', 'SL_TRIG_float', 'SL_TRIG_str', 'SL_Limit_float', 'Precision', 'Profit', 'Orden']
    df = pd.DataFrame(columns=titles)
    for pair in coins_upper:
        pricecheck = input('At what pice (in satoshis) was ' + pair + ' bought?: ' or 0)
        int_precision = precision_par(pair)
        sl_price_buy_input_str = '0.'+('0'*(int_precision - len(pricecheck))) + pricecheck
        int_buyprice = float(sl_price_buy_input_str)
        int_sl_limit_float = (100 - float(input("Input trailig stop-loss % limit: ") or 0)) / 100
        int_sl_sell_float = round(int_buyprice * int_sl_limit_float, int_precision)
        int_sl_sell_str = "{:10.8f}".format(int_sl_sell_float)
        int_sl_trig_float = round(int_sl_sell_float * 1.00, int_precision)
        int_sl_trig_str = "{:10.8f}".format(int_sl_trig_float)
        unidades = int(float(client.get_asset_balance(asset=pair[:3])['free']))# ver cuantas unidades hay disponibles de la moneda
        row = [pair, unidades, int_buyprice, 0, 0, int_sl_sell_float, int_sl_sell_str , int_sl_trig_float, int_sl_trig_str, int_sl_limit_float, int_precision, 0, 0]
        df = df.append(pd.Series(row, index = titles), ignore_index=True)
        df.index = df["Symbol"]
        print("\n%.0f tokens will be tracked, with a SL value of %s and a buy price of %10.8f\n" % (df.loc[pair, 'Amount'], df.loc[pair, 'SL_TRIG_str'], df.loc[pair, 'BuyPrice']))


# Main code
def process_message(msg):

    global start
    global df

    data = msg ['data']
    pair = data['s']

    current_price_str = data['p']
    current_price_float = round(float(current_price_str),8)

    if data['m'] == False:
        mov1 = 'bought'
        icon = '\u25b2'
        mov2 = 'Price ' + icon
    else:
        mov1 = 'sold'
        icon = '\u25bc'
        mov2 = 'Price ' + icon

    if start == True:
        print('        DATE        |  SYMBOL  |    PRICE     |   STOP-LOSS   | PROFIT |     MOVEMENTS       |  TREND   ')
        print('--------------------------------------------------------------------------------------------------------')
        start = False


    elif start == False:

        if current_price_float > df.loc[pair, 'SL_TRIG_float']:
            if current_price_float < df.loc[pair, 'BestPrice']:
                df.loc[pair, 'Profit'] = ((100 * current_price_float / df.loc[pair, 'BuyPrice'])*(1-0.0015))-100
                notification = '%19s | %8s | P %s | SL %s | %5.2f%% | %5.0f tokens %6s | %s' % ((datetime.datetime.fromtimestamp(float(data['E'])/1000).strftime("%Y-%m-%d %H:%M:%S"), pair, current_price_str, df.loc[pair, 'SL_TRIG_str'], df.loc[pair, 'Profit'], float(data['q']), mov1, mov2))
                print(notification)
                #bot.sendMessage(chat_id=171502119, text=notification) # Uncomment to enable Telegram notification

            elif current_price_float > df.loc[pair, 'BestPrice']:
                df.loc[pair, 'SL_SELL_float'] = round(current_price_float * df.loc[pair, 'SL_Limit_float'], df.loc[pair, 'Precision'])
                df.loc[pair, 'SL_SELL_str'] = "{:10.8f}".format(df.loc[pair, 'SL_SELL_float'])
                df.loc[pair, 'SL_TRIG_float'] = round(df.loc[pair, 'SL_SELL_float'] * 1.00, df.loc[pair, 'Precision'])
                df.loc[pair, 'SL_TRIG_str'] = "{:10.8f}".format(df.loc[pair, 'SL_TRIG_float'])
                df.loc[pair, 'Profit'] = ((100 * current_price_float / df.loc[pair, 'BuyPrice'])*(1-0.0015))-100
                notification = '%19s | %8s | P %s | SL %s | %5.2f%% | %5.0f tokens %6s | %s' % ((datetime.datetime.fromtimestamp(float(data['E'])/1000).strftime("%Y-%m-%d %H:%M:%S"), pair, current_price_str, df.loc[pair, 'SL_TRIG_str'], df.loc[pair, 'Profit'], float(data['q']), mov1, mov2))
                print(notification)
                #bot.sendMessage(chat_id=171502119, text=notification) # Uncomment to enable Telegram notification
                df.loc[pair, 'BestPrice'] = current_price_float

            elif current_price_float == df.loc[pair, 'BestPrice']:
                pass

    df.loc[pair, 'LastPrice'] = current_price_float

# Starts the socket
start = True
bm = BinanceSocketManager(client)
conn_key = bm.start_multiplex_socket(coins_list, process_message)
bm.start()

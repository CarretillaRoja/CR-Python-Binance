"""
Bottom Hunter

This piece of code allows you to track some coins for the minimum price. It works this way:
- It shows your the amount of BTC available and asks how many you will use.
- Asks for some coins you want to buy. It shows their price and asks at what price you want to start watching them. Eg: 100 satoshis.
- HERE IS THE POINT! You must enter a % to add on top of the coin price. Eg. 3%.

Then, it starts working:
- When the price gets to 100 satoshis, it starts monitoring it, with a buy target at 100 + 3% = 103 satoshis.
- If the price goes down further to 93, it lowers the buy target to 93 + 3% = 96 satoshis.
- Repeat this process if the price keeps going down.
- If the price raises, it lets you know when it gets to 96 satoshis.

As you know, there is a risk (which I am not responsible of!) when the price goes up from the beggining.
If the price goes down the same amount you specified for the %, you are covered and everything will be gains.

This is a PoC, just a simulation, it does not trade with your tokens nor send them anywhere.
If you feel brave, you can add the buy order to the code.

If you feel this code worthy, donations are appreciated:
- ETH: 0x56daD39CCd190D343682a903e0793E7427ECF287
- LTC: MUP3PcZ2QXgJ7CC1cmKTt7jEZDcQPcjcNu


"""

from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
from twisted.internet import reactor
from operator import itemgetter
import time
import datetime
import os
import sys
import pandas as pd
from tabulate import tabulate
from fnmatch import fnmatch
import telegram

width = os.get_terminal_size().columns
os.system('clear')


print('\n')
print(' /$$$$$$$              /$$     /$$                            '.center(width))
print('| $$__  $$            | $$    | $$                            '.center(width))
print('| $$  \ $$  /$$$$$$  /$$$$$$ /$$$$$$    /$$$$$$  /$$$$$$/$$$$ '.center(width))
print('| $$$$$$$  /$$__  $$|_  $$_/|_  $$_/   /$$__  $$| $$_  $$_  $$'.center(width))
print('| $$__  $$| $$  \ $$  | $$    | $$    | $$  \ $$| $$ \ $$ \ $$'.center(width))
print('| $$  \ $$| $$  | $$  | $$ /$$| $$ /$$| $$  | $$| $$ | $$ | $$'.center(width))
print('| $$$$$$$/|  $$$$$$/  |  $$$$/|  $$$$/|  $$$$$$/| $$ | $$ | $$'.center(width))
print('|_______/  \______/    \___/   \___/   \______/ |__/ |__/ |__/'.center(width))
print(''.center(width))
print(' /$$   /$$                       /$$                          '.center(width))
print('| $$  | $$                      | $$                          '.center(width))
print('| $$  | $$ /$$   /$$ /$$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$   '.center(width))
print('| $$$$$$$$| $$  | $$| $$__  $$|_  $$_/   /$$__  $$ /$$__  $$  '.center(width))
print('| $$__  $$| $$  | $$| $$  \ $$  | $$    | $$$$$$$$| $$  \__/  '.center(width))
print('| $$  | $$| $$  | $$| $$  | $$  | $$ /$$| $$_____/| $$        '.center(width))
print('| $$  | $$|  $$$$$$/| $$  | $$  |  $$$$/|  $$$$$$$| $$        '.center(width))
print('|__/  |__/ \______/ |__/  |__/   \___/   \_______/|__/   by:CR'.center(width))
print('\n')

#######################################################
####                START VARIABLES                ####
#######################################################

simulation = True
api_key='XXXX'
api_secret='XXXX'
#bot = telegram.Bot(token='AAAA:BBBB') # Enable to notify through Telegram
client = Client(api_key, api_secret)

#######################################################
####                   FUNCTIONS                   ####
#######################################################


def main_menu():
    print('MAIN MENU:')
    print(' 3 - Bottom Hunter')
    print(' 4 - Exit.\n')
    menu_option_int = int(input("Choose an option: ")) # Define qué hará a continuación
    return(menu_option_int)

def option3():
    global client
    btc_wallet = sorted([d for d in client.get_account()['balances'] if d['asset'] == 'BTC'])[0]
    btc_available = float(btc_wallet['free'])
    pricelist = sorted(client.get_ticker(), key=itemgetter('symbol'))
    values = (input("\nPlease input coin names separated by commas (eth, bnb, btc,...): "))
    coins_lower = values.split(", ")
    coins_lower = [x + 'btc'  for x in coins_lower]
    coins_upper = [x.upper() for x in coins_lower]
    coins_list = [x + '@aggTrade'  for x in coins_lower]
    titles = ['Symbol', 'Amount', 'LastPrice', 'LowerPrice', 'margin', 'min_price_float', 'min_price_str', 'trigger_price_float', 'trigger_price_str', 'buy_price_float', 'buy_price_str', 'Precision', 'Profit', 'Action']
    df_input = pd.DataFrame(columns = titles)
    order_list = dict(zip(coins_upper, [float(0)]*len(coins_upper)))
    all_prices = client.get_ticker()
    for pair in coins_upper:
        lastPrice = sorted([d for d in all_prices if d['symbol'] == pair], key=itemgetter('symbol'))[0]['lastPrice']
        prec2 = precision_par(pair) + 2
        print ('%s current price is %s' % (pair[:-3], lastPrice[:prec2]))
        input_min = input('Min price (in satoshis) to start SL for ' + pair + ' ? ' or 0)
        input_precision = precision_par(pair)
        input_min_str = '0.' + ('0' * (input_precision - len(input_min))) + input_min
        input_min_float = float(input_min_str)
        input_margin_float = (100 + float(input("Plese input stop-buy margin (in %): ") or 0)) / 100 # Esto calcula el 0.9x
        trigger_price_float = round(input_min_float * input_margin_float, input_precision)
        trigger_price_str = "{:10.8f}".format(trigger_price_float)
        trigger_price_str = trigger_price_str[:(2 + input_precision)]
        buy_price_float = trigger_price_float
        buy_price_str = trigger_price_str
        unidades = int(btc_available/trigger_price_float)# ver cuantas unidades hay disponibles de la moneda
        row = [pair, unidades, 0, 0, input_margin_float, input_min_float, input_min_str, trigger_price_float, trigger_price_str, buy_price_float, buy_price_str, input_precision, 0, 'BUY']
        df_input = df_input.append(pd.Series(row, index = titles), ignore_index=True)
        df_input.index = df_input["Symbol"]
        print("\nWhen %s < %s, it will watch %.0f coins with a %.2f%% of margin and a buy price of %10.8f\n" % (df_input.loc[pair, 'Symbol'], df_input.loc[pair, 'min_price_str'], df_input.loc[pair, 'Amount'], (input_margin_float - 1)*100, df_input.loc[pair, 'buy_price_float']))
    return df_input, coins_list, order_list

def clock_reset():
    global stop
    stop = (datetime.datetime.now() + datetime.timedelta(hours=12)) ### CAMBIAR PERIORDICIDAD AQUI

def precision_par(par):
    BinanceTickInfo = {'ADABTC': 8, 'ADXBTC': 8, 'AEBTC': 7, 'AGIBTC': 8, 'AIONBTC': 7, 'AMBBTC': 8, 'APPCBTC': 8, 'ARDRBTC': 8, 'ARKBTC': 7, 'ARNBTC': 8, 'ASTBTC': 8, 'BATBTC': 8, 'BCDBTC': 6, 'BCHABCBTC': 6, 'BCHSVBTC': 6, 'BCNBTC': 8, 'BCPTBTC': 8, 'BLZBTC': 8, 'BNBBTC': 8, 'BNTBTC': 8, 'BQXBTC': 8, 'BRDBTC': 8, 'BTGBTC': 6, 'BTSBTC': 8, 'CDTBTC': 8, 'CHATBTC': 8, 'CLOAKBTC': 7, 'CMTBTC': 8, 'CNDBTC': 8, 'CTRBTC': 8, 'CVCBTC': 8, 'DASHBTC': 6, 'DATABTC': 8, 'DCRBTC': 6, 'DENTBTC': 8, 'DGDBTC': 6, 'DLTBTC': 8, 'DNTBTC': 8, 'DOCKBTC': 8, 'EDOBTC': 7, 'ELFBTC': 8, 'ENGBTC': 8, 'ENJBTC': 8, 'EOSBTC': 7, 'ETCBTC': 6, 'ETHBTC': 6, 'EVXBTC': 8, 'FUELBTC': 8, 'FUNBTC': 8, 'GASBTC': 6, 'GNTBTC': 8, 'GOBTC': 8, 'GRSBTC': 8, 'GTOBTC': 8, 'GVTBTC': 7, 'GXSBTC': 7, 'HOTBTC': 8, 'HSRBTC': 6, 'ICNBTC': 8, 'ICXBTC': 7, 'INSBTC': 7, 'IOSTBTC': 8, 'IOTABTC': 8, 'IOTXBTC': 8, 'KEYBTC': 8, 'KMDBTC': 7, 'KNCBTC': 8, 'LENDBTC': 8, 'LINKBTC': 8, 'LOOMBTC': 8, 'LRCBTC': 8, 'LSKBTC': 7, 'LTCBTC': 6, 'LUNBTC': 7, 'MANABTC': 8, 'MCOBTC': 6, 'MDABTC': 8, 'MFTBTC': 8, 'MITHBTC': 8, 'MODBTC': 7, 'MTHBTC': 8, 'MTLBTC': 6, 'NANOBTC': 7, 'NASBTC': 7, 'NAVBTC': 7, 'NCASHBTC': 8, 'NEBLBTC': 7, 'NEOBTC': 6, 'NPXSBTC': 8, 'NULSBTC': 8, 'NXSBTC': 7, 'OAXBTC': 8, 'OMGBTC': 6, 'ONTBTC': 7, 'OSTBTC': 8, 'PHXBTC': 8, 'PIVXBTC': 7, 'POABTC': 8, 'POEBTC': 8, 'POLYBTC': 8, 'POWRBTC': 8, 'PPTBTC': 7, 'QKCBTC': 8, 'QLCBTC': 8, 'QSPBTC': 8, 'QTUMBTC': 6, 'RCNBTC': 8, 'RDNBTC': 8, 'RENBTC': 8, 'REPBTC': 6, 'REQBTC': 8, 'RLCBTC': 7, 'RVNBTC': 8, 'SALTBTC': 6, 'SCBTC': 8, 'SNGLSBTC': 8, 'SNMBTC': 8, 'SNTBTC': 8, 'STEEMBTC': 7, 'STORJBTC': 8, 'STORMBTC': 8, 'STRATBTC': 6, 'SUBBTC': 8, 'SYSBTC': 8, 'THETABTC': 8, 'TNBBTC': 8, 'TNTBTC': 8, 'TRIGBTC': 7, 'TRXBTC': 8, 'TUSDBTC': 8, 'VETBTC': 8, 'VIABTC': 7, 'VIBBTC': 8, 'VIBEBTC': 8, 'WABIBTC': 8, 'WANBTC': 7, 'WAVESBTC': 7, 'WINGSBTC': 8, 'WPRBTC': 8, 'WTCBTC': 8, 'XEMBTC': 8, 'XLMBTC': 8, 'XMRBTC': 6, 'XRPBTC': 8, 'XVGBTC': 8, 'XZCBTC': 6, 'YOYOBTC': 8, 'ZECBTC': 6, 'ZENBTC': 6, 'ZILBTC': 8, 'ZRXBTC': 8}
    prec = BinanceTickInfo[par]
    return prec

#######################################################
####                   MAIN CODE                   ####
#######################################################

menu_option = main_menu()

if menu_option == 3:
    btc_wallet = sorted([d for d in client.get_account()['balances'] if d['asset'] == 'BTC'])[0]
    btc_available = float(btc_wallet['free'])
    print('\nBTC Wallet | Available: {} | Locked: {}\n'.format(btc_wallet['free'], btc_wallet['locked']))
    btc_available = float(input('How many BTC are available to spend? '))
    df_bh, coins_list, order_list = option3()

if menu_option == 4:
    print ('Goodbye...\n')
    os._exit(1)


#######################################################
####                   MAIN CODE                   ####
#######################################################

def process_message(msg):

    global start
    global df_bh
    global order_list
    global menu_option
    global stop
    global coins_list
    global action

    data = msg ['data']
    pair = data['s']

    current_price_str = data['p'] # El precio actual en STRING
    current_price_float = round(float(current_price_str),8) # El precio actual en FLOAT

    if data['m'] == False:
        mov1 = 'Bought'
        mov2 = 'Price ' + '\u25b2'
    else:
        mov1 = 'Sold'
        mov2 = 'Price ' + '\u25bc'

    if start == True:
        print('        DATE        |  SYMBOL  |    PRICE     |   STOP-BUY    |    TRANSACTIONS     |   TREND  ')
        print('-----------------------------------------------------------------------------------------------')
        start = False

    elif start == False:
        if df_bh.loc[pair, 'Action'] == 'BUY':
            if current_price_float > df_bh.loc[pair, 'min_price_float']:
                notification = '%19s | %8s | P %s | Not reached minimun price (%10.8f)' % ((datetime.datetime.fromtimestamp(float(data['E'])/1000).strftime("%Y-%m-%d %H:%M:%S"), pair, current_price_str, df_bh.loc[pair, 'min_price_float']))
                print(notification)
            if current_price_float <= df_bh.loc[pair, 'min_price_float']:
                df_bh.loc[pair, 'Action'] = 'WATCH'
                df_bh.loc[pair, 'LowerPrice'] = current_price_float
                df_bh.loc[pair, 'LastPrice'] = current_price_float
                notification =  '\n%19s | %8s | P %s | SB %s | Start watching\n' %(datetime.datetime.fromtimestamp(float(data['E'])/1000).strftime("%Y-%m-%d %H:%M:%S"), pair, current_price_str, df_bh.loc[pair, 'trigger_price_str'])
                print(notification)
                #bot.sendMessage(chat_id = XXXX, text = notification)
        if df_bh.loc[pair, 'Action'] == 'WATCH':
            if order_list[pair] != 0:
                if simulation == True:
                    if current_price_float >= df_bh.loc[pair, 'trigger_price_float']:
                            notification = '%19s | %8s | Bought at %.8f!\n' % (datetime.datetime.fromtimestamp(float(data['E'])/1000).strftime("%Y-%m-%d %H:%M:%S"), pair, current_price_float)
                            #bot.sendMessage(chat_id = XXXX, text = notification)
                            print ('--------------------------------------------------------------------------------------------------------')
                            print(notification)
                            print ('--------------------------------------------------------------------------------------------------------')
                            bm.close()
                            reactor.stop()
                            os._exit(1)
            elif order_list[pair] == 0:
                if current_price_float < df_bh.loc[pair, 'trigger_price_float']:
                    if current_price_float < df_bh.loc[pair, 'LowerPrice']:
                        df_bh.loc[pair, 'trigger_price_float'] = round(df_bh.loc[pair, 'margin'] * current_price_float, df_bh.loc[pair, 'Precision'])
                        df_bh.loc[pair, 'trigger_price_str'] = "{:10.8f}".format(df_bh.loc[pair, 'trigger_price_float'])
                        df_bh.loc[pair, 'buy_price_float'] = df_bh.loc[pair, 'trigger_price_float']
                        df_bh.loc[pair, 'buy_price_str'] = df_bh.loc[pair, 'trigger_price_str']
                        notification = '%19s | %8s | P %s | SB %s | %9s %5.0f uds | %s' % ((datetime.datetime.fromtimestamp(float(data['E'])/1000).strftime("%Y-%m-%d %H:%M:%S"), pair, current_price_str, df_bh.loc[pair, 'trigger_price_str'], mov1, float(data['q']), mov2))
                        print(notification)
                        df_bh.loc[pair, 'LowerPrice'] = current_price_float
                    elif current_price_float > df_bh.loc[pair, 'LowerPrice']:
                        if current_price_float != df_bh.loc[pair, 'LastPrice']:
                            notification = '%19s | %8s | P %s | SB %s | %9s %5.0f uds | %s' % ((datetime.datetime.fromtimestamp(float(data['E'])/1000).strftime("%Y-%m-%d %H:%M:%S"), pair, current_price_str, df_bh.loc[pair, 'trigger_price_str'], mov1, float(data['q']), mov2))
                            print(notification)
                elif current_price_float >= df_bh.loc[pair, 'trigger_price_float']:
                    if simulation == True:
                        order_list[pair] = 1

    df_bh.loc[pair, 'LastPrice'] = current_price_float

    if datetime.datetime.now() > stop:
        bm.close()
        clock_reset()
        print ('--------------------------------------------------------------------------------------------------------')
        print ('Restarting socket...')
        print ('--------------------------------------------------------------------------------------------------------')
        conn_key = bm.start_multiplex_socket(coins_list, process_message)


#######################################################
####             START WEBSOCKET                   ####
#######################################################

start = True
clock_reset()
bm = BinanceSocketManager(client)
conn_key = bm.start_multiplex_socket(coins_list, process_message)
bm.start()


#######################################################
####              TELEGRAM REPORT                  ####
#######################################################

check = True
while check == True:
    update = ''
    time.sleep(900)
    for pair in range (len(df)):
        update = update + '%s | P %10.8f | SB %10.8f\n\n' % (df_bh.iloc[pair]['Symbol'], df_bh.iloc[pair]['lastPrice'], df_bh.iloc[pair]['trigger_price_str'])
    #bot.sendMessage(chat_id = XXXX, text = update)

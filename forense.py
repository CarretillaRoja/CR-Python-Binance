# Chequea una moneda para investigar que paso

from binance.client import Client
import time
import datetime
import pandas as pd

api_key='XXXX'
api_secret='XXXX'
client = Client(api_key, api_secret, {"timeout": 2000})

coin = input('Introduce una moneda (p.ej.: ETHBTC): ')
tiempo = int(input('¿Cuántos MINUTOS miramos hacia atrás? '))
coin = coin.upper()

def horas(TS):
    time_stamp = datetime.datetime.fromtimestamp(TS/1000).strftime('%Y-%m-%d %H:%M:%S')
    return time_stamp

# Descargar las velas
def velas(vela_coin, interval, period):
    k = client.get_historical_klines(vela_coin, interval, period)
    for h in range(len(k)):
        k[h][0]=horas(k[h][0])
    return k

#kline=velas(coin, Client.KLINE_INTERVAL_1MINUTE, "1 hour ago")
kline=velas(coin, Client.KLINE_INTERVAL_1MINUTE, "1 day ago")

titles=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteVolume', 'TradeNumber', 'NA1', 'NA2', 'NA3']
df = pd.DataFrame(kline, columns=titles)
df = df.tail(tiempo)
df = df.drop(['TradeNumber', 'NA1', 'NA2', 'NA3'], 1)
print(df)

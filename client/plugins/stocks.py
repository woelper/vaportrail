"""
Read stock prices
pip install realtime-stock
"""
from _base_plugin import *

# Import what you like here
import urllib2
import json

INTERVAL = 300
CATEGORY = 'Finance'
STOCKNAMES = ['AAPL', 'GOOG', 'NVDA', 'AMD', 'TSLA']

from rtstock.stock import Stock

def get_price(stock_name):
    stock = Stock(stock_name)
    return stock.get_latest_price()[0]['LastTradePriceOnly']


def run():
    stocks = {}

    for stockname in STOCKNAMES:
        stocks['{}@{}min'.format(stockname, int(round(INTERVAL/60)))] = get_price(stockname)

    return stocks

if __name__ == '__main__':
    print run()
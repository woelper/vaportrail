"""
Read stock prices
pip install realtime-stock
"""
from _base_plugin import *

# Import what you like here
import urllib2
import json
import stocks

INTERVAL = 100000
CATEGORY = 'Finance'

def run():
    result = {}

    for stockname in stocks.STOCKNAMES:
        result['{}@{}min'.format(stockname, int(round(INTERVAL/60)))] = stocks.get_price(stockname)

    return result

if __name__ == '__main__':
    print run()
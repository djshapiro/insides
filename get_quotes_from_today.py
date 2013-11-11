import urllib2
import ipdb
import pymongo
import datetime

def rangeTuple(range, last_price):
    parsedRange = range.split("-")

    def floatOrNA(num):
        try:
            return float(num)
        except ValueError:
            return last_price

    return [floatOrNA(num) for num in parsedRange]


columns = ["symbol", "last_price", "range"]
column_format_mask = [str, float, rangeTuple]
db_url = "localhost"

mongo = pymongo.Connection(db_url)
db = mongo.test
it_collection = db.insiderTrades
q_collection = db.quotes
stock_symbols = '+'.join(it_collection.distinct("symbol"))
quotes = urllib2.urlopen('http://finance.yahoo.com/d/quotes.csv?s=' + stock_symbols + '&f=sl1m')
now = str(datetime.datetime.date(datetime.datetime.now()))
quotes = quotes.readlines()
quotes = [[thing.strip('"\r\n') for thing in quote.split(',')] for quote in quotes]

for quote in quotes:
    print quote
    symbol = column_format_mask[0](quote[0])
    last_price = column_format_mask[1](quote[1])
    day_range = column_format_mask[2](quote[2], last_price)
    quote_ref = {"symbol": symbol, "date": now}
    q_collection.update(quote_ref, {"$set": {"lastPrice": last_price, "range": day_range}}, upsert=True)

import urllib2
import ipdb
import pymongo
import datetime

#For converting a range string like
#    '1.23 - 4.21'
#to a list like
#    [1.23, 4.21]
def floatTuple(range_str, quote):
    default_price = quote["last_price"]
    parsedRange = range_str.split("-")

    def floatOrNA(num):
        try:
            return float(num)
        except ValueError:
            #We got "N/A", so just return the default price
            return default_price

    return [floatOrNA(num) for num in parsedRange]

#A functional for converting values. Just for fun, really.
def convert(value, func, *args):
    try:
        #Try to give the conversion function all the arguments.
        return func(value, *args)
    except TypeError:
        #The conversion function doesn't take extra arguments.
        return func(value)

#Initialize some stuff
new_quotes = []
num_new_quotes = 0
columns = ["symbol", "last_price", "day_range"]
column_format_mask = [str, float, floatTuple]
db_url = "localhost"

#Get most recent quotes (in csv) of all stocks we have insider trades for
mongo = pymongo.Connection(db_url)
db = mongo.test
it_collection = db.insiderTrades
q_collection = db.quotes
stock_symbols = '+'.join(it_collection.distinct("symbol"))
quotes = urllib2.urlopen('http://finance.yahoo.com/d/quotes.csv?s=' + stock_symbols + '&f=sl1m')

#Prepare csv data to be parsed
now = str(datetime.datetime.date(datetime.datetime.now()))
quotes = quotes.readlines()
quotes = [[thing.strip('"\r\n') for thing in quote.split(',')] for quote in quotes]

#Upsert each quote in the csv data
for quote in quotes:
    quote_info = {}

    #Convert the data to proper formats
    for ii in range(len(quote)):
        quote_info[columns[ii]] = convert(quote[ii], column_format_mask[ii], quote_info)

    #Upsert!
    quote_ref = {"symbol": quote_info["symbol"], "date": now}
    quote_price = {"lastPrice": quote_info["last_price"], "range": quote_info["day_range"]}
    q_collection.update(quote_ref, quote_price, upsert=True)

    #Keep track of how many quotes we saved, so we can tell the user
    num_new_quotes = num_new_quotes + 1

print "Upserting {} new quotes".format(num_new_quotes)

#TODO:
#Move strategies to mongo
#------
#Decide how much performance information to store in mongo: do we say whether each trade was a success or failure on each day? do we do that for strategies? For people? For companies?

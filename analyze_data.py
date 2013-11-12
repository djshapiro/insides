import urllib2
import ipdb
import pymongo
import datetime

db_url = "localhost"
TRADE_COST = 7

mongo = pymongo.Connection(db_url)
db = mongo.test
it_collection = db.insiderTrades
q_collection = db.quotes
stock_symbols = set(it_collection.distinct("symbol"))

find_winner_fn = {
        "Buy":  lambda quote, trade: quote > trade,
        "Sell": lambda quote, trade: quote < trade
}

winning_stocks = set()

for symbol in stock_symbols:
    trades = list(it_collection.find({"symbol": symbol}))
    quotes = q_collection.find({"symbol": symbol})
    quotes = list(quotes.sort("date", "ASCENDING"))
    #DJSFIXME Eventually pul these from a mongo collection
    #DJSFIXME Need a way to not save weekend data
    '''strategies = {"Buy": {
            "buy": {
                "order": "market",
                "whenPlaced": "1d"
            },
            "sell":
                "order": "market",
                "whenPlaced": "4d"
            }
        "Sell": {}
        },
        {"Buy": {
            "buy": {
                "order": "market",
                "whenPlaced": "1d"
            },
            "sell":
                "order": "limit",
                "whenPlaced": "1d"
                "whenFinished": "3m"
                "limit": "20%"
            }
        "Sell": {}
        }
        for strategy in strategies:
            stategy["portfolio"] = []'''
        
    for trade in trades:
        trade_price = trade["price"]
        trade_type = trade["type"]
        for quote in quotes:
            quote_price = quote["lastPrice"]
            if find_winner_fn[trade_type](quote_price, trade_price):
#DJSFIXME I don't think you can classify a stock as purely a winner or a loser. It's the actual trades that win or lose.
#DJSFIXME Need to verify that insider trades are made at public price
#DJSFIXME Compare results to a purchase on a random date of the same stock. Aggregate these results. They should make money 50% of the time (?). Do insider trades succeed more ofter than random trades?
                winning_stocks.add(symbol)
                #print "A winner is you: ", symbol, percent_change, trade_price, trade_type, quote_price
                #DJSFIXME Things I'll want to measure:
# - Which people make money this way (more than 50% of the time?)?
# - Which companies make money this way (more than 50% of the time?)? (We'll need to compare the behavior of this company with the behavior of this industry and the stock market as a whole)
# - Which industries make money this way (more than 50% of the time?)? (This will involve knowing which industries these companies belong to. We'll need to compare the behavior of this industry against the stock market as a whole)
                #Ways to measure "winning":
# - What distance (both absolute and percentage) does the price get from the trade price?
# - How long does the price stay above/below the trade price (not sure whether a longer time or a shorter time equals "winning")
# - How soon after a trade does a trade "win"?
                #Some metadata-y way to:
                #- Define metrics

print "These are the winners: ", winning_stocks

losing_stocks = stock_symbols - winning_stocks

for symbol in losing_stocks:
    trades = list(it_collection.find({"symbol": symbol}))
    quotes = q_collection.find({"symbol": symbol})
    quotes = list(quotes.sort("date", "DESCENDING"))
    latest_quote = quotes[0]
    quote_price = latest_quote["lastPrice"]
    for trade in trades:
        trade_price = trade["price"]
        trade_type = trade["type"]
        percent_change = (quote_price - trade_price) * 100 / trade_price
        print "Money losses: ", symbol, percent_change, trade_price, trade_type, quote_price

for symbol in winning_stocks:
    trades = list(it_collection.find({"symbol": symbol}))
    quotes = q_collection.find({"symbol": symbol})
#DJSFIXME Does this date sorting actually work? Would integer dates make more sense?
    quotes = list(quotes.sort("date", "DESCENDING"))
    latest_quote = quotes[0]
    quote_price = latest_quote["lastPrice"]
    for trade in trades:
        trade_price = trade["price"]
        trade_type = trade["type"]
        percent_change = (quote_price - trade_price) * 100 / trade_price
        print "Money gain: ", symbol, percent_change, trade_price, trade_type, quote_price

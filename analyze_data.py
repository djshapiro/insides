import urllib2
import ipdb
import pymongo
import datetime

db_url = "localhost"

mongo = pymongo.Connection(db_url)
db = mongo.test
it_collection = db.insiderTrades
q_collection = db.quotes
stock_symbols = set(it_collection.distinct("symbol"))

find_winner_fn = {
        "Buy":  lambda trade, quote: quote > trade,
        "Sell": lambda trade, quote: quote < trade
}

winning_stocks = set()

for symbol in stock_symbols:
    trades = list(it_collection.find({"symbol": symbol}))
    quotes = q_collection.find({"symbol": symbol})
    quotes = list(quotes.sort("date", "ASCENDING"))
    for trade in trades:
        trade_price = trade["price"]
        trade_type = trade["type"]
        for quote in quotes:
            quote_price = quote["price"]
            if find_winner_fn[trade_type](trade_price, quote_price):
                #print "WE FOUND A WINNER", symbol, trade_price, trade_type, quote_price
                winning_stocks.add(symbol)
                percent_change = (quote_price - trade_price) * 100 / trade_price
                print "A winner is you: ", symbol, percent_change, trade_price, trade_type, quote_price
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
                #- Test investment strategies

print "These are the winners: ", winning_stocks

losing_stocks = stock_symbols - winning_stocks

for symbol in losing_stocks:
    trades = list(it_collection.find({"symbol": symbol}))
    quotes = q_collection.find({"symbol": symbol})
    quotes = list(quotes.sort("date", "DESCENDING"))
    latest_quote = quotes[0]
    quote_price = latest_quote["price"]
    for trade in trades:
        trade_price = trade["price"]
        trade_type = trade["type"]
        percent_change = (quote_price - trade_price) * 100 / trade_price
        print "Money losses: ", symbol, percent_change, trade_price, trade_type, quote_price



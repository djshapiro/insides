import urllib2
import ipdb
import pymongo
import datetime

#Initialize some stuff
db_url = "localhost"
winners = 0
losers = 0
ties = 0
all_perc = 0
all_profit = 0
all_cost = 0

profit_fn = {
        "Buy":  lambda quote, trade: quote - trade,
        "Sell": lambda quote, trade: trade - quote
}

mongo = pymongo.Connection(db_url)
db = mongo.test
it_collection = db.insiderTrades
q_collection = db.quotes
s_collection = db.strategies
stock_symbols = set(it_collection.distinct("symbol"))
now = str(datetime.datetime.date(datetime.datetime.now()))

'''for symbol in stock_symbols:
    s_index = {"symbol": symbol}
    sd_index = s_index.copy().update({"date": now})
    latest_quote = q_collection.find({"symbol": symbol, "date": now})
    trades = it_collection.find({"symbol": symbol})
    if latest_quote.count() != 1:
        print "ERROR: {} has {} quotes for {}".format(symbol, latest_quote.count(), now)

    #DJSFIXME Is there a better way to do this?
    quote = latest_quote.next()

    for trade in trades:
        profit = profit_fn[trade["type"]](quote["lastPrice"], trade["price"])
        if trade["price"] != 0:
            percent = 100 * profit/trade["price"]
        else:
            percent = 0
        if trade["type"] == "Buy":
            all_perc = all_perc + percent
            all_profit = all_profit + profit
            all_cost = all_cost + trade["price"]
        if profit > 0:
            winners = winners + 1
        elif profit < 0:
            losers = losers + 1
        else:
            ties = ties + 1
        #it_collection.update(trade, {'$push': {"profits": {"date": now, "profit": profit}}}, upsert=True) 

        print "{} made {} on {} or {}%".format(symbol, profit, now, percent)
        
    #Evaluate each trade compared to today's quote. Put results on trade (results can be a list of objects, each object containing parameters "date" and "profit")'''

strategies = s_collection.find({})
for strategy in strategies:
    print strategy
    #Evaluate each strategy compared to today's quotes. Put results on strategy (results can be a list of objects, each object containing parameters "date" and "profit")

print "\n------------------\n\nwinners: {}\nlosers:  {}\nties:    {}".format(winners, losers, ties)

print "\n------------------\n\ntotal calculated: {}%".format(all_profit/all_cost)


'''for symbol in stock_symbols:
    trades = list(it_collection.find({"symbol": symbol}))
    quotes = q_collection.find({"symbol": symbol})
    quotes = quotes.sort("date", pymongo.ASCENDING)
    #DJSFIXME Eventually pull these from a mongo collection
    strategies = {"Buy": {
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
            stategy["portfolio"] = []
        
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
    quotes = list(quotes.sort("date", pymongo.DESCENDING))
    latest_quote = quotes[0]
    quote_price = latest_quote["lastPrice"]
    for trade in trades:
        trade_price = trade["price"]
        trade_type = trade["type"]
        if trade_price == 0:
            continue
        percent_change = (quote_price - trade_price) * 100 / trade_price
        print "Money losses: ", symbol, percent_change, trade_price, trade_type, quote_price

for symbol in winning_stocks:
    trades = list(it_collection.find({"symbol": symbol}))
    quotes = q_collection.find({"symbol": symbol})
    quotes = list(quotes.sort("date", pymongo.DESCENDING))
    latest_quote = quotes[0]
    quote_price = latest_quote["lastPrice"]
    for trade in trades:
        trade_price = trade["price"]
        trade_type = trade["type"]
        if trade_price == 0:
            continue
        percent_change = (quote_price - trade_price) * 100 / trade_price
        print "Money gain: ", symbol, percent_change, trade_price, trade_type, quote_price'''

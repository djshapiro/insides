import urllib2
import ipdb
import pymongo
import datetime

#Initialize some stuff
db_url = "localhost"

profit_fn = {
        "Buy":  lambda quote, trade: quote - trade,
        "Sell": lambda quote, trade: trade - quote
}

comparator_fn = {
    "greaterThan": lambda quote, datum: quote > datum,
    "lessThan": lambda quote, datum: quote < datum
}

def getValueDeep(values, path):
    '''Get a value from a dictionary that is an arbitrary number of levels deep
    
       values: the dictionary to get values from
       path: a list containing the successive keys that point to the desired value'''
    if len(path) > 1:
        return getValueDeep(values[path[0]], path[1:])
    else:
        return values[path[0]]

def matchTradeFilter(trade, strategy):
    '''Find which filter in this strategy matches this trade

       trade: The insider trade to be matched
       strategy: The strategy attempting to use this trade as investment advice'''
    matching_filter = {}
    for trade_filter in strategy["tradeFilters"]:
        this_filter_matches = True
        if trade_filter.has_key("if"):
            for condition in trade_filter["if"]:
                if trade_filter["if"][condition] != getValueDeep(trade, condition.split("-")[1:]):
                    this_filter_matches = False
                    break
            if this_filter_matches:
                matching_filter = trade_filter
                break
        else:
            matching_filter = trade_filter

    return matching_filter

def applyTradeFilterDefaults(trade, trade_filter):
    '''Make a trade filter usable if it doesn't have all the required information

       trade: The trade we're eventually going to mimic. If needed, we'll take
              default information from trade.
       trade_filter: The filter to apply defaults to

       SIDE EFFECTS: trade_filter may be mutated'''

    if not trade_filter.has_key("begin"):
        trade_filter["begin"] = {
            "orderType": trade["type"],
            "whenPlaced": "1d",
            "order": "market"
        }

    if not trade_filter.has_key("end"):
        trade_filter["end"] = {
            "orderType": "Buy" if trade["type"]=="Sell" else "Sell",
            "whenPlaced": "",
            "order": "market"
        }

    return
       
def makeTrade(trade, parameters):
    '''Simulate a trade according to the given parameters.

       trade: The insider trade we're basing our trade on
       parameters: Parameters of the trade we're making'''
    #DJSFIXME whenPlaced == "" means today's date (like we haven't actualized the returns on this one yet)

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

if __name__ == "__main__":
    strategies = s_collection.find({})
    for strategy in strategies:
        for symbol in stock_symbols:
            s_index = {"symbol": symbol}
            sd_index = s_index.copy().update({"date": now})
            quotes = q_collection.find({"symbol": symbol})
            quotes = quotes.sort("date", pymongo.ASCENDING)
            trades = it_collection.find({"symbol": symbol})
            for trade in trades:
                trade_filter = matchTradeFilter(trade, strategy)
                applyTradeFilterDefaults(trade, trade_filter)
                begin_trade = makeTrade(trade, trade_filter["begin"])
                end_trade = makeTrade(trade, trade_filter["end"])
        #Evaluate each strategy compared to today's quotes. Put results on strategy (results can be a list of objects, each object containing parameters "date" and "profit")

#print "\n------------------\n\nwinners: {}\nlosers:  {}\nties:    {}".format(winners, losers, ties)
#print "\n------------------\n\ntotal calculated: {}%".format(all_profit/all_cost)


'''for symbol in stock_symbols:
    trades = list(it_collection.find({"symbol": symbol}))
    quotes = q_collection.find({"symbol": symbol})
    quotes = quotes.sort("date", pymongo.ASCENDING)
    #DJSFIXME Eventually pull these from a mongo collection

    strategies = [
        {
            tradeFilters: [
                {
                    if: {
                        tradeType: "Buy",
                        price: {
                            "comparator": "greaterThan",
                            "datum": 24
                        }
                    },
                    begin: {
                        orderType: "Buy",
                        whenPlaced: "1d",
                        order: "market"
                    },
                    end: {
                        orderType: "Sell",
                        whenPlaced: "10d",
                        order: "market"
                    }
                },
                {...},
                {
                    begin: {
                        orderType: "Buy",
                        ...
                    }
                }
            ]
        },
        {...}
    ]
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

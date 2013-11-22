import urllib2
import ipdb
import pymongo

#Initialize some stuff
columns = ["FAKE1", "symbol", "company", "name", "type", "shares", "price", "value", "time", "date"]
column_format_mask = [None, str, str, str, str, int, float, None, None, str]
db_url = "localhost"
new_trades = []
defaults = {}

#DJSFIXME I probably should have made the conversions objects rather than a big list of functions. The objects could contain validation information, too.
#DJSFIXME Make sure trades are made at market price
#DJSFIXME Consider an API that parses SEC form 4s to get trade info

def save_trade_from_html(elements, defaults):
    '''Takes a list of the elements of an insider trading transaction
       and turns them into an object representing the transaction.
       The elements get scrubbed of any html and extra junk.
       Saves this trade to the database and returns it.'''
    new_insider_trade = {}

    for ii in range(len(elements)):
        #remove closing td tag
        element = elements[ii].replace("</td>", "")

        #remove remainder of opening td tag
        start = element.find('>')
        element = element[start+1:]

        #remove all other tags
        while True:
            beginning_start = element.find('<')
            beginning_end = element.find('>', beginning_start)
            if beginning_start > -1:
                element = element[:beginning_start] + element[beginning_end+1:]
            else:
                break

        #remove white space
        element = element.strip()

        #If we've specified a conversion function for this element, convert and store.
        #Otherwise, ignore this element.
        func = column_format_mask[ii]
        if func:
            if func == int or func == float:
                element = element.replace(",", "")
            new_insider_trade[columns[ii]] = func(element)

    #Combine date and time
    #if new_insider_trade.has_key("date") and new_insider_trade.has_key("time"):
    #    date = new_insider_trade.pop("date")
    #    time = new_insider_trade.pop("time")
    #    dt = datetime.datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S")
    #    new_insider_trade["dt"] = str(dt)

    #Apply validation
    if new_insider_trade.has_key("symbol") and " " in new_insider_trade["symbol"]:
        #Ignore this if the symbol is bad
        return {}

    #Apply defaults
    if new_insider_trade.has_key("symbol") and new_insider_trade["symbol"] == "&nbsp;":
        new_insider_trade["symbol"] = defaults["symbol"]

    #Add trade to the database if we don't already have it
    if new_insider_trade:
        results = collection.find(new_insider_trade)
        if not results.count():
            collection.insert(new_insider_trade)
            new_trades.append(new_insider_trade)

    return new_insider_trade

#Get the mongo collection
mongo = pymongo.Connection(db_url)
db = mongo.test
collection = db.insiderTrades

#Get raw html of recent insider trades
response = urllib2.urlopen('http://www.insider-monitor.com/insider_stock_purchases.html')
response = response.readlines()
for line in response:
    if "<tr>" in line:
        for tag in ["<tr>", "</tr>"]:
            line = line.replace(tag, "")
        new_trade = save_trade_from_html(line.split("<td"), defaults)
        if new_trade.has_key("symbol"):
            defaults["symbol"] = new_trade["symbol"]

if new_trades:
    print "New trades were saved.\n\n" + str(new_trades)
else:
    print "No new trades were saved."

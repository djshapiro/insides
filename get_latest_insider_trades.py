import urllib2
import ipdb
import pymongo

columns = ["FAKE1", "symbol", "company", "name", "type", "shares", "price", "value", "time", "date"]
column_format_mask = [None, str, str, str, str, int, float, None, None, str]
db_url = "localhost"

def create_trade_from_html(elements, defaults):
    '''Takes a list of the elements of an insider trading transaction
       and turns them into an object representing the transaction.
       The elements get scrubbed of any html and extra junk.'''
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

        element = element.strip()
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

    #Apply defaults
    if new_insider_trade.has_key("symbol") and new_insider_trade["symbol"] == "&nbsp;":
        new_insider_trade["symbol"] = defaults["symbol"]

    symbol = ""
    if new_insider_trade:
        symbol = new_insider_trade["symbol"]
        collection.insert(new_insider_trade)

    return symbol



#################
#Parse new data and add it to the database
#################

new_insider_trades = []
defaults = {}
mongo = pymongo.Connection(db_url)
db = mongo.test
collection = db.insiderTrades

#Parse new data from the internet
response = urllib2.urlopen('http://www.insider-monitor.com/insider_stock_purchases.html')
response = response.readlines()
for line in response:
    if "<tr>" in line:
        for tag in ["<tr>", "</tr>"]:
            line = line.replace(tag, "")
        symbol = create_trade_from_html(line.split("<td"), defaults)
        if symbol:
            defaults["symbol"] = symbol

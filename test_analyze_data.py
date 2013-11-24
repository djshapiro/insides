import unittest
from analyze_data import getValueDeep, matchTradeFilter, applyTradeFilterDefaults, makeTrade

test_dict = {
        "a": 1,
        "b": {
            "c": 2
        },
        "d": {
            "e": {
                "f": 3,
                "g": {
                    "h": {
                        "i": 4
                    }
                }
            }
        }
    }

trades = [
        {
            "name": "Leap Day William",
            "price": 1.24,
            "shares": 10,
            "company": "Mariana Fishing Corp.",
            "date": "2012-02-29",
            "type": "Buy",
            "symbol": "MFC"
        },
        {
            "name": "Ogbert Jordan",
            "price": "403.05",
            "shares": 3000,
            "company": "Bank Sign Dismantlers, Inc.",
            "date": "2008-09-01",
            "type": "Buy",
            "symbol": "BSDI"
        },
        {
            "name": "John Francis Donaghy",
            "price": 15,
            "shares": 200,
            "company": "General Electric",
            "date": "2012-07-03",
            "type": "Sell",
            "symbol": "GE"
        }
    ]

strategies = [
        {
            "tradeFilters": [
                {
                    "if": {
                        "trade-type": "Buy"
                    },
                    "begin": {
                        "orderType": "Buy",
                        "whenPlaced": "@trade-date:+1d",
                        "order": "market"
                    },
                    "end": {
                        "orderType": "Sell",
                        "whenPlaced": "@trade-date:+10d",
                        "order": "market"
                    }
                },
                {
                    "begin": {
                        "orderType": "Buy",
                        "whenPlaced": "@trade-date:+1d",
                        "order": "market"
                    }
                }
            ]
        }
    ]


class Tests(unittest.TestCase):

    def testGetValueDeep1(self):
        self.failUnless(getValueDeep(test_dict, ["a"]) == 1)
        
    def testGetValueDeep2(self):
        self.failUnless(getValueDeep(test_dict, ["b", "c"]) == 2)

    def testGetValueDeep3(self):
        self.failUnless(getValueDeep(test_dict, ["d", "e", "f"]) == 3)

    def testGetValueDeep4(self):
        self.failUnless(getValueDeep(test_dict, ["d", "e", "g", "h", "i"]) == 4)

    def testMatchTradeFilter1(self):
        self.failUnless(matchTradeFilter(trades[0], strategies[0]) == strategies[0]["tradeFilters"][0])

    def testMatchTradeFilter2(self):
        self.failUnless(matchTradeFilter(trades[1], strategies[0]) == strategies[0]["tradeFilters"][0])
        
    def testMatchTradeFilter3(self):
        self.failUnless(matchTradeFilter(trades[2], strategies[0]) == strategies[0]["tradeFilters"][1])

def main():
    unittest.main()

main()

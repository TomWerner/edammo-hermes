from ibapi import wrapper
from ibapi.client import EClient

import numpy as np
import pickle
from ibapi.contract import *
import datetime
import time


class Contracts:
    @staticmethod
    def get_contract(symbolIn, exchangeIn="ISLAND", secTypeIn="STK", currencyIn="USD"):
        contract = Contract()
        contract.symbol = symbolIn
        contract.secType = secTypeIn
        contract.currency = currencyIn
        contract.exchange = exchangeIn

        return contract


class HistoricalDataFinishedException(Exception):
    pass


class HistoricalDataApp(wrapper.EWrapper, EClient):
    def __init__(self, date, contract, granularity=30):
        """
        :type date: datetime.datetime
        :type contract: Contract
        :type granularity: int
        """
        wrapper.EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.started = False

        self.start_date = date
        self.granularity = granularity
        self.contract = contract

        self.target_ts = []
        self.feature_ts = []

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.start()

    def start(self):
        if self.started:
            return
        self.started = True

        # TODO: whatToShow can also ask for bid and ask prices, add this in future
        duration = '28800 S'  # 8 hours
        regular_hours_only = True  # only use regular trading hours

        self.reqHistoricalData(1, self.contract, endDateTime=self.start_date.strftime("%Y%m%d %H:%M:%S"),
                               durationStr=duration, barSizeSetting='%d secs' % self.granularity, whatToShow="TRADES",
                               useRTH=regular_hours_only, formatDate=1, chartOptions=[])

    def historicalData(self, reqId, date, open, high, low, close, volume, barCount, WAP, hasGaps):
        super().historicalData(reqId, date, open, high, low, close, volume, barCount, WAP, hasGaps)
        self.target_ts.append(close)
        self.feature_ts.append((open + close) / 2)

    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        self.target_ts = np.array(self.target_ts)
        self.feature_ts = np.array(self.feature_ts)
        raise HistoricalDataFinishedException()


def get_historical_data(contract_list, end_date, num_days, cache_location, granularity=30):
    """
    :type contract_list: list[Contract]
    :type end_date: datetime.datetime
    :type num_days: int
    :type cache_location: str
    :type granularity: int
    :return: 
    """

    for contract in contract_list:
        for i in range(num_days):
            date_end = end_date + datetime.timedelta(days=-i)
            date_end = datetime.datetime(date_end.year, date_end.month, date_end.day, 16, 0, 0)
            date_beginning = datetime.datetime(date_end.year, date_end.month, date_end.day, 10, 0, 0)
            app = HistoricalDataApp(date_end, contract, granularity=granularity)
            app.connect("127.0.0.1", 7497, clientId=0)
            try:
                app.run()
            except HistoricalDataFinishedException:
                pass

            granularity_filename = cache_location + 'api_' + contract.symbol + "_" + \
                                   str(date_beginning.timestamp()) + "_" + \
                                   str(date_end.timestamp()) + "_" + str(granularity) + "_.pkl"
            pickle.dump(((app.feature_ts, app.target_ts, date_beginning, date_end), date_beginning, date_end),
                        open(granularity_filename, 'wb'))
            time.sleep(10)  # Pain in the ass, but rate limit requires this. Be sure to cache this data!!!!


def main():
    get_historical_data(
        [Contracts.get_contract(symbol) for symbol in ['AAPL', 'GOOG', 'IBM']],
        datetime.datetime.now(), 10,
        r'C:\Users\Tom\Documents\startup\data-pipeline\data-collection\edammo_test_run_worker\scratch\stock_data_cache')


if __name__ == '__main__':
    main()
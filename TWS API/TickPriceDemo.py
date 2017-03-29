"""
Copyright (C) 2016 Interactive Brokers LLC. All rights reserved.  This code is
subject to the terms and conditions of the IB API Non-Commercial License or the
 IB API Commercial License, as applicable.
"""

import argparse
import collections
import datetime
import queue

import logging
import time
import os.path

from ibapi import wrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper

# types
from ibapi.order_condition import *
from ibapi.ticktype import *
from ibapi import (comm)
from ibapi.common import *
from ibapi.contract import Contract
from ibapi.utils import (BadMessage)
from ibapi.errors import *




def SetupLogger():
    if not os.path.exists("log"):
        os.makedirs("log")

    time.strftime("pyibapi.%Y%m%d_%H%M%S.log")

    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'

    timefmt = '%y%m%d_%H:%M:%S'

    # logging.basicConfig( level=logging.DEBUG,
    #                    format=recfmt, datefmt=timefmt)
    logging.basicConfig(filename=time.strftime("log/pyibapi.%y%m%d_%H%M%S.log"),
                        filemode="w",
                        level=logging.INFO,
                        format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    logger.addHandler(console)


class Activity(Object):
    def __init__(self, reqMsgId, ansMsgId, ansEndMsgId, reqId):
        self.reqMsdId = reqMsgId
        self.ansMsgId = ansMsgId
        self.ansEndMsgId = ansEndMsgId
        self.reqId = reqId


class RequestMgr(Object):
    def __init__(self):
        # I will keep this simple even if slower for now: only one list of
        # requests finding will be done by linear search
        self.requests = []

    def addReq(self, req):
        self.requests.append(req)

    def receivedMsg(self, msg):
        pass

class Contracts:

    @staticmethod
    def get_contract(symbolIn, exchangeIn = "IDEAL", secTypeIn = "CASH", currencyIn = "USD"):
        contract = Contract()
        contract.symbol = symbolIn
        contract.secType = secTypeIn
        contract.currency = currencyIn
        contract.exchange = exchangeIn

        return contract


# ! [socket_init]
class TestApp(wrapper.EWrapper, EClient):
    container = {"id": "", "price": "", "size": "", "time": ""}
    price = ()
    size = ()

    def __init__(self):
        wrapper.EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        # ! [socket_init]
        self.nKeybInt = 0
        self.started = False
        self.nextValidOrderId = None
        self.permId2ord = {}
        self.reqId2nErr = collections.defaultdict(int)


    def run(self):
        """This is the function that has the message loop."""
        threshold = datetime.datetime.now()
        threshold = threshold + datetime.timedelta(0,30)
        try:
            while not self.done and (self.conn.isConnected()
                        or not self.msg_queue.empty()):
                if datetime.datetime.now() <= threshold:
                    try:
                        try:
                            text = self.msg_queue.get(block=True, timeout=0.2)
                            if len(text) > MAX_MSG_LEN:
                                self.wrapper.error(NO_VALID_ID, BAD_LENGTH.code(),
                                    "%s:%d:%s" % (BAD_LENGTH.msg(), len(text), text))
                                self.disconnect()
                                break
                        except queue.Empty:
                            logging.debug("queue.get: empty")
                        else:
                            fields = comm.read_fields(text)
                            logging.debug("fields %s", fields)
                            self.decoder.interpret(fields)
                    except (KeyboardInterrupt, SystemExit):
                        logging.info("detected KeyboardInterrupt, SystemExit")
                        self.keyboardInterrupt()
                        self.keyboardInterruptHard()
                    except BadMessage:
                        logging.info("BadMessage")
                        self.conn.disconnect()

                    logging.debug("conn:%d queue.sz:%d",
                             self.conn.isConnected(),
                             self.msg_queue.qsize())
                else:
                    threshold = threshold + datetime.timedelta(seconds=30)
                    self.container["price"] = sum(self.price)
                    self.container["size"] = sum(self.size)
                    print(self.container)
                    self.price = ()
                    self.size = ()
        finally:
            self.disconnect()


    @iswrapper
    # ! [connectack]
    def connectAck(self):
        if self.async:
            self.startApi()
    # ! [connectack]

    @iswrapper
    # ! [nextvalidid]
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        logging.debug("setting nextValidOrderId: %d", orderId)
        # ! [nextvalidid]

        # we can start now
        self.start()

    def start(self):
        if self.started:
            return

        self.started = True

        print("Executing requests")
        self.marketDataType_req()
        self.tickDataOperations_req()

        print("Executing requests ... finished")

    def keyboardInterrupt(self):
        self.nKeybInt += 1
        if self.nKeybInt == 1:
            self.stop()
        else:
            print("Finishing test")
            self.done = True

    def stop(self):
        print("Executing cancels")
        self.tickDataOperations_cancel()
        print("Executing cancels ... finished")


    @iswrapper
    # ! [error]
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id: ", reqId, " Code: ", errorCode, " Msg: ", errorString)
    # ! [error] self.reqId2nErr[reqId] += 1


    @iswrapper
    def winError(self, text: str, lastError: int):
        super().winError(text, lastError)

    def tickDataOperations_req(self):
        # Requesting real time market data

        # ! [reqmktdata]
        #self.reqMktData(1101, Contracts.get_contract("EUR"), "", False, False, [])
        self.reqMktData(1102, Contracts.get_contract("AAPL", "ISLAND", "STK"), "", False, False, [])
        #self.reqMktData(1103, Contracts.get_contract("MSFT"), "", False, False, [])
        #self.reqMktData(1104, Contracts.get_contract("FB"), "", False, False, [])

        # ! [reqsmartcomponents]
        # Requests description of map of single letter exchange codes to full exchange names
        self.reqSmartComponents(1013, "a6")
        # ! [reqsmartcomponents]

    def tickDataOperations_cancel(self):
        # Canceling the market data subscription
        # ! [cancelmktdata]
        #self.cancelMktData(1101)
        self.cancelMktData(1102)
        # ! [cancelmktdata]

    @iswrapper
    # ! [tickprice]
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float,
                  attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        print("Tick Price. Ticker Id:", reqId, "Price:", price)
        self.price = self.price + (price,)
        print(self.price)
    # ! [tickprice]


    @iswrapper
    # ! [ticksize]
    def tickSize(self, reqId: TickerId, tickType: TickType, size: int):
        super().tickSize(reqId, tickType, size)
        print("Tick Size. Ticker Id:", reqId, "Size:", size)
        self.size = self.size + (size,)
        print(self.size)
    # ! [ticksize]


    @iswrapper
    # ! [smartcomponents]
    def smartComponents(self, reqId:int, map:SmartComponentMap):
        super().smartComponents(reqId, map)
        print("smartComponents: ")
        for exch in map:
            print(exch.bitNumber, ", Exchange Name: ", exch.exchange, ", Letter: ", exch.exchangeLetter)
    # ! [smartcomponents]

    def marketDataType_req(self):
        # ! [reqmarketdatatype]
        # Switch to live (1) frozen (2) delayed (3) delayed frozen (4).
        self.reqMarketDataType(MarketDataTypeEnum.DELAYED)
    # ! [reqmarketdatatype]

    def miscelaneous_req(self):
        # Request TWS' current time ***/
        self.reqCurrentTime()
        # Setting TWS logging level  ***/
        self.setServerLogLevel(1)

def main():


    SetupLogger()
    logging.debug("now is %s", datetime.datetime.now())
    logging.getLogger().setLevel(logging.DEBUG)

    cmdLineParser = argparse.ArgumentParser("api tests")
    # cmdLineParser.add_option("-c", action="store_True", dest="use_cache", default = False, help = "use the cache")
    # cmdLineParser.add_option("-f", action="store", type="string", dest="file", default="", help="the input file")
    cmdLineParser.add_argument("-p", "--port", action="store", type=int,
                               dest="port", default=7497, help="The TCP port to use")
    cmdLineParser.add_argument("-C", "--global-cancel", action="store_true",
                               dest="global_cancel", default=False,
                               help="whether to trigger a globalCancel req")
    args = cmdLineParser.parse_args()
    print("Using args", args)
    logging.debug("Using args %s", args)
    # print(args)


    # enable logging when member vars are assigned
    from ibapi import utils
    from ibapi.order import Order
    Order.__setattr__ = utils.setattr_log
    from ibapi.contract import Contract, UnderComp
    Contract.__setattr__ = utils.setattr_log
    UnderComp.__setattr__ = utils.setattr_log
    from ibapi.tag_value import TagValue
    TagValue.__setattr__ = utils.setattr_log
    TimeCondition.__setattr__ = utils.setattr_log
    ExecutionCondition.__setattr__ = utils.setattr_log
    MarginCondition.__setattr__ = utils.setattr_log
    PriceCondition.__setattr__ = utils.setattr_log
    PercentChangeCondition.__setattr__ = utils.setattr_log
    VolumeCondition.__setattr__ = utils.setattr_log

    # from inspect import signature as sig
    # import code code.interact(local=dict(globals(), **locals()))
    # sys.exit(1)

    # tc = TestClient(None)
    # tc.reqMktData(1101, ContractSamples.USStockAtSmart(), "", False, None)
    # print(tc.reqId2nReq)
    # sys.exit(1)

    try:
        app = TestApp()
        app.connect("127.0.0.1", args.port, clientId=0)
        print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),
                                                      app.twsConnectionTime()))
        # ! [connect]
        app.run()

    except:
        raise


if __name__ == "__main__":
    main()

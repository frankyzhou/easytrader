# -*- coding: utf-8 -*-
__author__ = 'frankyzhou'

from swigibpy import EWrapper, EPosixClientSocket, ExecutionFilter
from swigibpy import Order as IBOrder

from easytrader.IButils import bs_resolve, action_ib_fill
from trade.util import *
import time

MAX_WAIT_SECONDS=10
MEANINGLESS_NUMBER=1729

## This is the reqId IB API sends when a fill is received
FILL_CODE=-1

def return_IB_connection_info():
    """
    Returns the tuple host, port, clientID required by eConnect

    """

    host=""

    port=7496
    clientid=999

    return (host, port, clientid)

class IBWrapper(EWrapper):
    """

    Callback object passed to TWS, these functions will be called directly by the TWS or Gateway.

    """

    def init_error(self):
        setattr(self, "flag_iserror", False)
        setattr(self, "error_msg", "")

    def error(self, id, errorCode, errorString):
        """
        error handling, simple for now

        Here are some typical IB errors
        INFO: 2107, 2106
        WARNING 326 - can't connect as already connected
        CRITICAL: 502, 504 can't connect to TWS.
            200 no security definition found
            162 no trades

        """
        ## Any errors not on this list we just treat as information
        ERRORS_TO_TRIGGER=[201, 103, 502, 504, 509, 200, 162, 420, 2105, 1100, 478, 201, 399]

        if errorCode in ERRORS_TO_TRIGGER:
            errormsg="IB error id %d errorcode %d string %s" %(id, errorCode, errorString)
            print errormsg

            setattr(self, "flag_iserror", True)
            setattr(self, "error_msg", True)

        ## Wrapper functions don't have to return anything

    """
    Following methods will be called, but we don't use them
    """

    def nextValidId(self, id):
        pass

    def managedAccounts(self, openOrderEnd):
        pass

    def orderStatus(self, reqid, status, filled, remaining, avgFillPrice, permId,
            parentId, lastFilledPrice, clientId, whyHeld):
        pass

    def commissionReport(self, blah):
        pass

    def updateAccountTime(self, timeStamp):
        pass



    """
    get stuff
    """

    def init_fill_data(self):
        setattr(self, "data_fill_data", {})
        setattr(self, "flag_fill_data_finished", False)

    def add_fill_data(self, reqId, execdetails):
        if "data_fill_data" not in dir(self):
            filldata={}
        else:
            filldata=self.data_fill_data

        if reqId not in filldata.keys():
            filldata[reqId]={}

        execid=execdetails['orderid']
        filldata[reqId][execid]=execdetails

        setattr(self, "data_fill_data", filldata)


    def execDetails(self, reqId, contract, execution):

        """
        This is called if

        a) we have submitted an order and a fill has come back
        b) We have asked for recent fills to be given to us

        We populate the filldata object and also call action_ib_fill in case we need to do something with the
          fill data

        See API docs, C++, SocketClient Properties, Contract and Execution for more details
        """
        reqId=int(reqId)

        execid=execution.execId
        exectime=execution.time
        thisorderid=int(execution.orderId)
        account=execution.acctNumber
        exchange=execution.exchange
        permid=execution.permId
        avgprice=execution.price
        cumQty=execution.cumQty
        clientid=execution.clientId
        symbol=contract.symbol
        expiry=contract.expiry
        side=execution.side

        execdetails=dict(side=str(side), times=str(exectime), orderid=str(thisorderid), qty=int(cumQty), price=float(avgprice), symbol=str(symbol), expiry=str(expiry), clientid=str(clientid), execid=str(execid), account=str(account), exchange=str(exchange), permid=int(permid))

        if reqId==FILL_CODE:
            ## This is a fill from a trade we've just done
            action_ib_fill(execdetails)

        else:
            ## This is just execution data we've asked for
            self.add_fill_data(reqId, execdetails)


    def execDetailsEnd(self, reqId):
        """
        No more orders to look at if execution details requested
        """

        setattr(self, "flag_fill_data_finished", True)


    def init_openorders(self):
        setattr(self, "data_order_structure", {})
        setattr(self, "flag_order_structure_finished", False)

    def add_order_data(self, orderdetails):
        if "data_order_structure" not in dir(self):
            orderdata={}
        else:
            orderdata=self.data_order_structure

        orderid=orderdetails['orderid']
        orderdata[orderid]=orderdetails

        setattr(self, "data_order_structure", orderdata)


    def openOrder(self, orderID, contract, order, orderState):
        """
        Tells us about any orders we are working now

        Note these objects are not persistent or interesting so we have to extract what we want


        """

        ## Get a selection of interesting things about the order
        orderdetails=dict(symbol=contract.symbol , expiry=contract.expiry,  qty=int(order.totalQuantity) ,
                       side=order.action , orderid=int(orderID), clientid=order.clientId )

        self.add_order_data(orderdetails)

    def openOrderEnd(self):
        """
        Finished getting open orders
        """
        setattr(self, "flag_order_structure_finished", True)


    def init_nextvalidid(self):
        setattr(self, "data_brokerorderid", None)


    def nextValidId(self, orderId):
        """
        Give the next valid order id

        Note this doesn't 'burn' the ID; if you call again without executing the next ID will be the same
        """

        self.data_brokerorderid=orderId


    def init_contractdetails(self, reqId):
        if "data_contractdetails" not in dir(self):
            dict_contractdetails=dict()
        else:
            dict_contractdetails=self.data_contractdetails

        dict_contractdetails[reqId]={}
        setattr(self, "flag_finished_contractdetails", False)
        setattr(self, "data_contractdetails", dict_contractdetails)


    def contractDetails(self, reqId, contractDetails):
        """
        Return contract details

        If you submit more than one request watch out to match up with reqId
        """

        contract_details=self.data_contractdetails[reqId]

        contract_details["contractMonth"]=contractDetails.contractMonth
        contract_details["liquidHours"]=contractDetails.liquidHours
        contract_details["longName"]=contractDetails.longName
        contract_details["minTick"]=contractDetails.minTick
        contract_details["tradingHours"]=contractDetails.tradingHours
        contract_details["timeZoneId"]=contractDetails.timeZoneId
        contract_details["underConId"]=contractDetails.underConId
        contract_details["evRule"]=contractDetails.evRule
        contract_details["evMultiplier"]=contractDetails.evMultiplier

        contract2 = contractDetails.summary

        contract_details["expiry"]=contract2.expiry

        contract_details["exchange"]=contract2.exchange
        contract_details["symbol"]=contract2.symbol
        contract_details["secType"]=contract2.secType
        contract_details["currency"]=contract2.currency

    def contractDetailsEnd(self, reqId):
        """
        Finished getting contract details
        """

        setattr(self, "flag_finished_contractdetails", True)

    ## contract details

    def init_contractdetails(self, reqId):
        if "data_contractdetails" not in dir(self):
            dict_contractdetails=dict()
        else:
            dict_contractdetails=self.data_contractdetails

        dict_contractdetails[reqId]={}
        setattr(self, "flag_finished_contractdetails", False)
        setattr(self, "data_contractdetails", dict_contractdetails)


    def contractDetails(self, reqId, contractDetails):
        """
        Return contract details

        If you submit more than one request watch out to match up with reqId
        """

        contract_details=self.data_contractdetails[reqId]

        contract_details["contractMonth"]=contractDetails.contractMonth
        contract_details["liquidHours"]=contractDetails.liquidHours
        contract_details["longName"]=contractDetails.longName
        contract_details["minTick"]=contractDetails.minTick
        contract_details["tradingHours"]=contractDetails.tradingHours
        contract_details["timeZoneId"]=contractDetails.timeZoneId
        contract_details["underConId"]=contractDetails.underConId
        contract_details["evRule"]=contractDetails.evRule
        contract_details["evMultiplier"]=contractDetails.evMultiplier

        contract2 = contractDetails.summary

        contract_details["expiry"]=contract2.expiry

        contract_details["exchange"]=contract2.exchange
        contract_details["symbol"]=contract2.symbol
        contract_details["secType"]=contract2.secType
        contract_details["currency"]=contract2.currency

    def contractDetailsEnd(self, reqId):
        """
        Finished getting contract details
        """

        setattr(self, "flag_finished_contractdetails", True)

    ## portfolio

    def init_portfolio_data(self):
        if "data_portfoliodata" not in dir(self):
            setattr(self, "data_portfoliodata", [])
        if "data_accountvalue" not in dir(self):
            setattr(self, "data_accountvalue", [])


        setattr(self, "flag_finished_portfolio", False)


    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        """
        Add a row to the portfolio structure
        """

        portfolio_structure=self.data_portfoliodata

        portfolio_structure.append((contract.symbol, contract.expiry, position, marketPrice, marketValue, averageCost,
                                    unrealizedPNL, realizedPNL, accountName, contract.currency))

    ## account value

    def updateAccountValue(self, key, value, currency, accountName):
        """
        Populates account value dictionary
        """
        account_value=self.data_accountvalue

        account_value.append((key, value, currency, accountName))


    def accountDownloadEnd(self, accountName):
        """
        Finished can look at portfolio_structure and account_value
        """
        setattr(self, "flag_finished_portfolio", True)

class IBclient(object):
    """
    Client object

    Used to interface with TWS for outside world, does all handling of streaming waiting etc

    Create like this
    callback = IBWrapper()
    client=IBclient(callback)

    We then use various methods to get prices etc

    """
    def __init__(self, callback, accountid="DU15237"):
        """
        Create like this
        callback = IBWrapper()
        client=IBclient(callback)
        """

        tws = EPosixClientSocket(callback)
        (host, port, clientid)=return_IB_connection_info()
        tws.eConnect(host, port, clientid)

        self.tws=tws
        self.accountid=accountid
        self.cb=callback

    def get_contract_details(self, ibcontract, reqId=MEANINGLESS_NUMBER):

        """
        Returns a dictionary of contract_details


        """

        self.cb.init_contractdetails(reqId)
        self.cb.init_error()

        self.tws.reqContractDetails(
            reqId,                                         # reqId,
            ibcontract,                                   # contract,
        )


        finished=False
        iserror=False

        start_time=time.time()
        while not finished and not iserror:
            finished=self.cb.flag_finished_contractdetails
            iserror=self.cb.flag_iserror

            if (time.time() - start_time) > MAX_WAIT_SECONDS:
                finished=True
                iserror=True
            pass

        contract_details=self.cb.data_contractdetails[reqId]
        if iserror or contract_details=={}:
            print self.cb.error_msg
            print "Problem getting details"
            return None

        return contract_details



    def get_next_brokerorderid(self):
        """
        Get the next brokerorderid
        """


        self.cb.init_error()
        self.cb.init_nextvalidid()


        start_time=time.time()

        ## Note for more than one ID change '1'
        self.tws.reqIds(1)

        finished=False
        iserror=False

        while not finished and not iserror:
            brokerorderid=self.cb.data_brokerorderid
            finished=brokerorderid is not None
            iserror=self.cb.flag_iserror
            if (time.time() - start_time) > MAX_WAIT_SECONDS:
                finished=True
            pass


        if brokerorderid is None or iserror:
            print self.cb.error_msg
            print "Problem getting next broker orderid"
            return None

        return brokerorderid


    def place_new_IB_order(self, ibcontract, trade, lmtPrice, orderType, orderid=None):
        """
        Places an order

        Returns brokerorderid

        raises exception if fails
        """
        iborder = IBOrder()
        iborder.action = bs_resolve(trade)
        iborder.lmtPrice = lmtPrice
        iborder.orderType = orderType
        iborder.totalQuantity = abs(trade)
        iborder.tif='DAY'
        iborder.transmit=True

        ## We can eithier supply our own ID or ask IB to give us the next valid one
        if orderid is None:
            print "Getting orderid from IB"
            orderid=self.get_next_brokerorderid()

        print "Using order id of %d" % orderid

         # Place the order
        self.tws.placeOrder(
                orderid,                                    # orderId,
                ibcontract,                                   # contract,
                iborder                                       # order
            )

        return orderid

    def any_open_orders(self):
        """
        Simple wrapper to tell us if we have any open orders
        """

        return len(self.get_open_orders())>0

    def get_open_orders(self):
        """
        Returns a list of any open orders
        """


        self.cb.init_openorders()
        self.cb.init_error()

        start_time=time.time()
        self.tws.reqAllOpenOrders()
        iserror=False
        finished=False

        while not finished and not iserror:
            finished=self.cb.flag_order_structure_finished
            iserror=self.cb.flag_iserror
            if (time.time() - start_time) > MAX_WAIT_SECONDS:
                ## You should have thought that IB would teldl you we had finished
                finished=True
            pass

        order_structure=self.cb.data_order_structure
        if iserror:
            print self.cb.error_msg
            print "Problem getting open orders"

        return order_structure



    def get_executions(self, reqId=MEANINGLESS_NUMBER):
        """
        Returns a list of all executions done today
        """
        assert type(reqId) is int
        if reqId==FILL_CODE:
            raise Exception("Can't call get_executions with a reqId of %d as this is reserved for fills %d" % reqId)

        self.cb.init_fill_data()
        self.cb.init_error()

        ## We can change ExecutionFilter to subset different orders

        self.tws.reqExecutions(reqId, ExecutionFilter())

        iserror=False
        finished=False

        start_time=time.time()

        while not finished and not iserror:
            finished=self.cb.flag_fill_data_finished
            iserror=self.cb.flag_iserror
            if (time.time() - start_time) > MAX_WAIT_SECONDS:
                finished=True
            pass

        if iserror:
            print self.cb.error_msg
            print "Problem getting executions"

        execlist=self.cb.data_fill_data[reqId]

        return execlist

    def get_IB_account_data(self):

        self.cb.init_portfolio_data()
        self.cb.init_error()

        ## Turn on the streaming of accounting information
        self.tws.reqAccountUpdates(True, self.accountid)

        start_time=time.time()
        finished=False
        iserror=False

        while not finished and not iserror:
            finished=self.cb.flag_finished_portfolio
            iserror=self.cb.flag_iserror

            if (time.time() - start_time) > MAX_WAIT_SECONDS:
                finished=True
                print "Didn't get an end for account update, might be missing stuff"
            pass

        ## Turn off the streaming
        ## Note portfolio_structure will also be updated
        self.tws.reqAccountUpdates(False, self.accountid)

        portfolio_data=self.cb.data_portfoliodata
        account_value=self.cb.data_accountvalue

        if iserror:
            print self.cb.error_msg
            print "Problem getting details"
            return None

        return (account_value, portfolio_data)

    def get_position_by_stock(self, position_ib, stockcode, asset, p):
        """
        获取特定股票的比重，量，和组合剩余仓位比重
        :param position_ib: 数据库暂存仓位信息
        :param stockcode: 股票代码
        :param asset:资产数
        :param p: 组合代码
        :return:股票的比重，量，组合剩余仓位比重
        """
        rest = 0  # 以防p不在列，但实际不可能
        if p in position_ib.position["portfolio"]:
            rest = position_ib.position["portfolio"][p]["percent_fixed"] - position_ib.position["portfolio"][p]["percent_now"]
            if stockcode in position_ib.position["portfolio"][p]["stock"].keys():
                return position_ib.position["portfolio"][p]["stock"][stockcode]["percent"], \
                       position_ib.position["portfolio"][p]["stock"][stockcode]["volume"], \
                       rest
        return 0, 0, rest  # 新加入的股票无量和比重，但仍然要返回组合剩余仓位

    def update_portfolio(self, position_ib, position, asset, portfolio_list):
        """
        更新仓位数据库信息
        :param position_ib:数据库暂存仓位信息
        :param position:IB真实仓位
        :param asset:总资产
        :param portfolio_list:初始组合列表
        :return:
        """
        # 组合原先全部空，初始化组合信息
        if "portfolio" not in position_ib.position.keys():
            position_ib.position["portfolio"] = {}
            for p in portfolio_list.keys():
                position_ib.position["portfolio"][p] = {"stock": {}, "percent_now": 0, "percent_fixed": 0}
        # 对于新加的组合初始化
        for p in portfolio_list.keys():
            if p not in position_ib.position["portfolio"].keys():
                position_ib.position["portfolio"][p] = {"stock": {}, "percent_now": 0, "percent_fixed": 0}
        # 更新时间，资产
        position_ib.position["asset"] = asset #更新总资产
        position_ib.position["date"] = datetime.datetime.now() #更新操作时间
        # 转化股价成字典
        position_dict = {}
        for e in position:
            code = e[0]
            price = round(e[3], 2)
            position_dict[code] = price

        # 逐个组合更新价格
        for p in position_ib.position["portfolio"]:
            for code in position_ib.position["portfolio"][p]["stock"].keys():
                if position_ib.position["portfolio"][p]["stock"][code]["volume"] == 0:
                    position_ib.position["portfolio"][p]["stock"].pop(code)
                else:
                    position_ib.position["portfolio"][p]["stock"][code]["price"] = position_dict[code] if code in position_dict else 0

        # 逐个组合更新比例
        need_delete = []
        for p in position_ib.position["portfolio"]:
            if p in portfolio_list.keys(): #没有删除的组合
                sum_percent = 0
                for code in position_ib.position["portfolio"][p]["stock"]:
                    price = position_ib.position["portfolio"][p]["stock"][code]["price"]
                    volume = position_ib.position["portfolio"][p]["stock"][code]["volume"]
                    position_ib.position["portfolio"][p]["stock"][code]["percent"] = price * volume / asset
                    sum_percent += position_ib.position["portfolio"][p]["stock"][code]["percent"]
                position_ib.position["portfolio"][p]["percent_now"] = sum_percent
                position_ib.position["portfolio"][p]["percent_fixed"] = portfolio_list[p]["percent"]
            else: #没有的组合进行数据库删除
                need_delete.append(p)

        if len(need_delete):
            for p in need_delete:
                position_ib.position["portfolio"].pop(p)

    def update_operation(self, position_ib, p, code, volume):
        """
        根据下单，更新仓位数据库信息
        :param position_ib:数据库仓位数据信息
        :param p:组合名
        :param code:股票代码
        :param volume:交易量
        :return:
        """
        # 股票若在则交易量相加， 不再则直接使用该交易量，并初始化其仓位信息
        if code in position_ib.position["portfolio"][p]["stock"].keys():
            volume_before = position_ib.position["portfolio"][p]["stock"][code]["volume"]
            volume_now = volume_before + volume
        else:
            volume_now = volume
            position_ib.position["portfolio"][p]["stock"][code] = {"volume": 0, "price": 0, "percent": 0}

        position_ib.position["portfolio"][p]["stock"][code]["volume"] = volume_now
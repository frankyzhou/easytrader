# -*- coding: utf-8 -*
import easytrader
import sys
import traceback
from cn_trade import *
import copy
__author__ = 'frankyzhou'
# declare basic vars
TEST_STATE = False
DB_NAME = "Xueqiu"
OPEA_COLL = "xq_operation"
SP_COLL = "shipan"
SLIP_POINT = 0


def judge_sp_trade(trade):
    if trade["target_weight"] == 0 or trade["target_weight"] - trade["prev_weight"] > 9.0:
        return True
    else:
        return False


class XqTrade(CNTrade):
    def __init__(self, p, is_first):
        # 固定部分
        super(XqTrade, self).__init__(p=p)
        self.xq = easytrader.use('xq')
        self.xq.prepare('config/xq'+p+'.json')
        self.xq.set_attr("portfolio_code", "ZH776826")
        self.logger = get_logger(OPEA_COLL, is_first=is_first)
        self.db = MongoDB(DB_NAME)

        # 每日更新 都在cn_trade里
        # self.last_trade_time = get_trade_date_series("CN")
        # self.trade_time = get_date_now("CN")
        # self.all_stocks_data = None
        # self.is_update_stocks = False
        # self.is_update_stocks, self.all_stocks_data = update_stocks_data(False, self.all_stocks_data)

    def judge_sp_trades(self, trade):
        trade_list = []
        trade_new = copy.deepcopy(trade)
        trade_cur = self.db.exist_stock(SP_COLL, trade)
        target_max = 0
        target_min = 0
        prev_max = 0
        prev_min = 0
        oper = ""
        for trade_tmp in trade_cur:
            if is_trade_time(test=TEST_STATE, last_trade_time=self.last_trade_time, test_time=trade_tmp["report_time"]):
                target_max = max(target_max, trade_tmp["target_weight"])
                target_min = min(target_min, trade_tmp["target_weight"])
                prev_max = max(prev_max, trade_tmp["prev_weight"])
                prev_min = min(prev_min, trade_tmp["prev_weight"])
                oper = trade["entrust_bs"]
                trade_list.append(trade_tmp)
        if oper == "买入":
            trade_new["prev_weight"] = prev_min
            trade_new["target_weight"] = target_max
        else:
            trade_new["prev_weight"] = prev_max
            trade_new["target_weight"] = target_min
        trade_new["report_time"] = trade_list[0]["report_time"]  # 第一个不会变，避免出现最后一次交易后，之前结果会重复交易
        return trade_new

    def trade_by_entrust(self, entrust, k, factor, percent):
        """
        解析每个组合的交易记录
        :param entrust:
        :param k:
        :param factor:
        :param percent:
        :return:
        """
        for trade in entrust:
            # only if entrust is today or not finished by no trade time
            trade["portfolio"] = k
            if not TEST_STATE:
                if is_trade_time(test=TEST_STATE, last_trade_time=self.last_trade_time, test_time=trade["report_time"]):
                    if self.db.exist_trade(OPEA_COLL, trade):  # 使用exist_trade防止实盘出现权重飘移
                        continue  # 操作存在，但可能出现交叉成交，只跳过, 头做一次针对第一次就正确，也包含虚拟组合
                    if k[:2] == "SP":  # 实盘特别处理
                        if not self.db.exist_trade(SP_COLL, trade):
                            self.db.insert_doc(SP_COLL, trade)
                        else:
                            continue  # 若已插入，证明已经处理过，无需等到下面

                        if not judge_sp_trade(trade):
                            trade = self.judge_sp_trades(trade)
                            if not judge_sp_trade(trade):
                                continue  # 合并操作仍然不符合要求

                        if trade["target_weight"] > 0:  # 是实盘操作，将买入权重修复
                            trade["prev_weight"] = 0
                            trade["target_weight"] = 10

                        if self.db.exist_trade(OPEA_COLL, trade):
                            continue  # 操作存在，但可能出现交叉成交，只跳过，后面做一次，针对多次作对
                else:
                    break  # 超时跳出大循环
            else:
                if self.db.get_doc(OPEA_COLL, trade):
                    continue

            record_msg(logger=self.logger, msg= k + " updates new operation!" +
                                               " @ " + trade["report_time"])
            code = str(trade["stock_code"][2:])
            target_percent = 0.0 if trade["target_weight"] < 2.0 and trade["prev_weight"] > trade["target_weight"] \
                else trade["target_weight"] * percent /100
            # 防止进入仓位1%，认为是卖出
            """
            before_percent has two version.
            1.the position is caled by yjb;
            2,the position is caled by xq;
            已经有比例，故其他需要对应
            """
            before_percent_yjb, enable_amount, asset, rest_money = parse_digit(self.client.exec_order("get_position "+ code))
            before_percent_xq = trade["prev_weight"] * percent / 100 if trade["prev_weight"] > 2.0 else 0.0
            dif, price, amount = self.get_trade_detail(target_percent, before_percent_xq,
                                                       before_percent_yjb, asset, factor, code, trade, rest_money)

            result = self.trade(dif, code, price, amount, enable_amount)
            record_msg(logger=self.logger,
                       msg=self.portfolio_list[k]["name"] + ": " + result + " 花" + cal_time_cost(trade["report_time"]) + "s")
            self.db.insert_doc(OPEA_COLL, trade)

    def get_trade_detail(self, target_percent, before_percent_xq, before_percent_yjb, asset, factor, code, trade, rest_money):
        """
        得到交易变化，价格，数量
        :param target_percent:
        :param before_percent_xq:
        :param before_percent_yjb:
        :param asset:
        :param factor:
        :param code:
        :param trade:
        :return:
        """
        dif_xq = target_percent - before_percent_xq
        dif_yjb = target_percent - before_percent_yjb

        dif = dif_xq if target_percent != 0 else -2
        '''
        除非target为0，不然全部采用雪球，证券不够可由可用额度确保
        '''
        # if dif_xq > 0:
        #     dif = dif_xq
        # elif target_percent == 0:
        #     dif = -2
        # else:
        #     dif = min(max(dif_xq, dif_yjb), 0)

        '''如果dif_xq为正，那幅度选择dif_xq，避免过高成本建仓；
        当dif_xq为负，
        若dif_yjb为正，说明目前账户持仓比雪球目标还低，出于风险考虑不加仓，dif取0；
        若dif_yib为负，择最大的变化，避免持有证券数量不够
        问题，做高抛低吸的操作，反应可能由于仓位比较小，导致无法识别
        '''
        # code = "600037"
        # dif = -0.04
        # price = 14.74

        volume = dif*asset if dif < 0 else min(dif*asset, rest_money)  # 当买入时，检查可用资金是否够
        factor = abs(factor) if dif > 0.0 else -abs(factor)
        price = get_price_by_factor(self.all_stocks_data, code, trade["business_price"], (1+factor))
        amount = abs(volume) * (1+SLIP_POINT) // price // 100 * 100

        return dif, price, amount

    def trade_entrust(self):
        for k in self.portfolio_list.keys():
            try:
                self.xq.set_attr("portfolio_code", k)
                time.sleep(10)
                entrust = self.xq.get_entrust()
                factor = self.portfolio_list[k]["factor"]
                percent = self.portfolio_list[k]["percent"]
                self.trade_by_entrust(entrust, k, factor, percent)

            except Exception, e:
                msg = "xq:" + str(e.message)
                # self.xq.driver.close()
                traceback.print_exc()
                record_msg(logger=self.logger, msg=msg, email=self.email)
                time.sleep(60)
                try:
                    self.xq.autologin()
                except:
                    print "login fail..."
                    return -1
                # return -1

    def main(self):
        while 1:
            self.update_para(TEST_STATE)
            while is_trade_time(TEST_STATE, self.last_trade_time):
                self.is_update_stocks, self.all_stocks_data = update_stocks_data(self.is_update_stocks,
                                                                                 self.all_stocks_data)
                if self.trade_entrust():
                    return -1  # 程序出错，跳出重启


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: python xq_trade.py profilio_num[1,2,....n]"
        exit(-1)
    is_first = True
    while 1:
        ins = XqTrade(sys.argv[1], is_first)
        ins.main()
        ins.xq.driver.close()
        time.sleep(10)
        is_first = False

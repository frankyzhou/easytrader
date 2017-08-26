import easytrader
from trade.util import *
import datetime as dt
import tushare as ts
import pandas as pd

DB_NAME = 'Xueqiu'
p_dict= {
    # 'ZH005825':'wuxinhongqi',
    'ZH003851':'tiequan',
    'ZH009023':'dahuasheng',
    'ZH070770':'yaobunengting',
    'ZH000770':'mario',
    'ZH016097':'jinyuren'
}

db = MongoDB(DB_NAME)
# xq = easytrader.use('xq')
# xq.prepare('config/xq1.json')
# for i in p_dict.keys():
#     print i, p_dict[i]
#     xq.set_attr("portfolio_code", i)
#     OPEA_COLL = p_dict[i]
#     entrust = xq.get_entrust(is_all=True)
#     for trade in entrust:
#         if not db.get_doc(OPEA_COLL, trade):
#             db.insert_doc(OPEA_COLL, trade)

def analyse_trade(coll):
    trade_hist = {}
    for i in db.db[coll].find():
        stock = i['stock_code']

        if stock in trade_hist:
            trade_hist[stock].append(i)
        else:
            trade_hist[stock] = []

    for s in trade_hist.keys():
        trade_lst = trade_hist[s]
        time_early = dt.datetime.now()
        time_late = dt.datetime.now() - dt.timedelta(days=10000)
        position_lst = []
        trade_df = pd.DataFrame(trade_lst)
        if len(trade_df) > 0:
            del trade_df['_id']
            trade_df = trade_df[['report_time', 'stock_code', 'stock_name', 'target_weight', 'prev_weight', 'comment', 'business_price', 'entrust_bs']]
        # for l in trade_lst:
        #     prev_weight = l['prev_weight']
        #     targe_weight = l['target_weight']
        #     report_time = dt.datetime.strptime(l['report_time'],'%Y-%m-%d %H:%M:%S')
        #     time_early = report_time if report_time < time_early else time_early
        #     time_late = report_time if report_time > time_late else time_late
        #     reason = l['comment']
        # df = ts.get_h_data(s[2:], (time_early-dt.timedelta(days=5)).strftime("%Y-%m-%d"), (time_late + dt.timedelta(days=5)).strftime("%Y-%m-%d"))
            trade_df.to_csv(coll+"/"+s+".csv", encoding='utf-8')
        print 1
    print 1

analyse_trade('jacky_he')
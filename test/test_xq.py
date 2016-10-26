import easytrader
xq = easytrader.use('xq')
xq.prepare('../trade/config/xq.json')
xq.set_attr("portfolio_code", "ZH958096")
# position = xq.get_position()
# for s in position:
#     code = s["stock_code"]
#     xq.adjust_weight(000001)
xq.adjust_weight('600781', 10)
# xq.buy('600781', amount=100, price=10)
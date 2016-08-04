import tushare as ts

def update_stocks_data(state, all_stocks):
    if not state:
        try:
            all_stocks = ts.get_today_all()
            state = True
        except Exception, e:
            print e
            all_stocks = None
            state = False
    return state, all_stocks

all_data = None
state = False
state, all_data = update_stocks_data(state, all_data)
print state
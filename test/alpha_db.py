
from trade.util import *
import easytrader

DB_NAME = "seek_alpha"
COLLECTION = "xueqiu"
db = MongoDB(DB_NAME)
path = os.getcwd()
result_file = open("Result.csv", "w")
count = 0


def parse(count, path):
    for root, dirs, files in os.walk(path + "\logs\seek_alpha"):
        for name in files:
            log_name = os.path.join(root, name)
            log = open(log_name)
            for line in log:
                if count % 10000 == 0:
                    print str(count) + " records has been cal."
                report = {}
                tokens = line.split()
                if len(tokens) == 14:
                    time = tokens[0]
                    code = tokens[3].split(":")[0]
                    alpha = get_four_five(tokens[4].split(":")[1], 5)
                    beta = get_four_five(tokens[5].split(":")[1], 5)
                    sharp = get_four_five(tokens[6].split(":")[1], 5)
                    drawdown = get_four_five(tokens[7].split(":")[1], 5)
                    sortino = get_four_five(tokens[8].split(":")[1], 5)
                    trade_times = int(tokens[9].split(":")[1])
                    market = tokens[10]
                    start_time = tokens[11]
                    fans = int(tokens[12])
                    status = 1 if tokens[13] == "run" else 0

                    report["time"] = time
                    report["code"] = code
                    report["alpha"] = alpha
                    report["beta"] = beta
                    report["sharp"] = sharp
                    report["drawdown"] = drawdown
                    report["sortino"] = sortino
                    report["trade_times"] = trade_times
                    report["market"] = market
                    report["start_time"] = start_time
                    report["fans"] = fans
                    report["status"] = status

                    db.insert_doc(COLLECTION, report)
                    count += 1

keys = ["code", "grade", "alpha", "beta", "sharp", "drawdown", "sortino", "trade_times", "market", "start_time", "fans", "time"]
factor_dict = []
factor_id_set = set()

now = datetime.datetime.now()
# parse(path=path, count=count)
for i in db.db[COLLECTION].find():
    start_time = datetime.datetime.strptime(i["start_time"], "%Y-%M-%d")
    delta = now - start_time
    del i["_id"]
    if i["market"] == "SH" and i["fans"] > 10 and i["status"] == 1 and\
            int(i["trade_times"]) < 300 and i["drawdown"] < 0.7 and \
            delta > datetime.timedelta(days=365):
        grade = i["alpha"] + i["sharp"]
        if abs(grade) < 50 and i["code"] not in factor_id_set:
            i["grade"] = grade
            factor_dict.append(i)
            factor_id_set.add(i["code"])

if len(factor_dict) > 0:
    # sorted_list = sorted(factor_dict.iteritems(), key=lambda d: d[1], reverse = True)
    for i in factor_dict:
        str_out = ""
        # i["start_time"] = i["start_time"].strftime("%Y-%M-%d")
        for key in keys:
            str_out = str_out + str(i[key]) + "\t"
        result_file.write(str_out + "\n")
result_file.close()

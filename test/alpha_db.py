
from trade.util import *
import easytrader

DB_NAME = "seek_alpha"
COLLECTION = "xueqiu"
db = MongoDB(DB_NAME)
path = os.getcwd()
result_file = open("Result.csv", "w")
# for root, dirs, files in os.walk(path + "\logs\seek_alpha"):
#     for name in files:
#         log_name = os.path.join(root, name)
#         log = open(log_name)
#         for line in log:
#             report = {}
#             tokens = line.split()
#             if len(tokens) == 7:
#                 time = tokens[0]
#                 code = tokens[3].split(":")[0]
#                 alpha = get_four_five(tokens[4].split(":")[1], 5)
#                 beta = get_four_five(tokens[5].split(":")[1], 5)
#                 sharp = get_four_five(tokens[6].split(":")[1], 5)
#                 report["time"] = time
#                 report["code"] = code
#                 report["alpha"] = alpha
#                 report["beta"] = beta
#                 report["sharp"] = sharp
#                 db.insert_doc(COLLECTION, report)
#         print 1
factor_dict = {}
for i in db.db[COLLECTION].find():
    grade = i["alpha"] + i["sharp"]
    factor_dict[i["code"]] = grade if abs(grade) < 100 else 0
    # if i["alpha"] > 1 and i["sharp"] > 1:
    #     result_file.write(i["code"] + "\t" + str(i["alpha"]) + "\t" + str(i["sharp"]) + "\n")
sorted_list = sorted(factor_dict.iteritems(), key=lambda d: d[1], reverse = True)[:100]
for i in sorted_list:
     result_file.write(str(i) + "\n")
result_file.close()

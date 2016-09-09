import os
import os.path
from decimal import Decimal
from trade.util import get_four_five

# def get_four_five(num, pre):
#     p = '{:.' + str(pre) + 'f}'
#     return float(p.format(Decimal(num)))

for root, dirs, files in os.walk("C:\Users\Administrator\develop\easytrader\logs\seek_alpha"):
    for name in files:
        log_name = os.path.join(root, name)
        log = open(log_name)
        for line in log:
            tokens = line.split()
            time = tokens[0]
            code = tokens[3].split(":")[0]
            alpha = get_four_five(tokens[4].split(":")[1], 5)
            beta = get_four_five(tokens[5].split(":")[1], 5)
            sharp = get_four_five(tokens[6].split(":")[1], 5)
        print 1
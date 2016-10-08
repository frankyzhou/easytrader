import bcolz
import datetime
y = bcolz.open("C:\\Users\\frankyzhou\\.rqalpha\\yield_curve.bcolz")
start_date = datetime.datetime.strptime("2016-01-01", "%Y-%M-%d")
d = start_date.year * 10000 + start_date.month * 100 + start_date.day
f = y.fetchwhere('date<={}'.format(d))
print 1
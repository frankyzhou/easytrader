import easytrader

target = 'rq'  # ricequant
follower = easytrader.follower(target)
follower.login(user='zljszlj@163.com', password='zljabhbhwan37')
xq_user = easytrader.use('xq')
xq_user.prepare('config/xq.json')

follower.follow(xq_user, 831953)
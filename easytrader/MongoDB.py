# -*- coding: utf-8 -*-#
#__author__ = 'frankyzhou'

import os
from easytrader import helpers
import pymongo
import datetime


class MongoDB:
    def __init__(self, db):
        """载入MongoDB数据库的配置"""
        try:
            config_path = os.path.dirname(__file__) + '/easytrader/config/db.json'
            config = helpers.file2dict(config_path)
            host = config['mongoHost']
            port = config['mongoPort']
        except:
            host = 'localhost'
            port = 27017

        self.dbClient = pymongo.MongoClient(host, port)
        self.db = self.dbClient[db]

    def insert_doc(self, coll, info):
        # 插入一个document
        colls = self.db[coll]
        colls.insert(info)

    def get_doc(self, coll, info):
        # 有就返回一个，没有就返回None
        # print colls.find_one()  # 返回第一条记录
        colls = self.db[coll]
        return colls.find_one(info)
        # print coll.find_one({"name": "none"})

    def get_one_by_id(db):
        # 通过objectid来查找一个doc
        coll = db['informations']
        obj = coll.find_one()
        obj_id = obj["_id"]
        # print "_id 为ObjectId类型，obj_id:" + str(obj_id)

        # print coll.find_one({"_id": obj_id})
        # 需要注意这里的obj_id是一个对象，不是一个str，使用str类型作为_id的值无法找到记录
        # print "_id 为str类型 "
        # print coll.find_one({"_id": str(obj_id)})
        # 可以通过ObjectId方法把str转成ObjectId类型
        from bson.objectid import ObjectId

        # print "_id 转换成ObjectId类型"
        # print coll.find_one({"_id": ObjectId(str(obj_id))})

    def clear_all_datas(self, coll):
        colls = self.db[coll]
        colls.drop()

    def exist_trade(self, coll, trade):
        colls = self.db[coll]
        return colls.find_one({"report_time": str(trade["report_time"]), "portfolio": str(trade["portfolio"]), \
                      "stock_name": str(trade["stock_name"])})

    def exist_stock(self, coll, trade):
        colls = self.db[coll]
        return colls.find({"portfolio": str(trade["portfolio"]), "stock_name": str(trade["stock_name"])})


# if __name__ == '__main__':
#     db = MongoDB("Positions", "IB")
#     # get_doc(db, "example", "sdfa")
#     post =  {
#     "ZH776826" : {
#         "RIO" : {"price":28.34, "volume":2453},
#         "DUST" : {"price":11.02, "volume":349},
#         "DGAZ" : {"price":12.18, "volume":44},
#         "DWTI" : {"price":74.84, "volume":105},
#     },
#     "date": datetime.datetime.now(),
#     "ZH796463" : {
#         "LGCY" : {"price":2.32, "volume":9800},
#     }
#     }
#
#     # # 插入记录
#     db.insert_doc(post)
#     # # 条件查询
#     # # 查询表中所有的数据
#     for iii in db.coll.find():
#         print iii
#     # print my_collection.count()
#     # my_collection.update({"author": "Mike"},
#     #                      {"author": "quyang", "text": "My first blog post!", "tags": ["mongodb", "python", "pymongo"],
#     #                       "date": datetime.datetime.utcnow()})
#     # for jjj in my_collection.find():
#     #     print jjj
#     # get_doc(db)
#     # get_one_by_id(db)
#     # get_many_docs(db)
#     # clear_all_datas(db)

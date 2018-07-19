# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class DoubanPipeline(object):
    def process_item(self, item, spider):
        return item


# https://docs.scrapy.org/en/latest/topics/item-pipeline.html#write-items-to-mongodb
class MongoPipeline(object):
    """
    将专辑信息写入Mongo
    """

    def __init__(self, host, db_name):
        self.host = host
        self.db_name = db_name

    @classmethod
    def from_crawler(cls, crawler):
        # 这里的配置由 settings.py 文件提供
        # 构造(初始化)方法中的值由这里注入
        return cls(
            host=crawler.settings.get('MONGO_HOST'),
            db_name=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = MongoClient(host=self.host)
        self.db = self.client.get_database(self.db_name)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if 'book_number' in item and 'book_name' in item:
            self.process_book_item(item, spider)
        elif 'book_number' in item and 'nickname' in item:
            pass
        else:
            # TODO 电影、音乐暂略
            pass

        return item

    def process_book_item(self, item, spider):
        self.db.get_collection('books').insert_one(dict(item))

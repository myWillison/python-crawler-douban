# -*- coding: utf-8 -*-
from scrapy import Spider


class BookSpider(Spider):
    name = 'book_spider'

    def start_requests(self):
        pass

    def parse(self, response):
        pass

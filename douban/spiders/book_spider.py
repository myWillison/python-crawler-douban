# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider


class BookSpider(Spider):
    name = 'book_spider'

    allowed_domains = ['book.douban.com']

    def start_requests(self):
        """
        Top250列表页非常规律，每页25条记录，所以后一页查询参数为当前页查询参数+25
        :return:
        """
        for i in range(0, 250, 25):
            yield scrapy.Request('https://book.douban.com/top250?start={}'.format(i), self.parse)

    def parse(self, response):
        """
        解析书籍列表页
        :param response:
        :return:
        """
        yield from [response.follow(url, self.parse_subject) for url in
                    response.xpath('//a[@class="nbg"]/@href').extract()]

        pass

    def parse_subject(self, response):
        """
        解析书籍详情页
        :param response:
        :return:
        """
        # TODO 提取书籍信息


        # TODO 组装书评页请求

        pass

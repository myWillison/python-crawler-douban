# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider

from douban.items import BookItem, BookCommentItem


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

        # # 调试阶段，只用一个URL
        # yield scrapy.Request('https://book.douban.com/top250?start={}'.format(0), self.parse)

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
        # 提取书籍信息
        # 编号
        book_number = int(response.url.split('/')[-2])
        # 书名
        book_name = response.xpath('//*[@id="wrapper"]/h1/span/text()').extract_first()
        # 封面
        cover = response.xpath('//*[@id="mainpic"]/a/img//@src').extract_first()

        # 评分，转换为浮点数
        score = response.xpath('//strong[contains(@class, "rating_num")]/text()').extract_first()
        score = float(score.strip())

        # 评星比例列表[5 ~ 1]
        stars = response.xpath('//div[contains(@class,"rating_wrap")]/span[@class="rating_per"]/text()').re(
            r'(\d+\.?\d*)')
        stars = [float(star) for star in stars]

        # 标签列表
        tags = response.xpath('//div[@id="db-tags-section"]//a/text()').extract()

        # 图书馆列表，去掉后面的括号
        libraries = response.xpath('//div[@id="borrowinfo"]//a/text()').extract()
        libraries = [library.split('(')[0] for library in libraries]

        # 最后处理书其它信息(内容放在一块，不好区分，采用将其一次提取出来，遍历处理)
        # 以下面方式找到全部信息，然后再遍历处理，注意作者可能同时有多个
        # `descendant` 表示取当前节点的所有后代节点(子代、孙代等)
        # >> > response.xpath('//div[@id="info"]/descendant::text()').re(r'\S+')
        # ['作者:', '[法]', '圣埃克苏佩里', '/', '[法]', '安东尼·德·圣-埃克苏佩里',
        # '出版社:', '人民文学出版社', '原作名:', 'Le', 'Petit', 'Prince',
        # '译者', ':', '马振聘', '出版年:', '2003-8', '页数:', '97', '定价:', '22.00元',
        # '装帧:', '平装', 'ISBN:', '9787020042494']
        infos = response.xpath('//div[@id="info"]/descendant::text()').re(r'\S+')
        # 记录处理后的结果
        data = {
            'book_number': book_number,
            'book_name': book_name,
            'cover': cover,
            'score': score,
            'stars': stars,
            'tags': tags,
            'libraries': libraries,
        }

        yield self._parse_subject_content(infos, data)

        # 组装书评页请求(书评第一页，后续页面URL由书评页提供)
        comment_url = response.url + 'comments/new?p=1'
        yield response.follow(comment_url, self.parse_comment)

    def _parse_subject_content(self, infos, data):
        # 记录当前迭代的位置(对应data的键)
        curr = None

        # 只是为了减少重复代码

        # 定义一个元组列表，声明了关键字与变量名之间映射关系
        metas = [
            ('作者', 'authors'),
            ('出版社', 'press'),
            ('原作名', 'origin_name'),
            ('出版年', 'publish_year'),
            ('页数', 'pages'),
            ('定价', 'price'),
            ('装帧', 'binding'),
            ('ISBN', 'isbn'),
            ('丛书', 'series'),
            ('出品方', 'publisher'),
            ('译者', 'translator'),
            ('副标题', 'book_subtitle'),
        ]

        # 组装数据
        for info in infos:
            for _key, _var in metas:
                # 由于某些时候':'会跟关键词分开，所以这里只匹配开始
                if info.startswith(_key):
                    curr = _var
                    data[curr] = []
                    break
            else:
                data[curr].append(info.strip())

        # 重组数据
        # 数据组装好后，进行格式转换、内容拼接处理
        if 'authors' in data:
            # 先将列表拼接成字符串，再按/拆分，目的是为了把国籍跟名字拼接在一起，多个作者之前以/分隔
            # https://book.douban.com/subject/1084336/
            data['authors'] = ''.join(data['authors']).split('/')

        def j(var_name):
            if var_name not in data:
                return
            # 如果列表第一个元素包含':'，可能是标题里的(部分网页存在:和标题分开的情况)
            # https://book.douban.com/subject/1084336/ 译者部分(但其它页并不存在这样的问题)
            if ':' in data[var_name]:
                del data[var_name][0]
            data[var_name] = ' '.join(data[var_name])

        # 其它字段都是单个值，所以简单拼接即可
        [j(_var) for _, _var in metas if _var != 'authors']

        # 去掉价格后面的元
        if 'price' in data:
            if '元' in data['price']:
                data['price'] = data['price'].split('元')[0]
            data['price'] = float(data['price'])
        if 'pages' in data:
            data['pages'] = int(data['pages'])

        return BookItem(data)

    def parse_comment(self, response):

        # 提取下一页URL
        next_url = response.xpath('//ul[@class="comment-paginator"]//a[last()]/@href')
        next_url = response.urljoin(next_url)
        yield response.follow(next_url, self.parse_comment)

        # 提取书籍编号
        book_number = int(response.url.split('/')[-3])

        # 提取书评数据
        for li in response.xpath('//div[@id="comments"]/ul/li[@class="comment-item"]'):
            item = BookCommentItem()
            item['book_number'] = book_number
            # 提取头像
            item['avatar'] = li.xpath('self::*//div[@class="avatar"]/a/img/@src').extract_first()
            # 提取昵称
            item['nickname'] = li.xpath('self::*//span[@class="comment-info"]/a/text()').extract_first()
            # 提取评星(有些可能没有)
            item['star'] = li.xpath('self::*//span[@class="comment-info"]/span[contains(@class, "rating")]/@class').re(
                r'allstar(\d)0\s+rating')
            if item['star']:
                item['star'] = int(item['star'][0])
            # 提取评论日期
            item['comment_date'] = li.xpath('self::*//span[@class="comment-info"]/span[last()]/text()').extract_first()
            # 提取点赞数
            item['votes'] = li.xpath('self::*//span[@class="comment-vote"]/span/text()').extract_first()
            if item['votes']:
                item['votes'] = int(item['votes'])
            # 提取评语
            item['content'] = li.xpath('self::*//p[@class="comment-content"]/span/text()').extract_first()

            yield item

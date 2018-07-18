# python-crawler-douban

豆瓣综合掉，使用 `Python-3.7 + Scrapy-1.5` 构建。含豆瓣电影、豆瓣读书、豆瓣音乐三类Top250内容爬取及短评爬取。

## 爬虫

#### [豆瓣读书Top250](https://book.douban.com/top250)
- 书籍信息
```
# 列表页URL结构
# https://book.douban.com/top250?start=0
# https://book.douban.com/top250?start=25

# 书籍页URL结构
# https://book.douban.com/subject/1770782/

# 采集字段
封面、作者、出版社、出品方、原作者、译者、出版年、页数、定价、装帧、丛书、ISBN
综合评分、评价人数、评星比例、常用标签、在哪借这本书列表
```
- 书评数据
```
# 书评页URL结构(分热门和最新，但实际数据是一致的，只是排序方式不同)
# https://book.douban.com/subject/1770782/comments/new?p=1

# 采集字段
用户头像、用户昵称、评星、日期、有用(点赞)数、评语
```


#### 破解反爬虫
###### IP限制
> 测试时，发现：检测到有异常请求从你的 IP 发出，请 登录 使用豆瓣。所以是单个IP访问过于频繁，触发了豆瓣反爬虫机制
- 降低爬取速度
```
# 放开如下配置，降低下载速度
AUTOTHROTTLE_ENABLED = True
DOWNLOAD_DELAY = 3

# 还需要实现在一个范围内随机变化，避免固定延时容易被检查出是爬虫
# TODO 待实现 
```
- 使用高匿代理IP，这需要一个代理IP池
> 目前采用<https://github.com/jhao104/proxy_pool>提供的服务(定时从其提供的服务上更新一组代理IP，避免实时访问对其服务造成过大压力)。后期改为自建代理IP服务，代理IP数据来源于：<http://www.xicidaili.com/>
```
# TODO 待实现
```
- 随机更换UA消息头，通过自定义下载中间件实现


## 分析

#### 豆瓣读书Top250
- 评分分布，每0.1为一个统计单位
- 统计各出版社书籍数量
- 统计书籍标签分布(Top100)
- 统计书籍图书译者译书数量分布(Top10)
- 统计评论用户评书数量分布(Top100)
- 统计书籍5星数最多的Top10
- Top250范围内统计短评热词Top100，生成词云
- 可借书图书馆借书数量分布
- ... ...
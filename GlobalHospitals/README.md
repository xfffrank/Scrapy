## [全球医院症状](http://zz.qqyy.com/letter/)爬虫

### What't new?

* 在`settings.py`的`DEFAULT_REQUEST_HEADERS`中定制默认的请求头，增加`Referer`、随机用户代理和其他字段来尽量模拟浏览器的行为；
* 定制下载中间件，继承`scrapy-proxies`库的`RandomProxy`类，使得每次运行爬虫时自动更新 ip 代理池并建立随机代理机制。需在`settings.py`中设置保存代理 ip 地址的文件名`PROXY_LIST`，以及用于验证 ip 有效性的网址`PROXY_TEST_SITE`；
* 使用两个 Mongo 数据库集合，一个存放从网站爬取下来的信息，一个记录已爬取的url，用于去重，详见`pipelines.py`。


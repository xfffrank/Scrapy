# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from GlobalHospitals.build_ip_pool import GetIp
from scrapy_proxies.randomproxy import *
from scrapy.conf import settings
import logging
from requests.packages.urllib3.connectionpool import log as requests_log

class GlobalhospitalsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

requests_log.setLevel(logging.WARNING)    # 设置 requests 库的日志输出级别
class GlobalhospitalsDownloaderMiddleware(RandomProxy):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        print('Test Site: {}'.format(settings['PROXY_TEST_SITE']))
        g = GetIp()
        g.get_proxy_ip()
        g.verify_proxies()
        with open(settings['PROXY_LIST'], 'w') as f:
            for proxy in g.proxy_list:
                f.write(proxy + '\n')
        super().__init__(settings)  

    @classmethod
    def from_crawler(cls, crawler):   # 覆盖父类的方法，不能去掉
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    # 父类已定义
    # def process_exception(self, request, exception, spider):
    #     # Called when a download handler or a process_request()
    #     # (from other downloader middleware) raises an exception.

    #     # Must either:
    #     # - return None: continue processing this exception
    #     # - return a Response object: stops process_exception() chain
    #     # - return a Request object: stops process_exception() chain
    #     pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        

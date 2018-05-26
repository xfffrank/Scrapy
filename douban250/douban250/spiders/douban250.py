from douban250.items import Douban250Item
import scrapy
from scrapy import Request

class DoubanMovie250Spider(scrapy.Spider):
    name = 'douban_movie_top_250'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    def start_requests(self):
        url = 'https://movie.douban.com/top250'
        yield Request(url, headers=self.headers)

    def parse(self, response):
        item = Douban250Item()
        movies = response.xpath('//ol[@class="grid_view"]/li')

        for movie in movies:
            item['ranking'] = movie.xpath('.//div[@class="pic"]/em/text()').extract()[0]
            item['poster'] = movie.xpath('.//div[@class="pic"]/a/img/@src').extract()[0]
            item['name'] = movie.xpath('.//div[@class="pic"]/a/img/@alt').extract()[0]
            item['score'] = movie.xpath('.//div[@class="star"]/span[2]/text()').extract()[0]
            item['reviews_num'] = movie.xpath('.//div[@class="star"]/span[4]').re(r'\d+')[0]
            try:
                item['quote'] = movie.xpath('.//span[@class="inq"]/text()').extract()[0]
            except IndexError:
                item['quote'] = ''
            yield item

        next_page = response.xpath('//span[@class="next"]/a/@href').extract_first()
        if next_page:
            next_url = 'https://movie.douban.com/top250' + next_page
            yield Request(next_url, headers=self.headers)
            
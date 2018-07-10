from scrapy.http import Request
from scrapy import Spider
from bs4 import BeautifulSoup

class FoodSpider(Spider):
    
    name = 'meishi'
    allowed_domains = ['www.meishij.net']

    def start_requests(self):
        url = 'https://www.meishij.net/china-food/xiaochi/'
        yield Request(url, self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        test = soup.find('dd').get_text()
        print(test)

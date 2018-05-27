import re, scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request
from dingdian.items import DingdianItem

class Myspider(scrapy.Spider):
    name = 'dingdian'
    allowed_domains = ['x23us.com']
    start = 'https://www.x23us.com/class/'
    end = '.html'

    def start_requests(self):
        for i in range(1, 11):
            url = self.start + str(i) + '_1' + self.end
            yield Request(url, self.parse)

    def parse(self, response):
        # 获取最大页码
        max_num= BeautifulSoup(response.text, 'lxml').find('a', class_='last').get_text()
        # 获取基url
        bash_url = str(response.url[:-6])

        for num in range(1, int(max_num) + 1):
            url = bash_url + str(num) + self.end
            yield Request(url, callback=self.get_name)

    def get_name(self, response):
        trs = BeautifulSoup(response.text, 'lxml').find_all('tr', bgcolor='#FFFFFF')
        for tr in trs:
            novel_name = tr.find_all('a')[1].get_text()
            novel_intro_url = tr.find_all('a')[0]['href']
            yield Request(novel_intro_url, callback=self.get_charpter_url, meta={
                'name': novel_name,
                'url': novel_intro_url
            })

    def get_charpter_url(self, response):
        item = DingdianItem()
        bs = BeautifulSoup(response.text, 'lxml')
        item['name'] = response.meta['name']
        item['novel_url'] = response.meta['url']
        item['category'] = bs.find('table').find('a').get_text()
        item['author'] = bs.find('table').find_all('td')[1].get_text().replace('\xa0', '')
        item['novel_id'] = bs.find('p', class_='btnlinks').find('a', class_='read')['href'][-6:-1].replace('/', '')
        item['serial_status'] = bs.find('table').find('tr').find_all('td')[-1].get_text().replace('\xa0', '')
        item['serial_length'] = bs.find('table').find_all('tr')[1].find_all('td')[1].get_text().replace('\xa0', '')
        yield item

        
        
    
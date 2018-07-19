from scrapy.http import Request
from scrapy import Spider
from bs4 import BeautifulSoup
import logging
from draxe.items import DraxeItem
from draxe.pipelines import DraxePipeline as dp
import re

logger = logging.getLogger('Draxe')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('draxe.log', encoding='utf-8')  # 防止出现中文乱码
fh.setLevel(logging.INFO)  # 设置文件流的级别
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)  # 设置控制台的级别
logger.addHandler(fh)
logger.addHandler(ch)

class DraxeSpider(Spider):

    name = 'draxe'
    allowed_domains = ['draxe.com']

    def start_requests(self):
        url = 'https://draxe.com/section/food/'
        yield Request(url, self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        fd_items = soup.find_all('div', class_='post-grid-item column small-6 medium-3 end')
        for item in fd_items:
            url = item.find('a')['href']
            title = item.find('div', class_='item-content').get_text().strip()
            if dp.find_item(title):
                logger.info('%s 已经爬过了。', title)
            else:
                yield Request(url, self.get_articles, meta={'title': title})

    def get_articles(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            url = soup.find('article').find('a')['href']
        except AttributeError as e:
            logger.info(e)
        else:
            title = response.meta['title']
            yield Request(url, self.crawl_info, meta={'title': title})

    def crawl_info(self, response):
        item = DraxeItem()
        soup = BeautifulSoup(response.text, 'lxml')
        url = response.url
        fd_name = response.meta['title']
        # fd_name = re.findall(r'com/(.*?)/', url)[0]
        benefits = self.get_benefits(soup)
        recipes = self.get_recipes(soup)
        item['fd_name'] = fd_name
        item['url'] = url
        if benefits:
            item['benefits'] = benefits
        if recipes:
            item['recipes'] = recipes
        yield item
        
    def get_benefits(self, soup):
        benefits_exist = soup.find('h2')
        if 'benefits' not in benefits_exist.get_text().lower():
            logger.warning('benefits 不存在！')
            return None
        benefits = dict()
        flag = 0
        for i in benefits_exist.next_siblings:
            if i.name == 'hr':
                break
            if i.name in ['p', 'h4']:
                b_exist = i.find('b', recursive=False)
                strong_exist = i.find('strong', recursive=False)
                if b_exist and re.findall(r'\d\.', b_exist.get_text()) or strong_exist and re.findall(r'\d\.', strong_exist.get_text()):
                    temp = re.sub(r'\d\.', '', i.get_text().strip())  # 改进，已验证
                    title = temp.replace('.', '')  # key must not contain '.' [fixed]
                    benefits[title] = []
                    flag = 1
                # if b_exist and re.findall(r'\d\.', b_exist.get_text()):
                #     # title = re.sub(r'\d\.', '', b_exist.get_text().strip())
                #     title = re.sub(r'\d\.', '', i.get_text().strip())  # 改进，已验证
                #     title = title.replace('.', '')
                #     benefits[title] = []
                #     flag = 1
                # elif strong_exist and re.findall(r'\d\.', strong_exist.get_text()):
                #     # title = re.sub(r'\d\.', '', strong_exist.get_text().strip())
                #     title = re.sub(r'\d\.', '', i.get_text().strip())  # 改进，已验证
                #     title = title.replace('.', '')
                #     benefits[title] = []
                #     flag = 1
                elif i.name == 'p' and flag:
                    keywords = i.find_all('strong')
                    for k in keywords:
                        benefits[title].append(k.get_text().strip())
        return benefits
            
    def get_recipes(self, soup):
        all_ul = soup.find_all('ul')
        for ul in all_ul:
            try:
                p = ul.find_previous_sibling('p').get_text().strip()
            except:
                pass
            else:
                if 'recipe' in p and p[-1] == ':':
                    recipes = []
                    # print('----********已经找到食谱********----')
                    for li in ul.find_all('li'):
                        recipes.append(li.get_text().strip())
                    # print(recipes)
                    return recipes
        return None

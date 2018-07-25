from scrapy.http import Request
from scrapy import Spider
from bs4 import BeautifulSoup
import logging
from fh_health.pipelines import FhHealthPipeline as pipeline
import re
import requests
import random
import time

logger = logging.getLogger('fh_health')
logger.setLevel(logging.DEBUG)  # 设置 scrapy 控制台的日志输出级别
fh = logging.FileHandler('fh_health.log', encoding='utf-8', mode='w')  # w 覆盖原文件
fh.setLevel(logging.INFO)   # 设置重定向文件的日志输出级别
logger.addHandler(fh)

base_url = 'http://zzk.fh21.com.cn'

class SymptomsSpider(Spider):
    name = 'symptoms'
    allowed_domains = ['zzk.fh21.com.cn']

    def start_requests(self):
        url = 'http://zzk.fh21.com.cn/letter/symptoms.html'
        yield Request(url, self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        
        submenu = soup.find('div', class_='submenu02').find_all('a')
        for a in submenu:
            url = base_url + a['href']
            yield Request(url, self.get_detail_url)

    def get_detail_url(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        all_ul = soup.find_all('ul', class_='block08 block08c')
        for ul in all_ul:
            all_li = ul.find_all('li')
            for li in all_li:
                symptom_name = li.find('a').text.strip()
                if pipeline.find_item(symptom_name):
                    logger.info(symptom_name + " 已经爬过了！")
                else:
                    pipeline.insert({'symptom_name': symptom_name})
                    temp = li.find('a')['href']
                    summary = temp.replace('detail', 'details')
                    similar = temp.replace('detail', 'similar')
                    disease_url = base_url + temp
                    summary_url = base_url + summary
                    similar_url = base_url + similar
                    pipeline.update(symptom_name, {'url': disease_url})
                    yield Request(disease_url, self.crawl_diseases, meta={'symptom_name': symptom_name})
                    yield Request(summary_url, self.crawl_summary, meta={'symptom_name': symptom_name})
                    yield Request(similar_url, self.crawl_similar, meta={'symptom_name': symptom_name})
        next_page = soup.find(lambda tag: tag.name == 'a' and '下一页' in tag.text)
        if next_page:  # 存在下一页
            url = base_url + next_page['href']
            yield Request(url, self.get_detail_url)

    def crawl_diseases(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            dl_tags = soup.find('div', class_='z_block08_con').find_all('dl')
        except: # 可能没有疾病字段
            logger.info('[没有疾病字段]' + response.url)
        else:
            # temp = map(lambda t: t.find('a')['title'], dl_tags)
            # diseases = list(temp)
            diseases = [self.process_tag(t) for t in dl_tags]
            pipeline.update(response.meta['symptom_name'], {'possible_causes': diseases})
            
    def process_tag(self, t):
        return t.find('a')['title']

    def crawl_similar(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            li_tags = soup.find('div', class_='z_block08_con').find_all('li')
        except:  # 可能没有相似症状的字段
            logger.info('[没有相似症状]' + response.url)
        else:
            if li_tags:
                # temp = map(lambda t: t.find('a')['title'], li_tags)
                # similar_symptoms = list(temp)
                similar_symptoms = [self.process_tag(t) for t in li_tags]
                pipeline.update(response.meta['symptom_name'], {'similar_symptoms': similar_symptoms})

    def crawl_summary(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            summary = soup.find('div', class_='detail').find('div', class_='detailc').get_text().strip().replace('\n', '')
        except:
            logger.info('[没有简介]' + response.url)
        else:
            pipeline.update(response.meta['symptom_name'], {'summary': summary})
        


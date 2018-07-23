from scrapy.http import Request
from scrapy import Spider
from bs4 import BeautifulSoup
import logging
from jb9939.items import Jb9939Item
from jb9939.pipelines import Jb9939Pipeline as jp
import re
import requests
import random
import time

logger = logging.getLogger('jb9939')
logger.setLevel(logging.DEBUG)  # 设置 scrapy 控制台的日志输出级别
fh = logging.FileHandler('jb9939.log', encoding='utf-8', mode='w')
fh.setLevel(logging.INFO)   # 设置重定向文件的日志输出级别
# ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
logger.addHandler(fh)
# logger.addHandler(ch)

class DiseasesSpider(Spider):
    
    # def __init__(self):
    #     with open('proxies.txt') as f:
    #         self.proxy_list = f.readlines()
    #     self.proxy = random.choice(self.proxy_list)
    #     self.headers = {
    #         'User-Agent': ''
    #     }
    #     self.user_agent_list = [
    #         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    #         "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    #         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    #         "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    #         "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    #         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    #         "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    #         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    #         "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    #         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    #         "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    #         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    #         "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    #         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    #         "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    #         "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    #         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    #         "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    #     ]
        

    name = 'diseases'
    allowed_domains = ['jb.9939.com']

    def start_requests(self):
        url = 'http://jb.9939.com/jbzz_t1/'
        yield Request(url, self.parse)
    
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        total_page_num = soup.find('div', class_='paget paint').find_all('a')[-2].get_text().strip()
        logger.info("疾病总页数：%s", total_page_num)
        base_url = 'http://jb.9939.com/jbzz_t1/?page='
        for num in range(1, int(total_page_num) + 1):
            # logger.info('正在处理第 %s 页', num)
            url = base_url + str(num)
            yield Request(url, self.get_detail_url)

    def get_detail_url(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        docs = soup.find_all('div', class_='doc_anwer disline')
        for d in docs:
            a = d.find('h3').find('a')
            title = a['title']
            if jp.find_item(title):
                logger.debug(title + " 已经爬过了！")
            else:
                url = a['href']
                yield Request(url, self.crawl_info, meta={'title': title})  

    def crawl_info(self, response):
        item = Jb9939Item()
        disease_name = response.meta['title']
        soup = BeautifulSoup(response.text, 'lxml')
        item['disease_name'] = disease_name
        alias = self.get_alias(soup)
        reg_office = self.get_reg_office(soup)
        come_on_site = self.get_site(soup)
        infect_method = self.get_infect_method(soup)
        group = self.get_group(soup)
        therapies = self.get_therapies(soup)
        medicine = self.get_medicine(soup)
        if alias:
            item['alias'] = alias
        if reg_office:
            item['reg_office'] = reg_office
        if come_on_site:
            item['come_on_site'] = come_on_site
        if medicine:
            item['medicine'] = medicine
        item['infect_method'] = infect_method
        item['group'] = group
        item['therapies'] = therapies
        yield item
        links = soup.find_all(lambda tag: tag.name == 'a' and '[详细]' in tag.text)
        base_url = 'http://jb.9939.com'
        intro_link = links[0]['href']
        symptom_link = links[1]['href']
        clinical_link = links[2]['href']
        intro_url = base_url + intro_link
        symptom_url = base_url + symptom_link
        clinical_url = base_url + clinical_link
        yield Request(intro_url, self.get_intro, meta={'name': disease_name})
        yield Request(symptom_url, self.get_symptoms, meta={'name': disease_name})
        yield Request(clinical_url, self.get_clinical_ex, meta={'name': disease_name})
    
    def get_intro(self, response):
        item = Jb9939Item()
        soup = BeautifulSoup(response.text, 'lxml')
        h2 = soup.find(lambda tag: tag.name == 'h2' and '简介' in tag.text)
        intro = h2.find_next_sibling('p').get_text().strip()
        item['intro'] = intro
        jp.update(response.meta['name'], item)

    def get_symptoms(self, response):
        item = Jb9939Item()
        soup = BeautifulSoup(response.text, 'lxml')
        h4 = soup.find(lambda tag: tag.name == 'h4' and '典型症状' in tag.text)
        temp = h4.find_next_sibling('p').find_all('a')
        symptoms = [a.text.strip() for a in temp]
        item['symptoms'] = symptoms
        jp.update(response.meta['name'], item)

    def get_clinical_ex(self, response):
        item = Jb9939Item()
        soup = BeautifulSoup(response.text, 'lxml')
        h4 = soup.find(lambda tag: tag.name == 'h4' and '检查项目' in tag.text)
        temp = h4.find_next_sibling('p').find_all('a')
        exams = [a.text.strip() for a in temp]
        item['clinical_exams'] = exams
        jp.update(response.meta['name'], item)

    def get_medicine(self, soup):
        span = soup.find(lambda tag: tag.name == 'span' and '常用药品：' in tag.text)
        try:
            temp = span.find_next_siblings('a')
            medicine = [a['title'] for a in temp]
        except:
            return
        else:
            return medicine

    def get_therapies(self, soup):
        temp = re.findall(r'治疗方法：</span>(.*?)</p>', str(soup))[0]
        return [i for i in temp.split(' ')]

    def get_group(self, soup):
        return re.findall(r'易感人群：</span>(.*?)</p>', str(soup))[0]

    def get_infect_method(self, soup):
        return re.findall(r'传染方式：</span>(.*?)</p>', str(soup))[0]

    def get_reg_office(self, soup):
        span = soup.find(lambda tag: tag.name == 'span' and '挂号科室：' in tag.text)
        try:
            temp = span.find_next_siblings('a')
            reg_office = [a.get_text().strip() for a in temp]
        except:
            return
        else:
            return reg_office
        
    def get_site(self, soup):
        span = soup.find(lambda tag: tag.name == 'span' and '发病部位：' in tag.text)
        try:
            temp = span.find_next_siblings('a')
            sites = [a['title'] for a in temp]
        except:
            return
        else:
            return sites

    def get_alias(self, soup):
        span = soup.find(lambda tag: tag.name == 'span' and '别名：' in tag.text)
        try:
            alias_a = span.find_next_siblings('a')
            alias = [a['title'] for a in alias_a]
        except:
            return
        else:
            return alias



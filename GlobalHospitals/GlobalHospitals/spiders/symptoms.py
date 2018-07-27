from scrapy.http import Request
from scrapy import Spider
from bs4 import BeautifulSoup
import logging
from GlobalHospitals.pipelines import GlobalhospitalsPipeline as pipeline
from GlobalHospitals.items import GlobalhospitalsItem
import re
import requests
import random
import time

#  记录网站爬虫信息
logger = logging.getLogger('global_hospitals')
logger.setLevel(logging.DEBUG)  # 设置 scrapy 控制台的日志输出级别
fh = logging.FileHandler('log/global_hospitals.log', encoding='utf-8', mode='a')  # w 覆盖原文件，a 追加
fh.setLevel(logging.INFO)   # 设置重定向文件的日志输出级别
logger.addHandler(fh)

# 记录去重信息
logger_qc = logging.getLogger('crawled')
logger_qc.setLevel(logging.DEBUG)  # 设置 scrapy 控制台的日志输出级别
fh = logging.FileHandler('log/crawled.log', encoding='utf-8', mode='a')  # w 覆盖原文件，a 追加
fh.setLevel(logging.INFO)   # 设置重定向文件的日志输出级别
logger_qc.addHandler(fh)

class SymptomsSpider(Spider):
    name = 'symptoms'
    allowed_domains = ['zz.qqyy.com']

    def start_requests(self):
        url = 'http://zz.qqyy.com/letter/'
        yield Request(url, self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        # print('*' * 10, '[test success]')
        zimu_items = soup.find_all('div', class_='zimu_item')
        # print('*' * 10, '[test success]')
        if zimu_items == []:
            logger_qc.warning(soup)
        for zimu in zimu_items:  # 按字母搜索
            all_li = zimu.find_all('li')
            for li in all_li:  # 搜索每个字母下的症状链接
                symptom_name = li.find('a')['title']   # 症状名字
                d_link = li.find('a')['href']   # 症状详情链接
                y_link = re.sub(r'/(\w+).html', r'/yufang/\1.html', d_link)  # 症状预防链接
                if not pipeline.find(name=symptom_name):
                    pipeline.insert({'symptom_name': symptom_name})  # 记录症状名称
                if not pipeline.find(detail_link=d_link):  # 详情链接未记录
                    yield Request(d_link, self.crawl_detail, meta={'symptom_name': symptom_name})
                if not pipeline.find(yufang_link=y_link):  # 预防链接未记录
                    yield Request(y_link, self.crawl_precaution, meta={'symptom_name': symptom_name})

    def crawl_detail(self, response):
        item = GlobalhospitalsItem()
        symptom_name = response.meta['symptom_name']
        item['symptom_name'] = symptom_name
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 部位
        try:
            location = soup.find('div', class_='zz_par_l_t_r').find('p').text.strip()
        except Exception as e:
            logger.error('部位获取出错：%s' % response.url)
            logger.error(e)
            time.sleep(1)
            return Request(response.url, self.crawl_detail)
        else:
            item['location'] = location
        # 简介
        try:
            summary = soup.find('div', class_='zz_par_l_item').text.strip()
        except Exception as e:
            logger.error('简介获取出错：%s' % response.url)
            logger.error(e)
            time.sleep(1)
            return Request(response.url, self.crawl_detail)
        else:
            item['summary'] = summary
        # 科室
        try:
            p = soup.find(lambda tag: tag.name == 'span' and '科室' in tag.text).find_next_sibling('p').text.strip()
            offices = p.split(',')
        except Exception as e:
            logger.error('科室获取出错：%s' % response.url)
            logger.error(e)
        else:
            item['offices'] = offices
        # 相关疾病
        possible_target_div = soup.find_all('div', class_='zz_par_l_tit')
        for div in possible_target_div:
            if '相关疾病' in div.find('h3').text:
                ul = div.find_next_sibling('ul')
                related_diseases = [self.process_tag(li) for li in ul.find_all('li')]
                item['related_diseases'] = related_diseases
        # logger_qc.info(item)
        yield item
        pipeline.update(symptom_name, {'detail_link': response.url})

    def process_tag(self, tag):
        return tag.find('a')['title']

    def crawl_precaution(self, response):
        item = GlobalhospitalsItem()
        symptom_name = response.meta['symptom_name']
        item['symptom_name'] = symptom_name
        soup = BeautifulSoup(response.text, 'lxml')
        try:  # 如何预防
            precaution = soup.find('span', class_='zz_par_bottom').find_previous_sibling(lambda tag: tag.name in ['div', 'p']).text.strip()
        except Exception as e:
            logger.error('预防措施获取出错：%s' % response.url)
            logger.error(e)
            time.sleep(1)
            return Request(response.url, self.crawl_precaution)
        else:
            item['precaution'] = precaution
            # logger_qc.info(item)
            yield item
            pipeline.update(symptom_name, {'yufang_link': response.url})
from scrapy.http import Request
from scrapy import Spider
from bs4 import BeautifulSoup
import logging
from HealthMatters.items import HealthmattersItem
from scrapy.conf import settings
import pymongo
import re

logger = logging.getLogger('来一碗粿条')

class HealthSpider(Spider):

    def __init__(self):
        client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        db = client[settings['MONGO_DB']]
        self.coll = db[settings['MONGO_COLL']]

    name = 'health'
    allowed_domains = ['www.healthmatters.io']
    global base_url
    base_url = 'https://www.healthmatters.io'

    def start_requests(self):
        url = 'https://www.healthmatters.io/biomarker-categories'
        yield Request(url, self.parse)

    def parse(self, response):
        global base_url
        soup = BeautifulSoup(response.text, 'lxml')
        categories_list = soup.find('div', id='categories_list').find_all('div', class_='item category-item')
        for cate_item in categories_list:
            link = cate_item.find('a', class_='link')['href']
            url = base_url + link
            # print(url)
            yield Request(url, self.get_component_url)

    def get_component_url(self, response):
        global base_url
        soup = BeautifulSoup(response.text, 'lxml')
        main_item_headers = soup.find_all('div', class_='main_item-header')
        for header in main_item_headers:
            link = header.find('a')['href']
            url = base_url + link
            yield Request(url, self.get_info)

    def get_info(self, response):
        item = HealthmattersItem()
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('div', class_='desc-element_header').find('h1').get_text()
        item['url'] = response.url
        if self.coll.find_one({'title': title}):  # 去重
            logger.info('%s 已经爬过了！', title)
            return None
        normal_split_list = self.get_normal_range(soup)
        # print(title)
        item['title'] = title
        item['normal_range'] = normal_split_list
        # print(normal_split_list)
        try:
            def_raw = soup.find('div', class_='desc-element_content text-left').find_all('p')[1].get_text().strip()
        except IndexError:
            # logger.warning(e)
            yield item
            return None  # 没有定义，直接return
        else:
            if def_raw[-1] == ':':  # 若以:结尾
                definition = '.'.join(def_raw.split('.')[:-1]) + '.'  # 用英文句号分割段落，去掉最后一句，再用英文句号连接列表
            else:
                definition = def_raw
            item['definition'] = definition
            # yield item # test
        expla = self.get_explanation(soup)
        if expla:
            for k, v in expla.items():
                item[k] = v
        yield item
        
    def get_explanation(self, soup):
        info_items = soup.find_all('div', class_='info_item')
        explanations = dict()
        cate_count = 0  # 0表示过低，1表示过高
        for info_item in info_items:
            try:
                first_p = info_item.find('div', class_='info_text').find('p')
                p_next_siblings = first_p.next_siblings
            except AttributeError:
                logger.warning('p tags not found !')
            else:
                element_list = [first_p]
                for sibling in p_next_siblings:
                    element_list.append(sibling)
                expla_text = ''
                cate = 'low' if cate_count == 0 else 'high'
                special = ''
                for sibling in element_list:  # 5 种数据：一般 p 文本，ul 列表，drugs，causes，states
                    if sibling.name == 'p':
                        if 'causes' in sibling.get_text() and ':' in sibling.get_text():
                            # print('---原因字段存在---')
                            sentence_list = sibling.get_text()[:-1].split('.')
                            sentence_num = len(sentence_list)
                            last_sen = sentence_list[-1]
                            if 'causes' in last_sen and sentence_num > 2:  # 除去最后一句
                                expla_text += '.'.join(sentence_list[:-1]) + ' '
                            special = 'causes'
                            explanations[cate + '_' + special] = []
                        elif 'states' in sibling.get_text() and ':' in sibling.get_text():
                            # print('---状态字段存在---')
                            special = 'states'
                            explanations[cate + '_' + special] = []
                        elif 'drugs' in sibling.get_text().lower() and ':' in sibling.get_text():
                            # print('---药物字段存在---')
                            special = 'drugs'
                            explanations[cate + '_' + special] = []
                        elif special and re.findall(r'\W', sibling.get_text().strip()[0]):  # special 字段存在且句子的第一个字符不是字母
                            explanations[cate + '_' + special].append(sibling.get_text().strip())
                        else:
                            expla_text += sibling.get_text().strip() + ' '
                    elif sibling.name == 'ul':
                        print('---无符号列表存在---')
                        if special:  # special 已被赋值
                            explanations[cate + '_' + special] = []
                            for li in sibling.find_all('li'):
                                explanations[cate + '_' + special].append(li.get_text().strip())
                        else:
                            li_list = [li.get_text().strip() for li in sibling.find_all('li')]
                            temp = ', '.join(li_list) if ',' not in ''.join(li_list) else ' '.join(li_list)
                            expla_text += temp
                if expla_text:
                    explanations[cate] = expla_text
            finally:
                cate_count += 1
        return explanations

    def get_normal_range(self, soup):
        normal_range_raw = soup.find('div', class_='desc-element_content text-left').find('b').get_text().split('\n')
        normal_range = [i.strip() for i in normal_range_raw[2:] if i.strip() and i.strip() != 'or']
        normal_range_res = list(map(self.remove_c, normal_range))
        normal_split_list = list(map(self.split_unit, normal_range_res))
        return normal_split_list

    def remove_c(self, x):
        return x[:-1] if x[-1] in [',', '.'] else x  # 处理『9.58 - 405.306 mcg/dL,』等类似情况

    def split_unit(self, x):
        i = -1
        while(True):  # 为「60 - 120 mL/min per 1.73 m2.」等类似情况而设计
            split_list = x.split(' ')
            if -i > len(split_list):
                unit = split_list[-1]
                break
            temp = split_list[i:]
            unit = ' '.join(temp)
            if '/' in unit and '/' not in ''.join(split_list[:i]):  # 为「0 - 30 ng/dL per ng/mL/hr」等类似情况而设计
                break
            else:
                i = i - 1
        # print(unit)
        range_num = x.replace(unit, '').strip()
        # print(range_num)
        return [range_num, unit]
        

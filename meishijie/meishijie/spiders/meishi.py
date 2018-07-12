from scrapy.http import Request
from scrapy import Spider
from bs4 import BeautifulSoup
from meishijie.items import MeishijieItem
import logging
import re
from meishijie.mysql_pipelines.sql import Sql

class FoodSpider(Spider):
    
    name = 'meishi'
    allowed_domains = ['www.meishij.net']

    def start_requests(self):
        url = 'https://www.meishij.net/chufang/diy/'
        yield Request(url, self.parse)

    def parse(self, response):
        base_url = 'https://www.meishij.net'
        soup = BeautifulSoup(response.text, 'lxml')
        menus = soup.find('ul', class_='listnav_ul').find_all('li')[1:6]
        for m in menus:
            url = m.find('a')['href']
            url = base_url + url if not url.startswith('https') else url
            print(url) 
            yield Request(url, callback=self.get_cate)

    def get_cate(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.find('div', class_='main').find('dl').find_all('dd')
        for c in categories:
            url = c.find('a')['href']
            yield Request(url, self.get_items)

    def get_items(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        food_items = soup.find_all('div', class_='listtyle1')
        for i in food_items:
            url = i.find('a')['href']
            resource_loc = re.findall(r'/(\w+).html', url)[0]
            ret = Sql.select_food(resource_loc)
            if ret == 1:
                title = i.find('a')['title']
                print(title, '----该食谱已存在！----')
            else:
                yield Request(url, self.get_info, meta={'resource_loc': resource_loc})
        next_page_url = response.xpath('.//a[@class="next"]/@href').extract_first()
        if next_page_url:
            # print('============下一页===========')
            yield Request(next_page_url, self.get_items)

    def get_info(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        materials = soup.find('div', class_='materials_box')
        if materials is None:
            return
        item = MeishijieItem()
        item['food_name'] = soup.find('h1', class_='title').get_text().strip()
        item['cate_tags'] = soup.find('ul', class_='pathstlye1').find_all('li')[-1].get_text().strip()
        try:
            tag_list = [t.get_text().strip() for t in soup.find('div', class_='info1').find('dl').find_all('a')]
            item['func_tags'] = ','.join(tag_list)
        except Exception as e:
            logging.basicConfig(level=logging.WARNING)
            logging.warning(e)
            item['func_tags'] = ''
        info2 = soup.find('div', class_='info2').find_all('li')[:4]
        item['technique'] = info2[0].find('a').get_text().strip()
        try:
            item['difficulty'] = info2[1].find('a').get_text().strip()
        except:
            item['difficulty'] = '未知'
        try:
            item['persons'] = info2[2].find('a').get_text().strip()
        except:
            item['persons'] = '未知'
        item['flavor'] = info2[3].find('a').get_text().strip()
        # item['main_ingre'] = '，'.join([li.find('h4').get_text().strip() for li in materials.find('div', class_='yl zl clearfix').find_all('li')])
        main_temp = [li.find('h4') for li in materials.find('div', class_='yl zl clearfix').find_all('li')]
        # main_list = []
        # for m in main_temp:
        #     main_name = m.find('a').get_text().strip()
        #     how_much = ''
        #     temp = m.find('span').get_text().strip()  # 是否存在用量字段
        #     if temp:
        #         how_much = m.find('span').get_text().strip()
        #         num_temp =  re.sub(r'[\u4e00-\u9fa5]', '', how_much)  # 除去中文字符
        #         # unit = re.findall(r'[\u4e00-\u9fa5]+', how_much)[0]
                
        #         if num_temp == '':
        #             unit = re.findall(r'[\u4e00-\u9fa5]+', how_much)[0]  # 单位中没有数字，适用于”适量“，”少许“等情况
        #             main_list.append(':'.join([main_name, unit]))
        #         else:
        #             num = num_temp
        #             unit = re.findall(r'\d(\D+)', how_much)[-1]  # 单位（中文，英文），将位于数字后的非数字字符视为单位
        #             main_list.append(':'.join([main_name, num, unit]))
        #     else:
        #         main_list.append(main_name)
        item['main_ingre'] = ';'.join(self.get_ingre(main_temp))
        # item['minor_ingre'] = '，'.join([li.get_text().strip() for li in materials.find('div', class_='yl fuliao clearfix').find_all('li')])
        try:  # 是否存在辅料
            minor_temp = materials.find('div', class_='yl fuliao clearfix').find_all('li')
        except Exception as e:
            logging.basicConfig(level=logging.WARNING)
            logging.warning(e)
            item['minor_ingre'] = ''
        else:
            item['minor_ingre'] = ';'.join(self.get_ingre(minor_temp))
        item['resource_loc'] = response.meta['resource_loc']  # 资源位置，用于去重
        # print(item)
        yield item

    def get_ingre(self, materials):
        m_list = []
        for m in materials:
            minor_name = m.find('a').get_text().strip()
            how_much = ''
            temp = m.find('span').get_text().strip()  # 是否存在用量说明
            if temp:
                how_much = m.find('span').get_text().strip()
                num_temp =  re.sub(r'[\u4e00-\u9fa5]', '', how_much)  # 保留除去中文字符后的字符
                # unit = re.findall(r'[\u4e00-\u9fa5]+', how_much)[0]
                if num_temp == '':
                    # unit = re.findall(r'[\u4e00-\u9fa5]+', how_much)[0]  # 用量中没有数字，适用于”适量“，”少许“等情况
                    m_list.append(':'.join([minor_name, how_much]))
                else:
                    num = num_temp
                    try:
                        unit = re.findall(r'\d(\D+)', how_much)[-1]  # 单位（中文，英文），将位于数字后的非数字字符视为单位
                    except Exception as e:  # 处理诸如『（丝）适量』的特殊字段
                        logging.basicConfig(level=logging.WARNING)
                        logging.warning(e)

                        # unit = re.findall(r'[\u4e00-\u9fa5]+', how_much)[0]  # 用量中没有数字，适用于”适量“，”少许“等情况
                        m_list.append(':'.join([minor_name, how_much]))
                    else:
                        m_list.append(':'.join([minor_name, num, unit]))
            else:
                m_list.append(minor_name)
        return m_list
        
        
        
            

        
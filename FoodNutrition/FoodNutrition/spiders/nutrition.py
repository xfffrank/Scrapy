from scrapy.http import Request
from scrapy import Spider
from bs4 import BeautifulSoup
import logging
from FoodNutrition.items import FoodnutritionItem
from FoodNutrition.pipelines import FoodnutritionPipeline as fp

logger = logging.getLogger('爬虫记录仪')
base_url = 'http://www.quanyy.com'

class NutritionSpider(Spider):

    name = 'nutrition'
    allowed_domains = ['quanyy.com']

    def start_requests(self):
        url = 'http://www.quanyy.com/?Tools/tools_cf_type/aid/1.html'
        yield Request(url, self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            categories = soup.find('div', class_='d-left').find_all('li')[:-3]
        except:
            print('出错的 html 文档如下：')
            print(soup)
            raise
        for c in categories:
            href = c.find('a')['href'][1:]
            url = base_url + href
            yield Request(url, self.get_url_1st)

    def get_url_1st(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.find('div', class_='list_01').find_all('span')
        for c in categories:
            href = c.find('a')['href'][1:]
            url = base_url + href
            yield Request(url, self.get_url_2nd)

    def get_url_2nd(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.find('div', class_='list_02').find_all('span')
        for c in categories:
            href = c.find('a')['href'][1:]
            url = base_url + href
            # print(url)
            yield Request(url, self.crawl_info)

    def crawl_info(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = FoodnutritionItem()
        # info = soup.find('div', class_='list_03').find_all('tr')[:-1]
        item['fd_name'] = self.get_info(soup, 'fd_name')
        if fp.find_item(item['fd_name']):
            logger.info('%s 已经爬过了。', item['fd_name'])
            return None
        item['sub_category'] = self.get_info(soup, 'sub_category')
        
        edible_prop = self.get_info(soup, 'edible')
        energy = self.get_info(soup, 'energy_kcal')
        protein = self.get_info(soup, 'protein')
        fat = self.get_info(soup, 'fat')
        carbohydrate = self.get_info(soup, 'cho')
        water = self.get_info(soup, 'water')
        ash = self.get_info(soup, 'ash')
        dietary_fiber = self.get_info(soup, 'diet_fiber')
        vit_a = self.get_info(soup, 'vit_a')
        carotene = self.get_info(soup, 'tot_carotene')
        vit_b_6 = self.get_info(soup, 'vit_b_6')
        vit_b_12 = self.get_info(soup, 'vit_b_12')
        vit_c = self.get_info(soup, 'vit_c')
        vit_e = self.get_info(soup, 'vit_e')
        thiamin = self.get_info(soup, 'thiamin')
        riboflavin = self.get_info(soup, 'riboflavin')
        niacin = self.get_info(soup, 'niacin')
        p = self.get_info(soup, 'p')
        k = self.get_info(soup, 'k')
        se = self.get_info(soup, 'se')
        fe = self.get_info(soup, 'fe')
        ca = self.get_info(soup, 'ca')
        cu = self.get_info(soup, 'cu')
        i = self.get_info(soup, 'i')
        zn = self.get_info(soup, 'zn')
        na = self.get_info(soup, 'na')
        mn = self.get_info(soup, 'mn')
        mg = self.get_info(soup, 'mg')
        cholesterol = self.get_info(soup, 'cholesterol')
        if edible_prop:
            item['edible_prop'] = [edible_prop, '%']
        if energy:
            item['energy'] = [energy, '千卡']
        if protein:
            item['protein'] = [protein, '克']
        if fat:
            item['fat'] = [fat, '克']
        if carbohydrate:
            item['carbohydrate'] = [carbohydrate, '克']
        if water:
            item['water'] = [water, '克']
        if ash:
            item['ash'] = [ash, '克']
        if dietary_fiber:
            item['dietary_fiber'] = [dietary_fiber, '克']
        if vit_a:
            item['vit_a'] = [vit_a, '微克RE']
        if carotene:
            item['carotene'] = [carotene, '微克']
        if vit_b_6:
            item['vit_b_6'] = [vit_b_6, '毫克']
        if vit_b_12:
            item['vit_b_12'] = [vit_b_12, '毫克']
        if vit_c:
            item['vit_c'] = [vit_c, '毫克']
        if vit_e:
            item['vit_e'] = [vit_e, '毫克']
        if thiamin:
            item['thiamin'] = [thiamin, '毫克']
        if riboflavin:
            item['riboflavin'] = [riboflavin, '毫克']
        if niacin:
            item['niacin'] = [niacin, '毫克']
        if p:
            item['p'] = [p, '毫克']
        if k:
            item['k'] = [k, '毫克']
        if se:
            item['se'] = [se, '毫克']
        if fe:
            item['fe'] = [fe, '毫克']
        if ca:
            item['ca'] = [ca, '毫克']
        if cu:
            item['cu'] = [cu, '毫克']
        if i:
            item['i'] = [i, '毫克']
        if zn:
            item['zn'] = [zn, '毫克']
        if na:
            item['na'] = [na, '毫克']
        if mn:
            item['mn'] = [mn, '毫克']
        if mg:
            item['mg'] = [mg, '毫克']
        if cholesterol:
            item['cholesterol'] = [cholesterol, '毫克']
        yield item
        # pufa_tds = soup.find('div', class_='list_03').find_all('tr')[-2].find_all('td')
        # title = pufa_tds[0].get_text()
        # content = pufa_tds[1].get_text()
        # print(title, content)
        
    def get_info(self, soup, info_id):
        return soup.find('td', id=info_id).get_text().strip()


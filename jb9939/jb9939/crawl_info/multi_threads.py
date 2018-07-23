from queue import Queue
import random
import logging
import requests
import time
from threading import Thread
from multiprocessing import Pool, Process, Queue  # 为啥使用 Process 一定需要 Pool？
from bs4 import BeautifulSoup
import re
import pymongo


logger = logging.getLogger('多线程下载器')
logger.setLevel(logging.DEBUG)  # 有什么用？
fh = logging.FileHandler('jb9939.log', encoding='utf-8', mode='w')
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(fh)
logger.addHandler(ch)

client = pymongo.MongoClient(host='127.0.0.1', port=27017)
db = client['jb9939']
coll = db['diseases']

class DownloadInfo(object):

    def __init__(self):
        with open('../proxies.txt') as f:
            self.proxy_list = f.readlines()
        self.proxy = random.choice(self.proxy_list)
        self.headers = {
            'User-Agent': ''
        }
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
    
    def get(self, url):
        ua = random.choice(self.user_agent_list)
        self.headers['User-Agent'] = ua
        # response = requests.get(url, timeout=2, headers=self.headers)
        # return response
        try: 
            protocol = 'https' if 'https' in self.proxy else 'http'
            proxies = {
                protocol: self.proxy
            }
            response = requests.get(url, proxies=proxies, timeout=3, headers=self.headers)
            return response
        except:
            # print('一秒后更换代理')
            logger.debug('一秒后更换代理')
            time.sleep(1)
            self.proxy = random.choice(self.proxy_list)
            return self.get(url) 

    def download(self):
        q = Queue()
        start = time.time()
        print('downloading urls...')
        # 将 url 放入队列
        with open('../diseases_url.txt') as f:
            for line in f:
                q.put(line.strip())
        workers = []
        for _ in range(20):
            workers.append(Thread(target=self.get_info, args=(q,)))
            # workers.append(Process(target=self.get_info, args=(q,)))
            # workers.append(Process(target=self.multi_threads, args=(q,)))
        for w in workers:
            w.start()
        for w in workers:
            q.put(0)  # 让线程/进程能及时关闭
        for w in workers:
            w.join()
        print('[Download completed!] Total time: %.2f s' % (time.time() - start))

    def find_item(self, name):
        return True if coll.find_one({'disease_name': name}) else False

    def get_info(self, q):
        while(1):
            url = q.get()
            if url == 0:
                break
            # print(url)
            item = dict()
            response = self.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            disease_name = soup.find('div', class_='widsp').find('b').text.strip()
            if self.find_item(disease_name):
                logger.info(disease_name + " 已经爬过了！")
            else:
                alias = self.get_alias(soup)
                reg_office = self.get_reg_office(soup)
                come_on_site = self.get_site(soup)
                infect_method = self.get_infect_method(soup)
                group = self.get_group(soup)
                therapies = self.get_therapies(soup)
                medicine = self.get_medicine(soup)
                links = soup.find_all(lambda tag: tag.name == 'a' and '[详细]' in tag.text)
                base_url = 'http://jb.9939.com'
                intro_link = links[0]['href']
                symptom_link = links[1]['href']
                clinical_link = links[2]['href']
                intro_url = base_url + intro_link
                symptom_url = base_url + symptom_link
                clinical_url = base_url + clinical_link
                intro = self.get_intro(intro_url)
                symptoms = self.get_symptoms(symptom_url)
                clinical_exams = self.get_clinical_ex(clinical_url)
                item['disease_name'] = disease_name
                item['intro'] = intro
                item['symptoms'] = symptoms
                item['clinical_exams'] = clinical_exams
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
                # print(item)
                self.save(item)  # 保存到 mongo 数据库

    def save(self, item):
        try:
            coll.insert(item)
        except Exception as e:
            logger.warning(e)
        else:
            logger.info('%s 存储完毕', item['disease_name'])

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

    def get_intro(self, url):
        response = self.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        h2 = soup.find(lambda tag: tag.name == 'h2' and '简介' in tag.text)
        intro = h2.find_next_sibling('p').get_text().strip()
        return intro

    def get_symptoms(self, url):
        response = self.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        h4 = soup.find(lambda tag: tag.name == 'h4' and '典型症状' in tag.text)
        symptom_list = h4.find_next_sibling('p').find_all('a')
        return [a.text.strip() for a in symptom_list]

    def get_clinical_ex(self, url):
        response = self.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        h4 = soup.find(lambda tag: tag.name == 'h4' and '检查项目' in tag.text)
        symptom_list = h4.find_next_sibling('p').find_all('a')
        return [a.text.strip() for a in symptom_list]


if __name__ == '__main__':
    d = DownloadInfo()
    d.download()

    
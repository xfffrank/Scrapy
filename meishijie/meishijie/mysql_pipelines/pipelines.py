from .sql import Sql
from meishijie.items import MeishijieItem

class MeishijiePipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, MeishijieItem):
            food_name = item['food_name']
            cate_tags = item['cate_tags']
            func_tags = item['func_tags']
            flavor = item['flavor']
            technique = item['technique']
            difficulty = item['difficulty']
            persons = item['persons']
            main_ingre = item['main_ingre']
            minor_ingre = item['minor_ingre']
            resource_loc = item['resource_loc']
            Sql.insert_food(food_name, cate_tags, func_tags, flavor, technique, difficulty, persons, main_ingre, minor_ingre, resource_loc)
            print(food_name + ' 存储完毕')
            return item
from .sql import Sql
from dingdian.items import DingdianItem

class DingdianPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, DingdianItem):
            novel_id = item['novel_id']
            ret = Sql.select_name(novel_id)
            if ret == 1:
                print("该小说已存在")
            else:
                name = item['name']
                author = item['author']
                category = item['category']
                Sql.insert_dd_name(name, author, category, novel_id)
                print("开始存入小说标题")

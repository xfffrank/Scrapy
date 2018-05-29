from .sql import Sql
from dingdian.items import DingdianItem, ContentItem

class DingdianPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, DingdianItem):
            novel_id = item['novel_id']
            name = item['name']
            author = item['author']
            category = item['category']
            Sql.insert_dd_name(name, author, category, novel_id)
            print("开始存入小说标题")

        if isinstance(item, ContentItem):
            url = item['chapter_url']
            novel_id = item['novel_id']
            num = item['num']
            chapter_name = item['chapter_name']
            content = item['chapter_content']
            Sql.insert_dd_chatername(chapter_name, content, novel_id, num, url)
            print("小说存储完毕")
            return item

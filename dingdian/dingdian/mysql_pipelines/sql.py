import pymysql
from dingdian import settings

MYSQL_HOSTS = settings.MYSQL_HOSTS
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_DB = settings.MYSQL_DB

# Connect to the database
connection = pymysql.connect(host=MYSQL_HOSTS,
                             user=MYSQL_USER,
                             password=MYSQL_PASSWORD,
                             db=MYSQL_DB,
                             charset='utf8mb4', # 必须指定字符集，否则无法存入中文
                             cursorclass=pymysql.cursors.DictCursor)

class Sql:

    @classmethod
    def insert_dd_name(cls, novel_name, author, category, novel_id):
        with connection.cursor() as cursor:
            sql = 'INSERT INTO dd_name (`novel_name`, `author`, `category`, `novel_id`) \
                    VALUES (%s, %s, %s, %s)'
            cursor.execute(sql, (novel_name, author, category, novel_id))
        connection.commit()

    @classmethod
    def select_name(cls, novel_id):
        with connection.cursor() as cursor:
            sql = 'SELECT EXISTS(SELECT 1 FROM dd_name WHERE novel_id = %s)'
            cursor.execute(sql, (novel_id,))
            result = cursor.fetchone()
            a = [value for value in result.values()]
            return a[0]
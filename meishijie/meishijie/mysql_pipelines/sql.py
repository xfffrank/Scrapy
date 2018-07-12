import pymysql
from meishijie import settings

MYSQL_HOSTS = settings.MYSQL_HOSTS
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_DB = settings.MYSQL_DB

connection = pymysql.connect(
    host=MYSQL_HOSTS,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    db=MYSQL_DB,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

class Sql:

    @classmethod
    def insert_food(cls, food_name, cate_tags, func_tags, flavor, technique, difficulty, persons, main_ingre, minor_ingre, resource_loc):
        with connection.cursor() as cursor:
            sql = 'INSERT INTO meishi (food_name, cate_tags, func_tags, flavor, technique, difficulty, persons, main_ingre, minor_ingre, resource_loc) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, (food_name, cate_tags, func_tags, flavor, technique, difficulty, persons, main_ingre, minor_ingre, resource_loc))
        connection.commit()

    @classmethod
    def select_food(cls, resource_loc):
        with connection.cursor() as cursor:
            sql = 'SELECT EXISTS(SELECT 1 FROM meishi WHERE resource_loc = %s)'
            cursor.execute(sql, (resource_loc,))
            result = cursor.fetchone()
            a = [value for value in result.values()]
            return a[0]
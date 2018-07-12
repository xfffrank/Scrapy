import pymysql
import settings

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

with connection.cursor() as cursor:
    sql = 'SELECT EXISTS(SELECT 1 FROM meishi WHERE resource_loc = %s)'
    cursor.execute(sql, ('quduoduoquqixiawucha',))
    result = cursor.fetchone()
    a = [value for value in result.values()]
    print(a[0])
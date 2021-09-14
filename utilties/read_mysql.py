import pymysql # python 版mysql 客户端
import datetime
import sys,os # 操作系统 os.path.isfile("a.txt")
file_name="a.doc"
#if os.path.isfile(file_name):
#    print(file_name, "is file")

# mysql -u youyou -p
create_table_sql = """\
        CREATE TABLE IF NOT EXISTS {table_name} (
id INT AUTO_INCREMENT PRIMARY KEY,
sex VARCHAR(255) NOT NULL,
grade INT NOT NULL,
salary FLOAT NOT NULL,
consumption FLOAT NOT NULL
)
"""

insert_table_sql = """\
        INSERT INTO {table_name}(sex,grade,salary,consumption)
 VALUES('{sex}','{grade}','{salary}','{consumption}')
"""

query_table_sql = """\
        SELECT id,sex,grade,salary,consumption
FROM {table_name} 
"""

delete_table_sql = """\
        DELETE FROM {table_name}
"""

drop_table_sql = """\
        DROP TABLE IF EXISTS {table_name}
"""

def fun1(*t):
    print(t, type(t))

def fun2(**s):
    print(s, type(s))


def create_table_sql_fun(connection,cur, table_name_):
    print('--------------新建表--------------')
    cur.execute(create_table_sql.format(table_name = table_name_))
    connection.commit()
def insert_table_sql_fun(connection,cur, table_name_):
    print('--------------插入数据--------------')
    cur.execute(insert_table_sql.format(table_name = table_name_, sex = '女', grade = 1, salary = 2100.00, consumption = 3000.00))
    cur.execute(insert_table_sql.format(table_name = table_name_, sex = '女', grade = 2, salary = 2900.00, consumption = 2500.00))
    cur.execute(insert_table_sql.format(table_name = table_name_, sex = '女', grade = 3, salary = 3100.00, consumption = 4000.00))
    cur.execute(insert_table_sql.format(table_name = table_name_, sex = '男', grade = 2, salary = 4500.00, consumption = 8000.00))
    connection.commit()
def query_table_sql_fun(connection, cur,table_name_):
    print('--------------查询数据--------------')
    cur.execute(query_table_sql.format(table_name = table_name_))
    results = cur.fetchall()#fetchall函数，取到上一步全部结果
    print(f'id\tsex\t grade\tsalary\tconsumption')#\t是制表符
    for row in results:
        print(row[0], row[1], row[2], row[3], row[4],sep='\t')#sep 是分隔符
def delete_table_sql_fun(connection,cur, table_name_):
    print('--------------清除数据--------------')
    cur.execute(delete_table_sql)
    connection.commit()
def drop_table_sql_fun(connection,cur, table_name_):
    print('--------------删除表--------------')
    cur.execute(drop_table_sql.format(table_name = table_name_))
    connection.commit()


if __name__ == "__main__":
    #fun1(111,222,333,444,'woaini')
    #fun2(sex = '女', grade = 2, salary = 2900.00, consumption = 2500.00)
    #strr = "性别 = {sex}, 年龄 = {age} "
    #print(strr.format(sex = "nan",age = 123))
    a = input("请输入：")
    print("输出：",a)
    host = 'localhost'
    username = 'youyou'
    password = '112358'
    db_name = 'student'

    connection = pymysql.connect(
        host=host,
        user=username,
        password=password,
        charset='utf8mb4',#字符格式
        db=db_name)

    try:
        with connection.cursor() as cur:
            table_name = "cass"
            create_table_sql_fun(connection,cur, table_name)#建表
            insert_table_sql_fun(connection,cur, table_name)#插入数据
            query_table_sql_fun(connection,cur, table_name)#查询数据
            drop_table_sql_fun(connection,cur, table_name)#删除表
            connection.close()
    except Exception as e:
        connection.close()
        print("failed",Exception,e)


#!/usr/bin/env python
# coding=utf-8

import pymysql 
import datetime
import sys,os 
file_name="a.doc"
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

class Mysql():
    def __init__(self. db_name = 'student'):
        host = 'localhost'
        username = 'youyou'
        password = '112358'
        self.db_name = db_name
        self.table_name = "cass"
        self.connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            charset='utf8mb4',#字符格式
            db=db_name)

    def __exit__(self, exc_type, exc_value, traceback):
        connection.close()

    def create_table_sql_fun(self, connection, cur, table_name_):
        print('--------------新建表--------------')
        try:
            with self.connection.cursor() as cur:
                cur.execute(create_table_sql.format(table_name = table_name_))
                self.connection.commit()
        except Exception as e:
            print("failed",Exception,e)

    def insert_table_sql_fun(self, connection, cur, table_name_):
        print('--------------插入数据--------------')
        try:
            with self.connection.cursor() as cur:
                cur.execute(insert_table_sql.format(table_name = table_name_))
                self.connection.commit()
        except Exception as e:
            print("failed",Exception,e)
       
    def query_table_sql_fun(self, connection, cur, table_name_):
        print('--------------查询数据--------------')
        cur.execute(query_table_sql.format(table_name = table_name_))
        results = cur.fetchall()#fetchall函数，取到上一步全部结果
        print(f'id\tsex\t grade\tsalary\tconsumption')#\t是制表符
        for row in results:
            print(row[0], row[1], row[2], row[3], row[4],sep='\t')#sep 是分隔符
    def delete_table_sql_fun(self, connection, cur, table_name_):
        print('--------------清除数据--------------')
        cur.execute(delete_table_sql)
        connection.commit()
    def drop_table_sql_fun(self, connection, cur, table_name_):
        print('--------------删除表--------------')
        cur.execute(drop_table_sql.format(table_name = table_name_))
        connection.commit()
    def load(self, excel_file):
        import pandas as pd
        df = pd.read_sql(excel_file)
        """
        df.insert(self.connection)
        """

if __name__ == "__main__":
    print("test")
    m = Mysql("consuption")
    m.create_table_sql()
else:
    print("")
    



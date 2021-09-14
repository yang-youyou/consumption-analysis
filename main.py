from utilties import reply_mail
from utilties import read_excel
from utilties import operator_mysql
from algorithm import anlyze_income
from algorithm import anlyze_consum
from algorithm import anlyze_preconsum
from algorithm import anlyze_finanical

import pandas as pd
import argparse
import sys
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger("main.log")


def analyze_data(store_paint):
    print("analyze data", store_paint)
    

def clear_store_data(origin_data, excel_file, key, mysql_name):
    df = pd.read_csv(excel_file)
    list_mail = pd.DataFrame(df, columns = ['email'])
    ex = read_excel.Excel(origin_data,key)
    ex.clear(excel_file)
    sql = operator_mysql.Mysql(mysql_name)
    sql.load(excel_file)
    print("deal with data")

def reply_mail(mail_password, excel_file, key):
    logger.info("mail password : ",mail_password, excel_file, key)
    df = pd.read_csv(excel_file)
    list_mail = pd.DataFrame(df, columns = ['email'])
    print(list_mail.isnull())
    '''
    for accout in list_mail:
        with reply_mail.Mail(mail_password) as e:
            e.send([accout])
            logger.info("{} send succees".format(account))
    '''

if __name__ == "__main__":
    # -t 1 清洗参数、写数据库
    # -t 2 分析 + 绘图 | 总结结论，生成回馈内容（定制）
    # -t 3 发邮件
    origin_data= "origin_data.csv" # 问卷星导出数据，存储在本地，不上传
    excel_file = "data/data_info.csv"   # 清理/加密后得到的excel
    mysql_name = "consuption"      # 默认使用的mysql名称，pymysql数据库过程调用
    parser = argparse.ArgumentParser(description='clea data、analyze、reply mail') #清洗存储、分析、邮件回复
    parser.add_argument('-t', '--type', required=False, type=str,default='1', help='operate type, 1:clear, 2:anlyze, 3:mail, 4:game') 
    parser.add_argument('-p', '--password', required=False, type=str, help='mail password') # 邮箱密码
    parser.add_argument('-k', '--key', required=False, type=str, help='key store') # 参与问卷的人邮箱加密存储
    parser.add_argument('-n', '--name', required=False, type=str, help='mysql name') # 指定数据库名称
    parser.add_argument('--store', nargs='?', const=1, type=str, default='Flase')  # 分析产出中产生的图片是否保存
    parser.add_argument('-u', '--url', required=False, type=str, help='game url')
    args = parser.parse_args()

    if int(args.type) not in range(1,5,1):
        parser.print_help()
        sys.exit()

    if args.type == '1' and args.key is not None:
        if args.name is not None:
            mysql_name = args.name
        local_key = args.key
        clear_store_data(origin_data, excel_file, local_key, mysql_name)

    if args.type == '2':
        local_store_paint = eavl(args.store)
        if not isinstance(local_store_paint, bool):
            print("Set whether to save the picture: True|False") 
            sys.exit()
        anayze_data(local_store_paint)

    if args.type == '3' and args.password is not None and args.key is not None:
        local_mail_password = args.password
        local_key = args.password
        reply_mail(local_mail_password, excel_file, local_key)

    if args.type == '4':
        print("game start")
        print("game over")


#!/usr/bin/env python3

from genericpath import isdir, isfile
from io import FileIO
import os
import sys
import urllib.request
import time
import re
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import logging
from logging.handlers import RotatingFileHandler
smtp_server = 'smtp.foxmail.com' #foxmail
logger = logging.getLogger("mail.log")

class Mail(object):
    def __init__(self):
        print("start send mail:")

    def __enter__(self):
        return self

    def __send_fina_mail(self, mail_user, mail_pass, to_list, subject, content):
        mailContext = '''<html><body>
                        {}
                        </body></html>
                    '''.format(content)

        msg = MIMEText(mailContext, 'html', 'utf-8')
        msg['From'] = Header(mail_user, 'utf-8')
        msg['To'] = ','.join(to_list)
        msg['Subject'] = Header(subject, 'utf-8')

        try:
            server = smtplib.SMTP(smtp_server, port = 25, timeout = 120)
            server.login(mail_user, mail_pass)
            server.sendmail(mail_user, to_list, msg.as_string())
            logger.info("send mail success") 
        except smtplib.SMTPException:
            logger.error('send mail error')

    def __send_mail(self, content, to_list):
        mail_user = 'xxxxxxx.foxmail.com' #foxmail account
        mail_pass = 'yyyyyyy'             #password
        realtime = "{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        topic = '问卷反馈（{}）'.format(realtime)
        self.__send_real_mail(mail_user, mail_pass, to_list, topic, content)

    def __send(self, to_list, return_result):
        hi = "Hi,Dear:"
        p1 = "<font face=宋体>1) {} <font><br>".format(return_result)
        line = '<div style="font-family:verdana;padding:8px;border-radius:3px;solid">{}{}</div>'
        p = line.format(p1)
        main_progress = "<h1><font face=黑体>{}</font></h1>".format("感谢参与！")
        p1 = "<h2><font face=黑体>{}</font></h2>".format("分析结果反馈:")
        content = "{}{}{}".format(hi, main_progress, p1, p)
        self.__send_mail(content, to_list)
    
    def __exit__(self, exc_type, exc_value, traceback):
        print("send finish")

    def send(self, content, to_list):
        self.__send(to_list, content)

if __name__ == "__main__":
    print("reply test mode")
    with Mail() as s: # e = Mail() e.send(["ff.qq.com"], "ivode")
        s.send(["1841531744@qq.com"], "test information")
else:
    print("reply online mode")

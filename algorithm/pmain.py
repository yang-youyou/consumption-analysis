#!/usr/bin/env python3
# coding=utf-8
import os
import sys
import requests
import logging
import json
import argparse
import socket
import subprocess
import datetime
import shutil
import fcntl
import time
import socket
import re
from cassandra.cluster import Cluster
from email.header import Header
from email.mime.text import MIMEText
from logging.handlers import RotatingFileHandler
logger = logging.getLogger("RegressionTesting")
smtp_server = 'yanyun@qq.com'
logger.setLevel(level=logging.INFO)
rHandler = RotatingFileHandler(
    "reg_cassandra.log", maxBytes=20*1024*1024, backupCount=3)
rHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rHandler.setFormatter(formatter)
logger.addHandler(rHandler)

class FileIo(object):
    __obj_account = 0
    def __init__(self, file_name):
        self.file_name = file_name
        self.handle = open(file_name, 'r')
        self.fd = self.handle.fileno()
        logger.info('NO.{} new file {} read succ'.format(
            FileIo.__obj_account, self.file_name))
    def __new__(cls, *args, **kwargs):
        cls.__obj_account += 1
        return super().__new__(cls)

    def __enter__(self):
        return self

    def __del__(self):
        try:
            self.handle.close()
            logger.info('file %s del succ' % self.file_name)
        except:
            logger.error('file %s close fail' % self.file_name)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.handle.close()
            logger.info('file %s exit succ' % self.file_name)
        except:
            logger.error('file %s exit fail' % self.file_name)

    def read_all(self):
        list_line = list()
        for line in self.handle.readlines():
            list_line.append(line)
        return tuple(list_line)


class CassandraTool(object):
    __slots__ = ("__cass_name", "__cluster", "__table_map",
                 "__spacekey", "__session", "__host")

    def __init__(self, name, spacekey, table, host=['127.0.0.1']):
        self.__cass_name = name
        self.__host = host
        self.__table_map = table
        self.__spacekey = spacekey
        self.__cluster = Cluster(self.__host)
        #session = cluster.connect('user_action') #指定连接keyspace，相当于sql中use dbname
        self.__session = self.__cluster.connect(self.__spacekey)

    def info(self):
        logger.info("Cassndra informartion : \nname = {}\nhost = {}\nkeyspace = {}\ntable = {}".format(
            self.__cass_name, self.__host, self.__spacekey, self.__table_map))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.__cluster.shutdown()
            logger.info('close cassandra status : {}'.format(
                self.__cluster.is_shutdown))
            logger.info('close cassandra {} succ'.format(self.__cass_name))
        except:
            logger.error('close cassandra {} fail'.format(self.__cass_name))

    def query(self, table):
        assert(table in self.__table_map)
        #rows = session.execute('select * from m_realtime_events')
        rows = self.__session.execute(
            'select * from {}'.format(self.__table_map[table]))
        return rows

    def query_count(self, table):
        assert(table in self.__table_map)
        rows = self.__session.execute(
            'select count(*) from {}'.format(self.__table_map[table]))
        return rows.one()[0]

    def insert_ups_from_file(self, filename):
        assert(os.path.isfile(filename))
        with FileIo(filename) as f:
            t = f.read_all()
            count = 0
            exec_insert = 0
            insert_before = self.query_count("ups")
            start = time.time()
            for i, val in enumerate(t):
                li = val.split('\t')
                id_event = li[1]
                li_event = li[2].split('\004')  # 会抛异常
                count += len(li_event)
                for j, event_val in enumerate(li_event):
                    #print("%s %s %s"%(li[1],li_event[0],li_event[1]))
                    if j == len(li_event) - 1:
                        event_val = event_val[0:-1]  # 处理最后1个event的\n
                    try:
                        li_event_json = event_val.split('\001')
                        type_event = li_event_json[0]
                        str_event = li_event_json[1]
                        json_event = json.loads(str_event)
                        time_event = json_event["time"] * 1000
                    #except ValueError:
                    except:
                        logger.error("parse ups log line {} NO.{} evenet failed, device_id = {}, event_type = {}".format(
                            i, j, id_event, type_event))
                        continue
                    #print(id_event, type_event, time_event, str_event)
                    self.insert_one_ups(
                        id_event, type_event, time_event, str_event)
                    exec_insert += 1

            end = time.time()
            insert_after = self.query_count("ups")
            logger.info("file {} event num {}, exec insert num {}, actually insert num {}, cost time {}s".format(
                filename, count, exec_insert, insert_after - insert_before, end - start))

    def insert_dmp():
        pass

    def insert_ups_from_dir(self, log_path):
        if os.path.isdir(log_path):
            log_dir = os.listdir(log_path)
            logger.info('load {}  directory {} file'.format(
                log_path, len(log_dir)))
        else:
            logger.error('directory {} is empty'.format(log_path))
        for filename in log_dir:
            filename = os.path.join(log_path, filename)
            logger.info('load {} file'.format(filename))
            self.insert_ups_from_file(filename)

    def insert_one_ups(self, *data):
        assert(len(data) == 4)
        UPS_INSERT = 'insert into {} (device_id, event_type, time, event) VALUES (%s, %s, %s, %s)'.format(
            self.__table_map["ups"])
        self.__session.execute(UPS_INSERT, data)

    def get_cur_date(self):
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    def timestamp_to_time(self, timestamp):
        timeStruct = time.localtime(timestamp)
        return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)

    def update_model_list(self, model_name, model_path):
        model_dict = self.load_model_dict(model_name)
        model_dict[model_path] = self.get_cur_date()
        #dump
        self.dump_model_dict(model_name, model_dict)


class ParameTool(object):
    def __init__(self, raw_request_dir, raw_response_dir, data_center, req_dir_name, res_dir_name, id_file_name):
        self.__origin_input_dir = raw_request_dir
        self.__origin_output_dir = raw_response_dir
        self.__data_center = data_center
        self.__max_line = 10  # request 单个文件最大请求量
        self.__request_size = 0
        self.__response_size = 0
        self.__id_size = 0
        self.__id_set = set()
        if not os.path.isdir(data_center):
            os.mkdir(data_center)
        assert(isinstance(req_dir_name, str) and (len(req_dir_name) != 0))
        assert(isinstance(res_dir_name, str) and (len(res_dir_name) != 0))
        assert(isinstance(id_file_name, str) and (len(id_file_name) != 0))
        self.__request_path = os.path.join(data_center, req_dir_name)
        self.__response_path = os.path.join(data_center, res_dir_name)
        self.__id_file = os.path.join(data_center, id_file_name)
        if not os.path.isdir(self.__request_path):
            os.mkdir(self.__request_path)
        if not os.path.isdir(self.__response_path):
            os.mkdir(self.__response_path)
        self.__id_fd = open(self.__id_file, "a+")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info("requet account = {}, id number = {}, valid id = {}, response num = {}, request dir = {} response dir = {}, id file = {}".format(
            self.__request_size, self.__id_size, len(self.__id_set), self.__response_size, self.__request_path, self.__response_path, self.__id_file))
        self.__id_fd.close()
        print("requet account = {}, id number = {}, valid id = {}, response num = {}, request dir = {} response dir = {}, id file = {}".format(
            self.__request_size, self.__id_size, len(self.__id_set), self.__response_size, self.__request_path, self.__response_path, self.__id_file))

    def parse_file(self):
        pass

    def parse_request(self):
        if os.path.isdir(self.__origin_input_dir):
            log_dir = os.listdir(self.__origin_input_dir)
            logger.info('request load {} directory {} file'.format(
                self.__origin_input_dir, len(log_dir)))
        else:
            logger.error('request directory {} is empty'.format(log_path))
        for filename in log_dir:
            filename = os.path.join(self.__origin_input_dir, filename)
            logger.info('request load {} file'.format(filename))
            print("info request file ", filename)
            with FileIo(filename) as f:
                t = f.read_all()
                for i, val in enumerate(t):
                    if i == len(t) - 1:
                        break
                    try:
                        li = val.split('\t')
                        li_event = li[1].split('\004')  # 会抛异常
                        json_event = json.loads(li_event[1])
                    except:
                        logger.error(
                            "parse request file {}, line {} failed".format(filename, i))
                        continue
                    # "{}\n".format(len(li_event[1])))
                    self.insert_request(li_event[0], li_event[1])

    def insert_request(self, *data):
        request_file = "request{}.json".format(
            int(self.__request_size / self.__max_line) + 1)
        with open("{}/{}".format(self.__request_path, request_file), "a+") as f:
            re = f.write(data[1])
            re1 = self.__id_fd.write("{}\n".format(data[0]))
            #print(re1, re)
            self.__id_size += 1
            self.__request_size += 1
            self.__id_set.add(data[0])
            #print(data[0], len(data[0]))
            f.close()

    def parse_response(self):
        if os.path.isdir(self.__origin_output_dir):
            log_dir = os.listdir(self.__origin_output_dir)
            logger.info('response load {} directory {} file'.format(
                self.__origin_input_dir, len(log_dir)))
        else:
            logger.error('response directory {} is empty'.format(log_path))
        for filename in log_dir:
            filename = os.path.join(self.__origin_output_dir, filename)
            logger.info('response load {} file'.format(filename))
            print("info response file ", filename)
            with FileIo(filename) as f:
                t = f.read_all()
                for i, val in enumerate(t):
                    li = val.split('\t')
                    try:
                        li_event = li[1].split('\004')  # 会抛异常
                        json_event = json.loads(li_event[1])
                    except:
                        logger.error(
                            "parse response file {}, line {} failed".format(filename, i))
                        continue
                    if li_event[0] in self.__id_set:
                        #print(i, li_event[0], len(li_event[0]), li_event[1])
                        # "{}\n".format(len(li_event[1])))
                        self.insert_response(li_event[1])

    def insert_response(self, data):
        response_file = "response{}.json".format(
            int(self.__response_size / self.__max_line) + 1)
        with open("{}/{}".format(self.__response_path, response_file), "a+") as f:
            re = f.write(data)
            self.__response_size += 1
            f.close()


class ExecReg(object):
    """
    执行回归bench，得到response, 分析比对
    """
    def __init__(self, start_script, request_script, request_json_dir, check_response_dir, key_id_file):
        assert(os.path.isfile(start_script))
        assert(os.path.isfile(request_script))
        assert(os.path.isfile(key_id_file))
        assert(os.path.isdir(request_json_dir))
        assert(os.path.isdir(check_response_dir))
        self.__service_script = start_script
        self.__client_script = request_script
        self.__request_dir = request_json_dir
        self.__response_dir = check_response_dir
        self.__id_file = key_id_file

    def __enter__(self):
        return self

    def run(self):
        logger.info("start Ranker service, start script {}".format(self.__service_script))
        try:
            command = "sh {}".format(self.__service_script)
            print("command : ", command)
            subprocess.check_call("sh {}".format(self.__service_script), shell=True)
        except:
            logger.error("start ranker_service failed")
        for i in range(12):
            url="http://127.0.0.1:18080"
            try:
                r = requests.get(url) # wait RS run
                code = r.status_code
                #print("code : ", code)
            except:
                print("wait! visit except, appear error!")
                time.sleep(1)
        for i in range(12):
            reg_test_url="http://127.0.0.1:18080/set?key=reg_test&value=2"
            try:
                r = requests.get(reg_test_url)
                code = r.status_code
                #print("code : ", code)
            except:
                print("wait update reg_test")
                time.sleep(1)

        if os.path.isdir(self.__request_dir):
            log_dir = os.listdir(self.__request_dir)
            logger.info('load {}  directory {} file'.format(
                self.__request_dir, len(log_dir)))
            print('load {}  directory {} file'.format(
                self.__request_dir, len(log_dir)))
        else:
            print("directory {} is empty".format(self.__request_dir))
            logger.error('directory {} is empty'.format(self.__request_dir))

        for filename in log_dir:
            filename = os.path.join(self.__request_dir, filename)
            logger.info('send request form file {}'.format(filename))
            print("sh {} {}".format(self.__client_script, filename))
            try:
                subprocess.check_call("sh {} {}".format(self.__client_script, filename), shell=True)
            except:
                print("exec failed")
                logger.error("send ranker_service failed")

    def __start_server(self):
        pass
    def __start_request(self):
        pass
    def __close_request(self):
        # service set 10201/set?key=test_reg&value=0
        pass
    def __analyze(self):
        file_path="../reg_log/response/"
        responseDir = re.findall(r'ranker_service_cicd.response+?\.',file_path)
        resp_id_set = set()
        resp_val_set = set()
        check_id_set = set()
        check_val_set = set()
        for file in responseDir:
            with FileIo(file) as f:
                t = f.read_all()
                for i,line in enumerate(t):
                    li = line.split("t")
                    li_event = li[1].spilt('\004')
                    resp_id_set.add(li_event[0])
                    resp_val_set.add(li_event[1])
        for file in os.listdir(self.__response_dir):
            file = os.path.join(self.__response_dir, file)
            with FileIo(file) as f:
                t = f.read_all()
                for i,line in enumerate(t):
                    check_val_set.add(line)

        with FileIo(self.__id_file) as f:
            t = f.read_all()
            for i,line in enumerate(t):
                check_id_set.add(line)
        id_set = resp_id_set & check_id_set
        id_ratio = len(id_set) * 1.0 / len(check_id_set)
        val_set = resp_val_set & check_val_set
        val_ratio = len(val_set) * 1.0 / len(check_val_set)
        print("id 覆盖率为 : {}\n response 相同比率为 : {}".format(id_ratio, val_ratio))

    def __exit__(self, exc_type, exc_value, traceback):
        print("finish")
        #stop Rs
        self.__analyze()
        pass
def main():
    host = ["127.0.0.1"]
    keyspace = "user_action"
    table = {"ups": "m_realtime_events", "dmp": "realtime_user_action"}
    ups_log_file = "../reg_log/ups/ranker_service_cicd.ups"
    ups_log_dir = "../reg_log/ups/"
    request_log_file = "../reg_log/request/ranker_service_cicd.request"
    request_log_dir = "../reg_log/request/"
    response_log_file = "../reg_log/response/ranker_service_cicd.response"
    response_log_dir = "../reg_log/response/"
    data_dir = "./result"
    input_dir_name = "request"
    output_dir_name = "response"
    id_dir_name = "id.key"
    with CassandraTool("Rs-Cassandra", keyspace, table, host) as cass:
        cass.info()
        # 灌数据库
        #cass.insert_one_ups("6107a8f7dfee480001156f4y","cli",1627674096,"xxxyyyy")
        #cass.insert_ups_from_file(ups_log_file)
        #cass.insert_ups_from_dir(ups_log_dir)
        #rows = cass.query("ups")
        #for row in rows:
        #    print(row[0],row[1],row[2])
    '''
    with FileIo(response_log_file) as f:
        t = f.read_all()
        for i,val in enumerate(t):
            if i > 1:
                pass
                #break
            li = val.split('\t')
            li_event = li[1].split('\004') #会抛异常
            #print("%s %s"%(li_event[0],len(li_event[1])))
            json_event = json.loads(li_event[1])
            print("%s %s"%(li_event[0],len(json_event)))
    '''

    with ParameTool(request_log_dir, response_log_dir, data_dir, input_dir_name, output_dir_name, id_dir_name) as pa:
        # 清洗输入输出参数
        #pa.parse_request()
        #pa.parse_response()
        pass

    with ExecReg("run_ranker.sh", "run_client.sh", "{}/{}".format(data_dir, input_dir_name),
            "{}/{}".format(data_dir, output_dir_name), "{}/{}".format(data_dir, id_dir_name)) as ex:
        ex.run()

if __name__ == "__main__":
    main()

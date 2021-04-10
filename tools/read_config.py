#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
@project: apiAutoTest
@author: zy7y
@file: read_config.py
@ide: PyCharm
@time: 2020/7/31
"""
import yaml
from loguru import logger


class ReadConfig(object):  #这个是读取数据的类
    data = None
    #定义data数据

    #把对应的错误用日志输出出来，输出到控制台或者日志文件
    @logger.catch
    def __init__(self):
        # 指定编码格式解决，win下跑代码抛出错误
        with open('../config/config.yaml', 'r', encoding='utf-8') as file:
            self.data = yaml.load(file.read(), Loader=yaml.FullLoader)     # load是将yaml类型转换为python数据类型
            #yaml.load解析文件流中第一个yaml文档，并生成python对象。

    @logger.catch
    def read_serve_config(self, sever_name):
    #读取服务器地址

        logger.info(self.data.get('server').get(sever_name))
        #获取yaml文件里的server内容，里面有test和dev,再get指定一下
        return self.data.get('server').get(sever_name)

    @logger.catch
    def read_response_reg(self):
    # 这是个获取token的          jsonpath表达式           ，      不是数据    ，      是表达式！
        get_token = self.data.get("response_reg").get("token")
        get_resp = self.data.get('response_reg').get('response')
        logger.info(f'从响应中提取的token表达式: {get_token}')   #另一种输出，格式好看点,在最下面显示
        logger.info(f'从响应提取的需要校验的表达式: {get_resp}')
        return get_token, get_resp

    @logger.catch
    #这里指定路径名称获取文件数据
    def read_file_path(self, file_path_name):
        return self.data.get('file_path').get(file_path_name)

    def read_email_setting(self):
        return self.data.get('email')

if __name__ == '__main__':  #测试下类功能有没有问题
    read_config = ReadConfig()  #实例化
    result = read_config.data
    print(type(result),result)  #<class 'dict'>

    result = read_config.read_serve_config('dev')
    print(result,type(result))  #接口测试中不变的那一串部分地址

    response_reg,token_reg = read_config.read_response_reg()
    print(response_reg,token_reg)

    result = read_config.read_file_path('case_data')
    print(result)

    result = read_config.read_file_path('test')  #读取不存在的文件路径
    print(result,type(result))   #None <class 'NoneType'>

    result = read_config.read_email_setting()
    print(result,type(result))




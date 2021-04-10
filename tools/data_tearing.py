#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
@project: apiAutoTest
@author: zy7y
@file: data_tearing.py
@ide: PyCharm
@time: 2020/8/10
"""
import json
from json import JSONDecodeError  #异常类

import jsonpath
from test import logger


class TreatingData(object):  #数据处理
    """
    处理header/path路径参数(url，不是文件)/请求data依赖数据代码
    """

    def __init__(self):
        #定义两个字典
        self.no_token_header = {}
        self.token_header = {}

    def treating_data(self, is_token, parameters, dependent, data, save_response_dict):
        #is_token 对应excel里面的token操作  空白 或者 读 写
        #parameters 对应url路径path参数依赖的内容
        #dependent 依赖数据的内容，元素表格中的jsonpath表达式
        #data   excel中  请求数据 内容，真正的data是请求+依赖
        #save_response_dict 保存实际响应的字典对象

        # 使用哪个header
        if is_token == '':
            header = self.no_token_header
        else:
            header = self.token_header
        logger.info(f'处理依赖前data的数据:{data}')

        # 处理依赖数据data  （请求数据的依赖）
        if dependent != '':
            #dependent两种形式
            #{"case_002": ["$.data.id"],"case_001":["$.meta.msg","$.meta.status"]}
            #key={"case_002": ["$.data.id"],"case_001":["$.meta.msg","$.meta.status"]}
            if dependent.find('=') != -1:  #存在上面的key= 形式，就把key和后面的分开保存为字典
                dependent_key = dependent.split('=')[0]
                dependent_value = dependent.split('=')[1]
                # dependent_data = {‘key’:{'id':1}}
                dependent_data = {dependent_key: save_response_dict.read_depend_data(dependent_value)}
            else:
                # {'id': 1}  dependent_data是最终值
                dependent_data = save_response_dict.read_depend_data(dependent)  # 直接保存
            logger.debug(f'依赖数据解析获得的字典{dependent_data}')


            if data != '':
                data = json.loads(data)#字符串转换为python对象,序列化

                exists_key = False  #不存在key就False，先默认为False，下面会具体判断有没有key
                # 处理data与依赖中有相同key的问题（原来请求就已经有name参数了，依赖里又从别的地方获取name参数）, 目前支持列表，字典,本地 列表形式调试通过，需要在定义时，data中该key定义成列表
                # 实例{"id": [1],"user":{"username":"123"}}
                for k, v in data.items(): #data excel中 请求数据栏 的内容,只是请求数据
                    for dk, dv in dependent_data.items():  #这是请求的依赖数据字典
                        if k == dk:

                            #请求数据为{"id": [1], "user": {"username": "123"}}，依赖数据为{"id": 500, "user": {"admin": "12345"}}
                            #data = {"id": [1,500], "user": {{"username": "123"},{"admin": "12345"}}
                            if isinstance(data[k], list):  #有相同的key，并且key的类型为列表（这里是按照原来的请求数据判断），就直接添加
                                data[k].append(dv)
                            if isinstance(data[k], dict):  #如果key对应的是字典，就更新
                                data[k].update(dv)
                            exists_key = True   # 如果修改了就改为存在

                if exists_key is False:  #不存在同样key，直接合并
                    #合并组成一个新的data  # dependent_data={'id':500}  data={'username':'admin'}
                    # 最终data = {'id':500,'username':admin}
                    dependent_data.update(data)
                    data = dependent_data
                    logger.info(f'data有数据，依赖有数据时 {data}')

            else:
                # data为空直接把依赖赋值给data
                data = dependent_data
                logger.info(f'data无数据，依赖有数据时 {data}')
        else:  #依赖为空
            if data == '':
                data = None
                logger.info(f'data无数据，依赖无数据时 {data}')
            else:
                data = json.loads(data)   # 前面的依赖数据  已经在获取依赖数据的方法中python对象化了
                logger.info(f'data有数据，依赖无数据 {data}')

        # 处理路径参数Path的依赖 （url路径的依赖）   总结：分开放，先把能提取对应转换的变过来，变不了的保留，最后一起map列表字符串化
        # 传进来的参数类似 {"case_002":"$.data.id"}/item/{"case_002":"$.meta.status"}，进行列表拆分
        path_list = parameters.split('/')  # {"case_002":"$.data.id"}  item  {"case_002":"$.meta.status"}
        # 获取列表长度迭代
        for i in range(len(path_list)):
            # 按着
            try:
                # 尝试序列化成dict:         中间的state或者数字2不能转换
                path_dict = json.loads(path_list[i])  #字符串转换为python对象，Python对象包括：所有Python基本数据类型，列表，元组，字典，自己定义的类，等等等等
            except JSONDecodeError as e:
                # 序列化失败此path_list[i]的值不变化
                logger.error(f'无法转换字典，进入下一个检查，本轮值不发生变化:{path_list[i]},{e}') #json.loads('2')，转换不了先保存下面会再处理
                # 跳过进入下次循环
                continue
            else:
                # 解析该字典，获得用例编号，表达式
                logger.info(f'{path_dict}')   # 打印第一次转换成果，已经转换成功的放进来

                # 处理json.loads('数字')正常序列化导致的AttributeError  为什么不直接map化呢？？？（先把能依赖的依赖了）
                try:
                    for k, v in path_dict.items():
                        #{'case_002':'$.data.id'}      case_002   .   $.data.id
                        try:
                            # 尝试从对应的case实际响应提取某个字段内容{'id':500} , $.data.id   根据key从实际响应中提取value
                            path_list[i] = jsonpath.jsonpath(save_response_dict.actual_response[k], v)[0]
                            # 500   path_list[i]是最终地址
                        except TypeError as e:
                            logger.error(f'无法提取，请检查响应字典中是否支持该表达式,{e}')  # 类似找不到这种状态
                except AttributeError as e:

                    logger.error(f'类型错误:{type(path_list[i])}，本此将不转换值 {path_list[i]},{e}')
        # 字典中存在有不是str的元素:使用map 转换成全字符串的列表     #path_list = [500,'item',200]
        path_list = map(str, path_list)
        #path_list = ['500','item','200']

        # 将字符串列表转换成字符：500/item/200
        parameters_path_url = "/".join(path_list)  #相当于部分路径
        logger.info(f'path路径参数解析依赖后的路径为{parameters_path_url}')
        return data, header, parameters_path_url
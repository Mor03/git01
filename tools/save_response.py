#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
@project: apiAutoTest的副本
@author: zy7y
@file: save_response.py
@ide: PyCharm
@time: 2020/8/8
"""
import json

import jsonpath  # 提取json，dict某个字段的值
from loguru import logger


class SaveResponse(object):   # 保存实际响应结果，处理依赖数据提取
    def __init__(self):
        # 定义实际响应字典
        self.actual_response = {}

    # 保存实际响应
    def save_actual_response(self, case_key, case_response):  # 传入用例 和 对应请求返回的数据
        """
        每个接口执行完成得到一个响应，通过用例case
        :param case_key:用例编号
        :param case_response:对应用例编号的  实际响应
        """
        self.actual_response[case_key] = case_response  #把对应编号和和响应变成键值对，放入字典里
        logger.info(f'当前字典数据{self.actual_response}')  #每次调用打印

    # 读取依赖数据
    def read_depend_data(self, depend):
        """
        :param depend: 需要依赖数据字典{"case_001":"['jsonpath表达式1', 'jsonpath表达式2']"}
        """
        depend_dict = {} #loads str转换为python
        depend = json.loads(depend)  # 字符串转换成Python对象  {"case_002": ["$.data.id"],"case_001":["$.meta.msg","$.meta.status"]}
        for k, v in depend.items():  #key value,循环遍历
            # 取得依赖中对应case编号的值提取表达式
            try:
                for value in v: #v是列表，可能一条可能几条
                    # value : '$.data.id'
                    # 取得 对应用例编号 的 实际响应结果 放入actual
                    actual = self.actual_response[k]
                    # 返回依赖数据的key
                    d_k = value.split('.')[-1]  # d_k ='id'，取最后一个标签
                    # 添加到依赖数据   字典  并返回
                    depend_dict[d_k] = jsonpath.jsonpath(actual, value)[0]#方法返回的是数组，所以取下标拿到值
                    #实际响应actual ，根据value格式在实际响应中查找
                    #假设actual内容  {'data':{'id':1},'meta':{'msg':'成功'}}
                    # value : '$.data.id'  jsonpath方法就相当于从里面最终取出id对应的值
                    #这个实例相当于depend_dict = {'id':1},多条就向后面追加上

            except TypeError as e:
                logger.error(f'实际响应结果中无法正常使用该表达式提取到任何内容，发现异常{e}')
        return depend_dict  # 得到数据依赖到底要什么数据，并添加到depend_dict中

# 调试代码
if __name__ == '__main__':
    sr = SaveResponse()
    sr.save_actual_response("case_001", {'data': None, 'meta': {'msg': '参数错误', 'status': 400}})
    sr.save_actual_response("case_002", {'data': {'id': 500, 'rid': 0, 'username': 'admin', 'mobile': '13718940015', 'email': '1172366686@qq.com', 'token': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjUwMCwicmlkIjowLCJpYXQiOjE1OTY4NTYwNTQsImV4cCI6MTU5Njk0MjQ1NH0.6D9u4x8M4yVWAsK-zJPCw2e7sddClFV-JvntuQyZ8JA'}, 'meta': {'msg': '登录成功', 'status': 200}})

    print(sr.actual_response, type(sr.actual_response))
    depned_str = """{"case_002": ["$.data.id"],"case_001":["$.meta.msg","$.meta.status"]}"""   #依赖数据，依赖别人的数据 再提取合成新的

    result = sr.read_depend_data(depned_str)   #上面要先添加保存实际响应，下面的依赖 才能查找对应的用例数据
    print(result)
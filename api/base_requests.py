#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
@project: apiAutoTest
@author: zy7y
@file: base_requests.py
@ide: PyCharm
@time: 2020/7/31
"""
from loguru import logger
import requests


class BaseRequest(object):
    def __init__(self):
    # 修改时间：2020年9月14日17:09
    # 确保，整个接口测试中，使用同一个requests.Session() 来管理cookie
        self.session = requests.Session()

    # 请求
    def base_requests(self, method, url, parametric_key=None, data=None, file_var=None, file_path=None, header=None):
        """

        :param method: 请求方法 get put delete post head patch
        :param url: 请求url  http://xxxxxxip:端口号/接口地址
        :param parametric_key:
         入参关键字， get/delete/head/options/请求使用params,
         post/put/patch请求可使用json（application/json）/data

        :param data: 参数数据，默认等于None，里面包含文件参数等信息

        上传才使用？    传文件方式和文件在本地地址
        :param file_var: 接口中接受文件的参数关键字，例如以流的形式post上去
        :param file_path: 文件对象的地址， 单个文件直接放地址：/Users/zy7y/Desktop/vue.js
        多个文件格式：["/Users/zy7y/Desktop/vue.js","/Users/zy7y/Desktop/jenkins.war"]

        :param header: 请求头
        :return: 返回json格式的响应
        """
        # 修改时间：2020年9月14日17:09
        session = self.session  # 返回一个自动管理cookie的requests对象，与requests方法一致  把类的数据传到方法里
        if (file_var in [None, '']) and (file_path in [None, '']):  #没有文件
            files = None
        else:
            # 文件不为空的操作  判断是否为多个文件路径，是则拆分
            if file_path.startswith('[') and file_path.endswith(']'):
                file_path_list = eval(file_path)
                #["/Users/zy7y/Desktop/vue.js","/Users/zy7y/Desktop/jenkins.war"]  这是字符串，eval后就是列表，就可以迭代取值
                #eval()函数将字符串str当成有效的表达式来求值并返回计算结果 print(eval('1+2')) 输出3
                files = []
                # 多文件上传
                for file_path in file_path_list:
                    files.append((file_var, (open(file_path, 'rb'))))  # 多个分开放入字典，file_var是名称？
            else:
                # 单文件上传
                files = {file_var: open(file_path, 'rb')}   # 单个直接放入字典

        # 入参关键字， get / delete / head / options / 请求使用params,
        # post / put / patch请求可使用json（application / json） / data
        if parametric_key == 'params':  # 只需要基础参数   。这里不用传文件地址  也就是没有file_var 和 file_path
            #  下面相当于requests.request(method=get) 或者直接request.get（。。。）
            res = session.request(method=method, url=url, params=data, headers=header)
        elif parametric_key == 'data':  #  需要基础+文件（文件参数都在data里面，所以大家都要带上data）
            res = session.request(method=method, url=url, data=data, files=files, headers=header)
        elif parametric_key == 'json':
            res = session.request(method=method, url=url, json=data, files=files, headers=header)
        else:
            raise ValueError('可选关键字为：get/delete/head/options/请求使用params, post/put/patch请求可使用json（application/json）/data')

        logger.info(f'请求方法:{method}，请求路径:{url}, 请求参数:{data}, 请求文件:{files}, 请求头:{header})')  # 没有文件输出就为空
        return res.json()  # 以json格式返回接收到的数据




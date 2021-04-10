#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
@project: apiAutoTest
@author: zy7y
@file: test_api.py
@ide: PyCharm
@time: 2020/7/31
"""

import json
import jsonpath
from loguru import logger
import pytest
import allure
from api.base_requests import BaseRequest  # api是包

from tools.data_tearing import TreatingData
from tools.read_config import ReadConfig

from tools.read_data import ReadData

from tools.save_response import SaveResponse

# 读取配置文件

rc = ReadConfig()  #类里面有方法没有参数
# 把要的数据读取出来，和之前的main测试内容一样
base_url = rc.read_serve_config('dev')
token_reg, res_reg = rc.read_response_reg()  # token 和 meta 表达式
# 获取目录
case_data_path = rc.read_file_path('case_data')
report_data = rc.read_file_path('report_data')
report_generate = rc.read_file_path('report_generate')
log_path = rc.read_file_path('log_path')   #这里有问题
report_zip = rc.read_file_path('report_zip')
"""
file_path:
  case_data: ../data/case_data.xlsx  #测试数据路径
  report_data: ../report/data/  #报告生成data路径
  report_generate: ../report/html/  #报告生成可视化allure路径
  report_zip: ../report/html/apiAutoTestReport.zip  #报告生成压缩类型路径
  log_path: ../log/运行日志{time}.log #日志路径
"""
email_setting = rc.read_email_setting()


# 实例化响应的对象
save_response_dict = SaveResponse()   # 里面有2个函数（注意这里只是处理依赖方法的对象，真正要用的在下面的TreatingData（）里面），一个保存实际响应结果dict（case_001,对应的data mata），另一个
# 函数根据1的dict处理 请求依赖 数据，提取需要的.得到数据依赖到底要什么数据，并添加到depend_dict中

# 读取excel数据对象
data_list = ReadData(case_data_path).get_data()    # 把每一行数据放到元组（），再放到大列表

# 数据处理对象
treat_data = TreatingData()   #处理是否带header和数据依赖，路径依赖实际返回值.#return data(原始请求数据), header, parameters_path_url（解析依赖后的部分数据）

# 请求对象
br = BaseRequest()  # br能调用不同request方法，并添上对应的参数
logger.info(f'配置文件/excel数据/对象实例化，等前置条件处理完毕\n\n')


class TestApiAuto(object):


    # 启动方法
    def run_test(self):
        import os, shutil
        if os.path.exists('../report') and os.path.exists('../log'):
            shutil.rmtree(path='../report')  # 如果存在就删了
            shutil.rmtree(path='../log')

        # 日志存取路径： ../log/xxxx.log
        logger.add(log_path, encoding='utf-8')

        # 运行报告  report_data = ../report/data
        # 相当于命令 pytest --alluredir='../report/data'
        pytest.main(args=[f'--alluredir={report_data}'])
        # 本地生成 allure 报告文件，需注意 不用pycharm等类似ide 打开会出现无数据情况
        os.system(f'allure generate {report_data} -o {report_generate} --clean')  #  report_generate: ../report/html/  #报告生成可视化allure路径
        # 直接启动allure报告（会占用一个进程，建立一个本地服务并且自动打开浏览器访问，ps 程序不会自动结束，需要自己去关闭）
        os.system(f'allure serve {report_data}')
        logger.warning('报告已生成')

    # [(),(),()] 帮我们做for循环，得到（）（）（），分别解包执行下列代码
    """
    #数据驱动方法，几个数据跑几次
        #pytest自带测试方法   parametrize两个变量，
        @pytest.mark.parametrize('a',[1,2])
        def test_001(self,a):
            assert a == 1
            #这里跑两次，一次成功
    #如果改为('a,b',[(1,2),(3,4)]) 用列表更容易识别
    #这也是执行两次，第一次a=1,b=2 第二次a=3,b=4
    """
    @pytest.mark.parametrize('case_number,case_title,path,is_token,method,parametric_key,file_var,'
                             'file_path, parameters, dependent,data,expect', data_list)
    def test_main(self, case_number, case_title, path, is_token, method, parametric_key, file_var,
                  file_path, parameters, dependent, data, expect):

        # 感谢：https://www.cnblogs.com/yoyoketang/p/13386145.html，提供动态添加标题的实例代码
        # 动态添加标题
        allure.dynamic.title(case_title)

        logger.debug(f'⬇️⬇️⬇️...执行用例编号:{case_number}...⬇️⬇️⬇️️')
        with allure.step("处理相关数据依赖，header"):

            # return data(原始请求数据), header, parameters_path_url（解析依赖的数据）
            data, header, parameters_path_url = treat_data.treating_data(is_token, parameters, dependent, data,
                                                                         save_response_dict)
            #allure报告还支持显示许多不同类型的附件，可以补充测试结果
            allure.attach(json.dumps(header, ensure_ascii=False, indent=4), "请求头", allure.attachment_type.TEXT)
            allure.attach(json.dumps(data, ensure_ascii=False, indent=4), "请求数据", allure.attachment_type.TEXT)

        with allure.step("发送请求，取得响应结果的json串"):
            allure.attach(json.dumps(base_url + path + parameters_path_url, ensure_ascii=False, indent=4), "最终请求地址",
                          allure.attachment_type.TEXT)
            res = br.base_requests(method=method, url=base_url + path + parameters_path_url,
                                   parametric_key=parametric_key, file_var=file_var, file_path=file_path,
                                   data=data, header=header)
            allure.attach(json.dumps(res, ensure_ascii=False, indent=4), "实际响应", allure.attachment_type.TEXT)

        with allure.step("将响应结果的内容写入实际响应字典中"):
            save_response_dict.save_actual_response(case_key=case_number, case_response=res)
            allure.attach(json.dumps(save_response_dict.actual_response, ensure_ascii=False, indent=4), "实际响应字典",
                          allure.attachment_type.TEXT)

            # 写token的接口必须是要正确无误能返回token的，前面先提取再判断
            if is_token == '写':
                with allure.step("从登录后的响应中提取token到header中"):
                    # $.data.token
                    treat_data.token_header['Authorization'] = jsonpath.jsonpath(res, token_reg)[0]  #字典

        with allure.step("根据配置文件的提取响应规则提取实际数据"):
            really = jsonpath.jsonpath(res, res_reg)[0]
            allure.attach(json.dumps(really, ensure_ascii=False, indent=4), "提取用于断言的实际响应部分数据",
                          allure.attachment_type.TEXT)

        with allure.step("处理读取出来的预期结果响应"):
            # 处理预期结果数据中使用True/False/None导致的无法转换bug
            if 'None' in expect:
                expect = expect.replace('None', 'null')
            if 'True' in expect:
                expect = expect.replace('True', 'true')
            if 'False' in expect:
                expect = expect.replace('False', 'false')
            expect = json.loads(expect)
            allure.attach(json.dumps(expect, ensure_ascii=False, indent=4), "预期响应", allure.attachment_type.TEXT)

        with allure.step("预期结果与实际响应进行断言操作"):
            logger.info(f'完整的json响应: {res}\n需要校验的数据字典: {really} 预期校验的数据字典: {expect} \n测试结果: {really == expect}')
            logger.debug(f'⬆⬆⬆...用例编号:{case_number},执行完毕,日志查看...⬆⬆⬆\n\n️')
            allure.attach(json.dumps(really == expect, ensure_ascii=False, indent=4), "测试结果",
                          allure.attachment_type.TEXT)
            assert really == expect


if __name__ == '__main__':
    TestApiAuto().run_test()

    # # 使用jenkins集成将不会使用到这两个方法（邮件发送/报告压缩zip）
    # from tools.zip_file import zipDir
    # from tools.send_email import send_email
    # zipDir(report_generate, report_zip)
    # send_email(email_setting)

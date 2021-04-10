#!/usr/bin/env/python3
# -*- coding:utf-8 -*-
"""
@project: apiAutoTest
@author: zy7y
@file: read_data.py
@ide: PyCharm
@time: 2020/7/31
"""
import xlrd   #读取xlsx数据   xlwings可以读取excel数据
from test import logger


class ReadData(object):
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.book = xlrd.open_workbook(self.excel_path)  #根据地址打开之后的对象，类似open as f,这是专门为excel设计的

    def get_data(self):
        """
        :return: data_list - pytest参数化可用的数据
        """
        data_list = []
        table = self.book.sheet_by_index(0)  #打开excel中第一个sheet页  返回表格

        print(type(table))
        print(table.nrows)

        # table.nrows获取table里面行的数量，从0开始算
        for norw in range(1, table.nrows):   #行下标0123，这里抛去第一行文字说明
            # 每行第4列 是否运行
            if table.cell_value(norw, 3) == '否':  # 每行第三列 等于否 将不读取内容，列下标0123....
                continue  # 跳过这行，下一行第三个
            value = table.row_values(norw)  # 获取每行的所有值 是list
            value.pop(3)  # 删除列表中下标为3，即上面判断是否执行的单元格数据

            # 配合将每一行转换成元组存储，方便放入下面的大列表。迎合 pytest的参数化操作，如不需要可以注释掉 value = tuple(value)
            value = tuple(value)  #列表转元组
            logger.info(f'{value}')
            data_list.append(value)  #一行数据的元组 再放入大列表
        return data_list

if __name__ == '__main__':  #没事多调试
    read_data = ReadData('../data/case_data.xlsx')
    result = read_data.get_data()
    print(result)




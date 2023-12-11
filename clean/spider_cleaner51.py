# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/10 12:38
# @Author  : Exisi
# @Version : python3.10.6
# @Desc    : 51job spider data cleaner

import re
import pandas as pd

pd.set_option('display.max_rows', None)


def process_salary_format(salary: str or float):
    """ Salary format to x-x万

    :Arg:
     - salary: salary data
    """
    salary = str(salary)
    if '万/年' in salary:
        pattern = r'(\d+\.\d+|\d+)-(\d+\.\d+|\d+)万/年'
        match = re.search(pattern, salary)
        if match:
            min_salary = round(float(match.group(1)) / 12, 4)
            max_salary = round(float(match.group(2)) / 12, 4)
            return f"{min_salary}-{max_salary}万"
    if '千·' in salary:
        pattern = r'(\d+\.\d+|\d+)-(\d+\.\d+|\d+)千·(\d+)'
        match = re.search(pattern, salary)
        if match:
            min_salary = round(float(match.group(1)) * 0.1 * int(match.group(3)) / 12, 4)
            max_salary = round(float(match.group(2)) * 0.1 * int(match.group(3)) / 12, 4)
            return f"{min_salary}-{max_salary}万"
    if '万·' in salary:
        pattern = r'(\d+\.\d+|\d+)-(\d+\.\d+|\d+)万·(\d+)'
        match = re.search(pattern, salary)
        if match:
            min_salary = round(float(match.group(1)) * int(match.group(3)) / 12, 4)
            max_salary = round(float(match.group(2)) * int(match.group(3)) / 12, 4)
            return f"{min_salary}-{max_salary}万"
    if '千-' in salary:
        pattern = r'(\d+\.\d+|\d+)千-(\d+\.\d+|\d+).*(?:·(\d+))?'
        match = re.search(pattern, salary)
        if match:
            if match.group(3):
                min_salary = round(float(match.group(1)) * 0.1 * int(match.group(3)) / 12, 4)
                max_salary = round(float(match.group(2)) * int(match.group(3)) / 12, 4)
                return f"{min_salary}-{max_salary}万"
            else:
                min_salary = round(float(match.group(1)) * 0.1, 4)
                max_salary = round(float(match.group(2)), 4)
                return f"{min_salary}-{max_salary}万"
    if '元/天' in salary:
        pattern = r'(\d+\.\d+|\d+)元/天'
        match = re.search(pattern, salary)
        if match:
            salary = round(int(match.group(1)) * 365 / 10000 / 12, 4)
            return f"{salary}-{salary}万"

    pattern = r'(\d+\.\d+|\d+)-(\d+\.\d+|\d+)千'
    match = re.search(pattern, salary)
    if match:
        min_salary = round(float(match.group(1)) * 0.1, 1)
        max_salary = round(float(match.group(2)) * 0.1, 1)
        return f"{min_salary}-{max_salary}万"
    return salary


def process_salary(data: pd.DataFrame):
    """ Salary formatting

     Then, split to min and min
     Finally, return data

    :Arg:
     - data: origin data
    """
    data['薪资'] = data['薪资'].apply(process_salary_format)
    data['最大薪资'] = data['薪资'].str.extract(r'(\d+\.\d+|\d+)-(\d+\.\d+|\d+)万', expand=False)[1].astype(float) * 10000
    data['最小薪资'] = data['薪资'].str.extract(r'(\d+\.\d+|\d+)-(\d+\.\d+|\d+)万', expand=False)[0].astype(float) * 10000
    data['最小薪资'].fillna(data['最小薪资'].mode()[0], inplace=True)
    data['最大薪资'].fillna(data['最大薪资'].mode()[0], inplace=True)
    data['最小薪资'] = data['最小薪资'].apply(lambda x: int(x))
    data['最大薪资'] = data['最大薪资'].apply(lambda x: int(x))
    return data


def process_work_year(data: pd.DataFrame):
    """ Work year format to x-x年

    :Arg:
     - data: origin data
    """
    data['工作年限'] = data['工作年限'].replace(['无需经验', '在校生/应届生'], '0')
    data['工作年限'] = data['工作年限'].str.extract(r'(\d+-\d+|\d+)')
    range_values = data['工作年限'].str.extract(r'(\d+)-(\d+)|(\d+)')
    data['最小工作年限'] = range_values[0].fillna(range_values[2])
    data['最大工作年限'] = range_values[1].fillna(range_values[2])
    return data


def process_size(data: pd.DataFrame):
    """ Split company people size to min and max

    :Arg:
     - data: origin data
    """

    data['人数'] = data['人数'].str.extract(r'(\d+-\d+|\d+)')
    range_values = data['人数'].str.extract(r'(\d+)-(\d+)|(\d+)')
    data['最小人数'] = range_values[0].fillna(range_values[2])
    data['最大人数'] = range_values[1].fillna(range_values[2])
    data['最小人数'].fillna(data['最小人数'].mode()[0], inplace=True)
    data['最大人数'].fillna(data['最大人数'].mode()[0], inplace=True)
    return data


def process():
    """ Data process starter """

    data = pd.read_csv('../output/51job.csv')
    data = process_salary(data)
    data = process_work_year(data)
    data = process_size(data)
    data['学位要求'].fillna(data['学位要求'].mode()[0], inplace=True)


if __name__ == '__main__':
    '''
    薪资（散点图）
    学位要求（柱状图，饼图？）
    工作年限（饼图），城市（地图）
    公司规模（柱状图，饼图？）
    公司类型（饼图）
    '''
    process()

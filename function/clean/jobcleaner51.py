# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/10 12:38
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : 51job spider data cleaner

import os
import re
import sqlite3
import pandas as pd
from function.spider import logger

pd.set_option('display.max_rows', None)


class JobCleaner51(object):
    """ This cleaner is based on spider file"""

    def __init__(self):
        self.root = os.path.abspath('..')
        self.CSV_FILE = '51job.csv'
        self.SQLITE_FILE = '51job.db'
        self.ORIGIN_CSV_FILE_PATH = os.path.join(self.root, "output/job/" + self.CSV_FILE)
        self.ORIGIN_SQLITE_FILE_PATH = os.path.join(self.root, "output/job/" + self.SQLITE_FILE)
        self.CSV_FILE_PATH = os.path.join(self.root, "output/clean/" + self.CSV_FILE)
        self.SQLITE_FILE_PATH = os.path.join(self.root, "output/clean/" + self.SQLITE_FILE)
        self.__create_output_dir()

    @staticmethod
    def __create_output_dir():
        """ Create output directory if not exists """

        root = os.path.abspath('..')

        directory = os.path.join(root, "output/clean")
        if not os.path.exists(directory):
            os.makedirs(directory)

    def __process_salary_format(self, salary: str or float):
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

    def __process_salary(self, data: pd.DataFrame):
        """ Salary formatting

         Then, split to min and min
         Finally, return data

        :Arg:
         - data: origin data
        """
        data['salary'] = data['salary'].apply(self.__process_salary_format)
        data['min_salary'] = data['salary'].str.extract(r'(\d+\.\d+|\d+)-(\d+\.\d+|\d+)万', expand=False)[0].astype(
            float) * 10000
        data['max_salary'] = data['salary'].str.extract(r'(\d+\.\d+|\d+)-(\d+\.\d+|\d+)万', expand=False)[1].astype(
            float) * 10000
        data['min_salary'].fillna(data['min_salary'].mode()[0], inplace=True)
        data['max_salary'].fillna(data['max_salary'].mode()[0], inplace=True)
        data['min_salary'] = data['min_salary'].apply(lambda x: int(x))
        data['max_salary'] = data['max_salary'].apply(lambda x: int(x))
        return data

    def __process_work_year(self, data: pd.DataFrame):
        """ Work year format to x-x年

        :Arg:
         - data: origin data
        """
        data['workYear'] = data['workYear'].replace(['无需经验', '在校生/应届生'], '0年')
        return data

    def __process_size(self, data: pd.DataFrame):
        """ Company size value replace

        :Arg:
         - data: origin data
        """
        data['companySize'] = data['companySize'].str.replace('�于50人', '小于50人')
        data['companySize'] = data['companySize'].str.replace('500-1000��', '500-1000以上')
        data['companySize'] = data['companySize'].str.replace('1000-5000��', '1000-5000人')
        data['companySize'] = data['companySize'].str.replace('10000�以上', '10000人以上')
        data['companySize'] = data['companySize'].str.replace('150-500�', '150-500人')
        data['companySize'] = data['companySize'].str.replace('10000人以��', '10000人以上')
        mode_value = data['companySize'].mode()[0]
        data['companySize'] = data['companySize'].fillna(mode_value)
        return data

    def __process_companyType(self, data):
        """ Company type value fill NA

        :Arg:
         - data: origin data
        """
        mode_value = data['companyType'].mode()[0]
        data['companyType'] = data['companyType'].fillna(mode_value)
        return data

    def __process_degree(self, data):
        """ Fill degree data with mode

        :Arg:
         - data: origin data
        """
        data['degree'].fillna(data['degree'].mode()[0], inplace=True)
        return data

    def __process_tags(self, data):
        """ Remove the first two tags

        :Arg:
         - data: origin data
        """
        data['tags'] = data['tags'].str.split(',', n=2).str[2]
        mode_value = data['tags'].mode()[0]
        data['tags'] = data['tags'].fillna(mode_value)
        return data

    def __save_to_csv(self, data: pd.DataFrame, output: str):
        """ Save data to csv

        :Arg:
         - detail: Dictionary of a single data
         - output: Data output path
        """
        data.to_csv(output, index=False, encoding='utf-8')

    def __save_to_db(self, data: pd.DataFrame, output: str):
        """ Save data to sqlite

        :Arg:
         - output: Data output path
        """

        connect = sqlite3.connect(output)
        data.to_sql('job51', connect, if_exists='replace',index=False)
        connect.close()

    def save(self, data: pd.DataFrame, type: str):
        """ Data save

        :Arg:
         - data: origin data
         - save_engine: Data storage engine, support for csv, db and both
        """

        save_to = {
            'csv': lambda x: self.__save_to_csv(x, self.CSV_FILE_PATH),
            'db': lambda x: self.__save_to_db(x, self.SQLITE_FILE_PATH),
        }
        save = save_to[type]
        save(data)

    def process(self, data: pd.DataFrame):
        """ Data process starter

        :Arg:
         - data: origin data
        """
        data = self.__process_salary(data)
        data = self.__process_work_year(data)
        data = self.__process_size(data)
        data = self.__process_degree(data)
        data = self.__process_tags(data)
        data = self.__process_companyType(data)
        data.drop('salary', axis=1, inplace=True)
        data.drop('issueDate', axis=1, inplace=True)
        return data

    def get_origin_data(self):
        sql = 'SELECT * FROM `job51` ;'
        data = {
            'csv': pd.read_csv(self.ORIGIN_CSV_FILE_PATH),
            'db': pd.read_sql(sql, f'sqlite:///{self.ORIGIN_SQLITE_FILE_PATH}'),
        }
        return data


def start(save_engine: str):
    """ cleaner starter

    :Args:
     - save_engine: Data storage engine, support for csv, db and both
    """
    if save_engine not in ['csv', 'db', 'both']:
        return logger.error("The data storage engine must be 'csv' , 'db' or 'both' ")

    cleaner = JobCleaner51()
    data = cleaner.get_origin_data()

    if save_engine == 'both':
        data_csv = cleaner.process(data["csv"])
        cleaner.save(data_csv, "csv")
        data_db = cleaner.process(data["db"])
        cleaner.save(data_db, "db")
    else:
        data = cleaner.process(data[save_engine])
        cleaner.save(data, save_engine)

    logger.close()

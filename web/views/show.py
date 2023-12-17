# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/14 22:33
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$

import os
import math
import sqlite3
from io import BytesIO

import pandas as pd
from flask import Blueprint, render_template, redirect, session, request, send_file, abort

from web.models.result import Result

show = Blueprint('show', __name__)


def login_required(view_func):
    """ Login verification function

    :Arg:
     - view_func: view function
    """

    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')

        return view_func(*args, **kwargs)

    return wrapper


@show.route('/show')
@login_required
def main():
    """ home page """

    return render_template('pages/datashow.html')


@show.route('/api/jobs')
def select():
    """ Get jobs json"""

    data = None
    pageNum = request.args.get('pageNum')
    pageSize = request.args.get('pageSize')
    type = request.args.get('type')

    pageNum = int(pageNum) if pageNum else 1
    pageNum = pageNum if pageNum != 0 else 1
    pageSize = int(pageSize) if pageSize else 15

    start_index = (pageNum - 1) * pageSize
    end_index = start_index + pageSize

    if type == 'csv':
        data = pd.read_csv('../output/clean/51job.csv')

    if type == 'db':
        sql = 'SELECT * FROM `job51` ;'
        data = pd.read_sql(sql, f'sqlite:///{os.path.abspath("..")}/output/clean/51job.db')

    joblist = data[start_index:end_index].to_dict(orient='records')
    total = len(data)
    totalSize = math.ceil(total / pageSize)

    data = {
        'list': joblist,
        'total': total,
        'pageSize': pageSize,
        'totalSize': totalSize,
        'current': pageNum,
        'prev': pageNum - 1 if pageNum - 1 > 0 else None,
        'next': pageNum + 1 if pageNum < totalSize else None
    }

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    response.set_data(data)
    return response.to_json()


@show.route('/api/jobs/export')
def export():
    """ Get jobs json"""

    root = os.path.abspath('..')

    directory = os.path.join(root, "output/export")
    if not os.path.exists(directory):
        os.makedirs(directory)

    data = None
    CSV_PATH = f'{os.path.abspath("..")}/output/clean/51job.csv'
    SQLITE_PAHT = f'{os.path.abspath("..")}/output/clean/51job.db'
    CSV_EXPORT_PATH = f'{os.path.abspath("..")}/output/export/51job.csv'
    EXCEL_EXPORT_PATH = f'{os.path.abspath("..")}/output/export/51job.xlsx'

    source = request.args.get('source')
    type = request.args.get('type')

    if not source or not type:
        abort(400, description='参数异常！')

    if source == 'csv':
        data = pd.read_csv(CSV_PATH)

    if source == 'db':
        sql = 'SELECT * FROM `job51` ;'
        data = pd.read_sql(sql, f'sqlite:///{SQLITE_PAHT}')

    if type == 'csv':
        data.to_csv(CSV_EXPORT_PATH, index=False)
        return send_file(CSV_EXPORT_PATH, as_attachment=True)

    if type == 'excel':
        data.to_excel(EXCEL_EXPORT_PATH, index=False)
        return send_file(EXCEL_EXPORT_PATH, as_attachment=True)


@show.route('/api/jobs/import', methods=["PUT"])
def add():
    """ Add jobs data"""
    root = os.path.abspath('..')
    directory = os.path.join(root, "output/clean")
    CSV_FILE_PATH = os.path.join(directory, '51job.csv')
    SQLITE_FILE_PATH = os.path.join(directory, '51job.db')

    data = request.form
    file_type = data.get('type')
    file_source = data.get('source')
    file = request.files['file']

    if file_type not in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv',
                         'application/vnd.ms-excel']:
        abort(500, "不支持的文件类型")

    types = {
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'excel',
        'application/vnd.ms-excel': 'excel',
        'text/csv': 'csv',
    }

    file_type = types[file_type]
    file_stream = file.stream.read()

    get_data = {
        'csv': lambda x: pd.read_csv(BytesIO(x)),
        'excel': lambda x: pd.read_excel(BytesIO(x))
    }

    data = get_data[file_type](file_stream)

    if file_source == 'csv':
        data.to_csv(CSV_FILE_PATH, index=False, header=False, mode='a', encoding='utf-8')
        df = pd.read_csv(CSV_FILE_PATH, delimiter=',')
        df.drop_duplicates(inplace=True)
        df.to_csv(CSV_FILE_PATH, index=False, encoding='utf-8')

    if file_source == 'db':
        connect = sqlite3.connect(SQLITE_FILE_PATH)
        existing_data = pd.read_sql_query('SELECT * FROM job51', connect)
        data = pd.concat([existing_data, data])
        data = data.drop_duplicates()
        data.to_sql('job51', connect, if_exists='replace', index=False)
        connect.close()

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    return response.to_json()


@show.errorhandler(400)
def handle_400_error(error):
    '''
    400 error handler
    :param error: error param
    :return: request response
    '''
    response = Result()
    response.set_status(0)
    response.set_message(error.description)
    response.set_code(400)
    return response.to_json()


@show.errorhandler(500)
def handle_500_error(error):
    '''
    500 error handler
    :param error: error param
    :return: request response
    '''
    response = Result()
    response.set_status(0)
    response.set_message(error.description)
    response.set_code(500)
    return response.to_json()

# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/14 22:33
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : data show view

import os
import math
import re
import sqlite3
import pandas as pd
from io import BytesIO
from web.models.result import Result
from flask import Blueprint, render_template, redirect, session, request, send_file, abort

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

    return render_template('pages/data_show.html')


@show.route('/api/jobs')
def select():
    """ Get jobs json """

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)

    name = request.args.get('name')
    pageNum = request.args.get('pageNum')
    pageSize = request.args.get('pageSize')
    keyword = request.args.get('keyword')
    dtype = request.args.get('type')

    pageNum = int(pageNum) if pageNum else 1
    pageNum = pageNum if pageNum != 0 else 1
    pageSize = int(pageSize) if pageSize else 15

    start_index = (pageNum - 1) * pageSize
    end_index = start_index + pageSize

    if name not in ['51job']:
        abort(400, description='参数异常！')

    directory = f'{os.path.abspath("..")}/output/clean'
    data = get_data_by_name(name, dtype, directory)

    if data.empty:
        return response.to_json()

    if keyword:
        keywords = keyword.split()
        target = data.astype(str).apply(lambda row: any(re.search(kw, cell) for kw in keywords for cell in row), axis=1)
        data = data[target]

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

    response.set_data(data)
    return response.to_json()


@show.route('/api/jobs/import', methods=["PUT"])
def add():
    """ Add jobs data """

    root = os.path.abspath('..')
    directory = os.path.join(root, "output/clean")

    data = request.form
    name = data.get('name')
    file = request.files['file']
    file_type = data.get('type')
    file_source = data.get('source')

    if name not in ['51job']:
        abort(400, description='参数异常！')

    CSV_FILE_PATH = os.path.join(directory, f'{name}.csv')
    SQLITE_FILE_PATH = os.path.join(directory, f'{name}.db')

    if file_type not in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']:
        abort(500, "不支持的文件类型！")

    types = {
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'excel',
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
        header = False
        if not os.path.exists(CSV_FILE_PATH):
            header = True

        data.to_csv(CSV_FILE_PATH, index=False, header=header, mode='a', encoding='utf-8')
        df = pd.read_csv(CSV_FILE_PATH, delimiter=',')
        df.drop_duplicates(inplace=True)
        df.to_csv(CSV_FILE_PATH, index=False, encoding='utf-8')

    if file_source == 'db':
        table = {
            '51job': 'job51'
        }

        if os.path.exists(SQLITE_FILE_PATH):
            connect = sqlite3.connect(SQLITE_FILE_PATH)
            existing_data = pd.read_sql_query(f'SELECT * FROM {table[name]}', connect)
            data = pd.concat([existing_data, data])
            data = data.drop_duplicates()

        connect = sqlite3.connect(SQLITE_FILE_PATH)
        data.to_sql(table[name], connect, if_exists='replace', index=False)
        connect.close()

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    return response.to_json()


@show.route('/api/jobs', methods=['DELETE'])
def delete():
    """ Add jobs data """

    data = request.get_json()
    name = data.get('name')
    source = data.get('source')

    root = os.path.abspath('..')
    CSV_SOURCE_PATH = os.path.join(root, f'output/clean/{name}.csv')
    SQLITE_SOURCE_PATH = os.path.join(root, f'output/clean/{name}.db')

    flag = {
        'csv': os.path.exists(CSV_SOURCE_PATH),
        'db': os.path.exists(SQLITE_SOURCE_PATH)
    }

    if not flag[source]:
        abort(500, '没有数据可以操作！')

    remove = {
        'csv': lambda: os.remove(CSV_SOURCE_PATH),
        'db': lambda: os.remove(SQLITE_SOURCE_PATH)
    }
    remove = remove[source]
    remove()

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    return response.to_json()


@show.route('/api/jobs/export')
def export():
    """ Get jobs json """

    root = os.path.abspath('..')

    directory = os.path.join(root, "output/export")

    if not os.path.exists(directory):
        os.makedirs(directory)

    name = request.args.get('name')
    dtype = request.args.get('type')
    file_source = request.args.get('source')

    if not file_source or not dtype or name not in ['51job']:
        abort(400, description='参数异常！')

    CSV_DIRECTORY = f'{os.path.abspath("..")}/output/clean'
    SQLITE_DIRECTORY = f'{os.path.abspath("..")}/output/clean'
    CSV_EXPORT_PATH = f'{os.path.abspath("..")}/output/export/51job.csv'
    EXCEL_EXPORT_PATH = f'{os.path.abspath("..")}/output/export/51job.xlsx'

    data = {
        'csv': get_data_by_name(name, file_source, CSV_DIRECTORY),
        'db': get_data_by_name(name, file_source, SQLITE_DIRECTORY),
    }

    data = data[file_source]

    if dtype == 'csv':
        data.to_csv(CSV_EXPORT_PATH, index=False)
        return send_file(CSV_EXPORT_PATH, as_attachment=True)

    if dtype == 'excel':
        data.to_excel(EXCEL_EXPORT_PATH, index=False)
        return send_file(EXCEL_EXPORT_PATH, as_attachment=True)


def get_data_by_name(name: str, dtype: str, directory: str):
    """ Get job data by job name

    :Arg:
     - name: job name
     - dtype: data source name
     - directory: data directory
    """
    data = None

    if not os.path.exists(f'{directory}/{name}.{dtype}'):
        return pd.DataFrame([])

    if dtype == 'csv':
        data = pd.read_csv(f'{directory}/{name}.csv')

    if dtype == 'db':
        table = {
            '51job': 'job51'
        }
        sql = f'SELECT * FROM {table[name]} ;'
        data = pd.read_sql(sql, f'sqlite:///{directory}/{name}.db')

    return data


@show.errorhandler(400)
def handle_400_error(error):
    """ 400 error handler

    :Arg:
     - error: error param
    """
    response = Result()
    response.set_status(0)
    response.set_message(error.description)
    response.set_code(400)
    return response.to_json()


@show.errorhandler(500)
def handle_500_error(error):
    """ 500 error handler

    :Arg:
     - error: error param
    """
    response = Result()
    response.set_status(0)
    response.set_message(error.description)
    response.set_code(500)
    return response.to_json()

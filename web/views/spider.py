# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/17 21:37
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$
import math
import os
import re
import sqlite3
import pandas as pd
from io import BytesIO
from function.spider import jobspider51, logger
from web.models.result import Result
from function.spider.area import areaspider51
from flask import Blueprint, render_template, redirect, session, request, abort, send_file

spider = Blueprint('spider', __name__)


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


@spider.route('/spider')
@login_required
def home():
    """ home page """

    return render_template('pages/data_spider.html')


@spider.route('/api/areas')
def get_area():
    """ get area data """

    data = None
    name = request.args.get('name')
    dtype = request.args.get('type')
    root = os.path.abspath('..')

    path = {
        'csv': os.path.join(root, "output/area/51area.csv"),
        'db': os.path.join(root, "output/area/51area.db")
    }

    path = path[dtype]

    if not os.path.exists(path):
        spider = bind_area_spider(name)
        spider.start(dtype)

    if dtype == 'csv':
        data = pd.read_csv(path, dtype=str)

    if dtype == 'db':
        sql = 'SELECT * FROM `area51` ;'
        data = pd.read_sql(sql, f'sqlite:///{path}')

    data = data.set_index('area')['code'].to_dict()

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    response.set_data(data)
    return response.to_json()


@spider.route('/api/spider/worker')
def get_jobs():
    """ get job data """

    keyword = request.args.get('keyword')
    area = request.args.get('area')
    type = request.args.get('type')
    name = request.args.get('name')

    if not all(request.args.get(key) for key in ['keyword', 'area', 'type', 'name']):
        abort(400, description='参数不能为空！')

    if area == '000000':
        full_spider(name, keyword, type)
    else:
        part_spider(name, keyword, area, type)

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    return response.to_json()


@spider.route('/api/jobs/row')
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

    directory = f'{os.path.abspath("..")}/output/job'
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


@spider.route('/api/jobs/row/import', methods=["PUT"])
def add():
    """ Add jobs data """

    root = os.path.abspath('..')
    directory = os.path.join(root, "output/job")

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


@spider.route('/api/jobs/row', methods=['DELETE'])
def delete():
    """ Add jobs data """

    data = request.get_json()
    name = data.get('name')
    source = data.get('source')

    root = os.path.abspath('..')
    CSV_SOURCE_PATH = os.path.join(root, f'output/job/{name}.csv')
    SQLITE_SOURCE_PATH = os.path.join(root, f'output/job/{name}.db')

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


@spider.route('/api/jobs/row/export')
def export():
    """ Get jobs json"""

    root = os.path.abspath('..')

    directory = os.path.join(root, "output/export")

    if not os.path.exists(directory):
        os.makedirs(directory)

    name = request.args.get('name')
    type = request.args.get('type')
    file_source = request.args.get('source')

    if not file_source or not type or name not in ['51job']:
        abort(400, description='参数异常！')

    CSV_DIRECTORY = f'{os.path.abspath("..")}/output/job'
    SQLITE_DIRECTORY = f'{os.path.abspath("..")}/output/job'
    CSV_EXPORT_PATH = f'{os.path.abspath("..")}/output/export/51job.csv'
    EXCEL_EXPORT_PATH = f'{os.path.abspath("..")}/output/export/51job.xlsx'

    data = {
        'csv': get_data_by_name(name, file_source, CSV_DIRECTORY),
        'db': get_data_by_name(name, file_source, SQLITE_DIRECTORY),
    }

    data = data[file_source]

    if type == 'csv':
        data.to_csv(CSV_EXPORT_PATH, index=False)
        return send_file(CSV_EXPORT_PATH, as_attachment=True)

    if type == 'excel':
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


def bind_area_spider(name: str):
    bindSpider = {
        '51job': areaspider51,
    }

    return bindSpider[name]


def bind_job_spider(name: str):
    bindSpider = {
        '51job': jobspider51,
    }

    return bindSpider[name]


def part_spider(name: str, keyword: str, area: str, type: str):
    spider = bind_job_spider(name)

    param = {
        '51job': {
            "keyword": keyword,
            "pages": 1,
            "pageSize": 1000,
            "area": area
        },
    }
    param = param[name]
    spider.start(param, save_engine=type)


def full_spider(name: str, keyword: str, type: str):
    root = os.path.abspath('..')
    spider = bind_job_spider(name)

    area = {
        '51job': '51area',
    }

    if type == 'csv':
        df = pd.read_csv(f'{root}/output/area/{area[name]}.csv', header=None, names=None, skiprows=1, delimiter=',')

        for area in df[0]:
            param = {
                "keyword": keyword,
                "pages": 1,
                "pageSize": 1000,
                "area": area
            }
            spider.start(args=param, save_engine=type)

    if type == 'db':
        results = None
        connect = sqlite3.connect(f'{root}//output/area/{name}.db')
        cursor = connect.cursor()

        table = {
            'job51': 'area51'
        }

        sql = f'SELECT `code` FROM `{table[name]}`';
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            connect.commit()
        except Exception as e:
            logger.warning("SQL execution failure of SQLite: " + str(e))
        finally:
            cursor.close()
            connect.close()

        for area in results:
            param = {
                "keyword": keyword,
                "pages": 1,
                "pageSize": 1000,
                "area": area[0]
            }
            spider.start(args=param, save_engine=type)


@spider.errorhandler(400)
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


@spider.errorhandler(500)
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

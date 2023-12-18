# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/17 21:37
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$

import os
import sqlite3
import pandas as pd
from function.spider import jobspider51, logger
from web.models.result import Result
from function.spider.area import areaspider51
from flask import Blueprint, render_template, redirect, session, request, abort

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

    return render_template('pages/spider.html')


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

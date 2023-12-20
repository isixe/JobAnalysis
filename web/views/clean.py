# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/19 13:52
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : data clean view

import os
import pandas as pd
from flask import redirect, session, Blueprint, render_template, request, abort

from function.clean import jobcleaner51
from web.models.result import Result

clean = Blueprint('clean', __name__)


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


@clean.route('/clean')
@login_required
def home():
    """ home page """

    return render_template('pages/data_clean.html')


@clean.route('/api/clean')
def selcct():
    name = request.args.get('name')
    dtype = request.args.get('type')

    if not dtype or name not in ['51job']:
        abort(400, description='参数异常！')

    originDir = f'{os.path.abspath("..")}/output/job'

    origin_data = get_data_by_name(name, dtype, originDir)

    if origin_data.empty:
        abort(500, '无可用数据，请先进行爬取')

    cleanDir = f'{os.path.abspath("..")}/output/clean'
    clean_data = get_data_by_name(name, dtype, cleanDir)

    data = {
        'originCount': len(origin_data),
        'currentCount': len(clean_data),
        'cleanCount': len(origin_data) - len(clean_data)
    }

    if clean_data.empty:
        data['cleanCount'] = 0

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    response.set_data(data)
    return response.to_json()


@clean.route('/api/clean', methods=["PUT"])
def add():

    data = request.form
    name = data.get('name')
    dtype = data.get('type')

    if not dtype or name not in ['51job']:
        abort(400, description='参数异常！')

    originDir = f'{os.path.abspath("..")}/output/job'

    origin_data = get_data_by_name(name, dtype, originDir)

    if origin_data.empty:
        abort(500, '无可用数据，请先进行爬取')

    cleaner = bind_job_cleaner(name)
    cleaner.start(save_engine=dtype)

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    return response.to_json()


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


def bind_job_cleaner(name: str):
    """ Binding jobs spider by name """

    bindSpider = {
        '51job': jobcleaner51,
    }

    return bindSpider[name]


@clean.errorhandler(400)
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


@clean.errorhandler(500)
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

# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/14 22:33
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$
import json
import math
import os

import pandas as pd
from flask import Blueprint, render_template, redirect, url_for, session, request, abort

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
def get():
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

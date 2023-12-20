# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/13 13:25
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : home view
import os
import pandas as pd
from flask import Blueprint, render_template, redirect, session, request, abort

from web.models.result import Result

index = Blueprint('index', __name__)


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


@index.route('/')
@login_required
def home():
    """ home page """

    return render_template('index.html')


@index.route('/api/preview')
def get():
    name = request.args.get('name')
    dtype = request.args.get('type')

    if not all(request.args.get(key) for key in ['name', 'type']):
        abort(400, description='参数不能为空！')

    root = os.path.abspath('..')

    directory = os.path.join(root, f'output/job')

    flag = {
        'csv': os.path.exists(os.path.join(directory, f'{name}.csv')),
        'db': os.path.exists(os.path.join(directory, f'{name}.db'))
    }

    if not flag[dtype]:
        abort(500, '没有数据可以操作！')

    data = get_data_by_name(name, dtype, directory)
    data['issueDate'] = pd.to_datetime(data['issueDate'])

    monthlyCounts = data.groupby(data['issueDate'].dt.to_period('M')).size()
    monthlyCounts = monthlyCounts.reset_index()
    monthlyCounts.columns = ['Month', 'Count']
    monthlyCounts['Month'] = monthlyCounts['Month'].dt.strftime('%m').astype(int)

    weeklyCounts = data.groupby(data['issueDate'].dt.dayofweek).size()
    weeklyCounts = weeklyCounts.reset_index()
    weeklyCounts.columns = ['Week', 'Count']

    months = pd.Series(range(1, 13), name='Month')

    monthlyCounts = monthlyCounts.set_index('Month').reindex(months, fill_value=0).reset_index()

    data = {
        'totalCounts': len(data),
        'monthlyCounts': monthlyCounts['Count'].tolist(),
        'weekCounts': weeklyCounts['Count'].tolist(),
        'areaCounts': data['area'].nunique(),
        'companyCounts': data['companyName'].nunique(),
        'companyTypeCounts': data['companyType'].nunique()
    }

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    response.set_data(data)
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

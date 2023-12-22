# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/15 0:15
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : job analysis view

import os
import re
import pandas as pd
from collections import Counter
from web.models.result import Result
from web.utils.matplotlib_drawer import MatplotlibDrawer
from flask import Blueprint, render_template, redirect, session, request, abort

analysis = Blueprint('analysis', __name__)


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


@analysis.route('/analysis')
@login_required
def main():
    """ linear predict page """

    return render_template('pages/analysis.html')


@analysis.route('/api/analysis')
def draw():
    """ Draw job analysis image by matplotlib """

    if not all(request.args.get(key) for key in ['keyword','name', 'type', 'chartype']):
        abort(400, description='参数不能为空！')

    keyword = request.args.get('keyword')
    name = request.args.get('name')
    dtype = request.args.get('type')
    chartype = request.args.get('chartype')

    directory = f'{os.path.abspath("..")}/output/clean'
    data = get_data_by_name(name, dtype, directory)

    if not keyword == '':
        keywords = keyword.split()
        target = data.astype(str).apply(lambda row: any(re.search(kw, cell) for kw in keywords for cell in row), axis=1)
        data = data[target]

    workYearCount = data['workYear'].value_counts()
    workYearCount = dict(sorted(workYearCount.items(), key=lambda x: int(re.findall(r'\d+', x[0])[0])))

    degreeCount = dict(data['degree'].value_counts())

    minSalary = data['min_salary']
    maxSalary = data['max_salary']
    salary = pd.concat([minSalary, maxSalary], axis=0)
    avgMinSalary = int(sum(minSalary) / len(minSalary))
    avgMaxSalary = int(sum(maxSalary) / len(maxSalary))

    companySize = dict(data['companySize'].value_counts())
    companySize.pop('')

    text = data['tags'].str.cat(sep=',')
    wordFrequent = Counter(text.split(','))
    topWordFrequents = '、'.join([item[0] for item in wordFrequent.most_common(3)])

    companyName = dict(data['companyName'].value_counts())
    print(companyName)

    items = {
        'bar': {
            'title': '工作年限柱状图',
            'data': workYearCount,
            'xlabel': '工作年限',
            'ylabel': '招聘数量',
            'legendlabels': ['招聘数量'],
            'issue': f'工作经验为 <b>{max(workYearCount, key=workYearCount.get)}</b> 时，招聘岗位数量最多，优势越大'
        },
        'pie': {
            'title': '学历要求饼状图',
            'data': degreeCount,
            'issue': f'学历为 <b>{max(degreeCount, key=degreeCount.get)}</b> 时，招聘岗位数量最多，优势越大'
        },
        'scatter': {
            'title': '薪资分布散点图',
            'data': salary.tolist(),
            'xlabel': '薪资数量',
            'ylabel': '薪资水平',
            'issue': f'薪资主要分布在 <b>0-{int(max(salary) / 6)}</b> 区间，薪资越低数量月多，薪资越高数量越少'
        },
        'plot': {
            'title': '薪资折线图',
            'data': {
                'minSalary': minSalary.tolist(),
                'maxSalary': maxSalary.tolist()
            },
            'xlabel': '薪资数量',
            'ylabel': '薪资水平',
            'issue': f'以最低薪资为基准，平均薪资为 <b>{avgMinSalary}</b>；以最高薪资为基准，平均薪资为 <b>{avgMaxSalary}</b>'
        },
        'barh': {
            'title': '公司规模条形图',
            'data': companySize,
            'xlabel': '公司规模',
            'ylabel': '公司数量',
            'legendlabels': ['公司数量'],
            'issue': f'公司规模主要分布在 <b>{max(companySize, key=companySize.get)}</b> 区间'
        },
        'wordcloud': {
            'title': '招聘岗位词云图',
            'data': text.replace(',', ' '),
            'issue': f'招聘岗位前三的标签词为 <b>{topWordFrequents}</b>'
        }
    }

    drawer = bind_draw_type(chartype)()

    getCharts = {
        'matplotlib': get_charts_by_matplotlib(drawer, items)
    }

    items = getCharts[chartype]

    response = Result()
    response.set_status(1)
    response.set_message('成功')
    response.set_code(200)
    response.set_data(items)
    return response.to_json()


def get_charts_by_matplotlib(drawer: MatplotlibDrawer, items: dict):
    """ get and draw chart by matplotlib

    :Arg:
     - drawer: MatplotlibDrawer
     - items: response data dict
    """
    chart = items['bar']
    chartdata = chart['data']
    keys = list(chartdata.keys())
    values = list(chartdata.values())
    plt = drawer.bar(keys, values, chart['title'], chart['xlabel'], chart['ylabel'], chart['legendlabels'])
    items['bar']['data'] = drawer.generate_base64(plt)

    chart = items['pie']
    chartdata = chart['data']
    keys = list(chartdata.keys())
    values = list(chartdata.values())
    plt = drawer.pie(values, keys, chart['title'], keys)
    items['pie']['data'] = drawer.generate_base64(plt)

    chart = items['scatter']
    chartdata = chart['data']
    plt = drawer.scatter(chartdata, range(len(chartdata)), chart['title'], chart['xlabel'], chart['ylabel'])
    items['scatter']['data'] = drawer.generate_base64(plt)

    chart = items['plot']
    chartdata = chart['data']
    plt = drawer.plot(chartdata['minSalary'], chartdata['maxSalary'], range(len(chartdata['minSalary'])),
                      chart['title'], chart['xlabel'], chart['ylabel'])
    items['plot']['data'] = drawer.generate_base64(plt)

    chart = items['barh']
    chartdata = chart['data']
    keys = list(chartdata.keys())
    values = list(chartdata.values())
    plt = drawer.barh(keys, values, chart['title'], chart['xlabel'], chart['ylabel'], chart['legendlabels'])
    items['barh']['data'] = drawer.generate_base64(plt)

    chart = items['wordcloud']
    chartdata = chart['data']
    plt = drawer.word_cloud(chartdata, chart['title'])
    items['wordcloud']['data'] = drawer.generate_base64(plt)
    return items


def bind_draw_type(chartype: str):
    """ Binding drawer by type

    :Arg:
     - chartype: drawer type
    """
    drawer = {
        'matplotlib': MatplotlibDrawer,
    }
    drawer = drawer[chartype]
    return drawer


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

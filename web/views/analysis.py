# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/15 0:15
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$

from flask import Blueprint, render_template, redirect, session

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


@analysis.route('/analysis/job51')
@login_required
def job51():
    """ linear predict page """

    return render_template('pages/analysis_job51.html')

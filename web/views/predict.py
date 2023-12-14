# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/14 22:46
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$

from flask import Blueprint, render_template, redirect, session

predict = Blueprint('predict', __name__)


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


@predict.route('/predict/linear')
@login_required
def linear():
    """ linear predict page """

    return render_template('pages/predict_linear.html')

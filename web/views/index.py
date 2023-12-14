# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/13 13:25
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : home view

from flask import Blueprint, render_template, redirect, url_for, session

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

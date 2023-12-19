# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/19 13:52
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$

from flask import redirect, session, Blueprint, render_template

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

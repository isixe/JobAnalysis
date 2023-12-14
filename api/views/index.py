# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/13 13:25
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : home view

from flask import Blueprint, render_template, redirect, url_for, session

index = Blueprint('index', __name__)


@index.route('/')
def home():
    """ home page """

    username = session.get('user')
    if not username:
        return redirect(url_for('auth.sign_in'))
    return render_template('index.html')

# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/13 13:25
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : home view

from flask import Blueprint, render_template, redirect, url_for

index = Blueprint('index', __name__)


@index.route('/')
def home():
    login = None
    if not login:
        return redirect(url_for('index.auth'))
    return render_template('index.html')


@index.route('/login')
def auth():
    return render_template('pages/sign-in.html')

# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/13 23:25
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : login and register view

from functools import wraps
from flask import Blueprint, render_template, request, redirect, abort, session
from web.models.result import Result
from web.models.user import User
from web.utils.database_builder import Database

auth = Blueprint('auth', __name__)


def login_required(view_func):
    """ Login verification function

    :Arg:
     - view_func: view function
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return redirect('/')

        return view_func(*args, **kwargs)

    return wrapper


@auth.route('/login')
@login_required
def sign_in():
    """ Return login page """

    return render_template('pages/sign_in.html')


@auth.route('/register')
@login_required
def sign_up():
    """ Return register page """

    return render_template('pages/sign_up.html')


@auth.route('/api/login', methods=["POST"])
def login():
    db = None
    user = None
    connect = None
    response = Result()
    data = request.get_json()

    if not all(data.get(key) for key in ['username', 'password']):
        abort(400, description='参数不能为空！')
    try:
        db = Database()
        connect = db.connect()
        user = connect.query(User).filter(User.username == data['username']).first()
    except Exception as e:
        connect.rollback()
        abort(500, description=str(e))
    finally:
        connect.close()
        db.close()

    if not user or user.password != data.get('password'):
        abort(400, description='用户名或密码错误！')

    session.update({'user': user.username})
    response.set_message('登录成功')
    response.set_status(1)
    response.set_code(200)
    return response.to_json()


@auth.route('/api/register', methods=["POST"])
def register():
    db = None
    user = None
    connect = None
    response = Result()
    data = request.get_json()

    if not all(data.get(key) for key in ['username', 'password']):
        abort(400, description='参数不能为空！')
    try:
        db = Database()
        connect = db.connect()
        user = connect.query(User).filter(User.username == data['username']).first()
    except Exception as e:
        connect.rollback()
        abort(500, description=str(e))
    finally:
        connect.close()
        db.close()

    if user:
        abort(400, description='用户名已存在！')

    try:
        db = Database()
        connect = db.connect()
        user = User(**data)
        connect.add(user)
        connect.commit()
    except Exception as e:
        connect.rollback()
        abort(500, description=str(e))
    finally:
        connect.close()
        db.close()

    response.set_message('注册成功')
    response.set_status(1)
    response.set_code(200)
    return response.to_json()


@auth.route('/api/logout', methods=["POST"])
def logout():
    session.pop('user')
    response = Result()
    response.set_message('退出成功')
    response.set_status(1)
    response.set_code(200)
    return response.to_json()


@auth.errorhandler(400)
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


@auth.errorhandler(500)
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
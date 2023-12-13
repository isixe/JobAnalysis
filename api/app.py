# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/11/29 11:20
# @Author  : isixe
# @Version : python3.10.6
# @Desc    : $END$

from api import App

app = App(__name__)

if __name__ == '__main__':
    app.debug = True
    app.run()

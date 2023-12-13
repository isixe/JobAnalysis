# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/13 23:25
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$

from api import App

app = App(__name__)

if __name__ == '__main__':
    app.debug = True
    app.run()

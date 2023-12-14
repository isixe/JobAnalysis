# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/13 23:25
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$

from flask import Flask

from api.views.auth import auth
from api.views.index import index


class App(Flask):
    def __init__(self, name):
        super().__init__(name)
        self.static_folder = '../static'
        self.template_folder = '../templates'
        self.secret_key = 'd6635f7540731f615f069b7a99974146daead07b8d26f1ac0fdb663a212193e6'
        self._register_blueprints()

    def _register_blueprints(self):
        self.register_blueprint(index)
        self.register_blueprint(auth)

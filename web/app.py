# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/13 23:25
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : app starter

from flask import Flask

from web.views.auth import auth
from web.views.index import index
from web.views.show import show
from web.views.predict import predict
from web.views.analysis import analysis
from web.views.spider import spider


class App(Flask):
    def __init__(self, name):
        """ Flask init """

        super().__init__(name)
        self.static_folder = '../static'
        self.template_folder = '../templates'
        self.secret_key = 'd6635f7540731f615f069b7a99974146daead07b8d26f1ac0fdb663a212193e6'
        self._register_blueprints()

    def _register_blueprints(self):
        """ add views """

        self.register_blueprint(index)
        self.register_blueprint(auth)
        self.register_blueprint(show)
        self.register_blueprint(predict)
        self.register_blueprint(analysis)
        self.register_blueprint(spider)


if __name__ == '__main__':
    app = App(__name__)
    app.debug = True
    app.run()

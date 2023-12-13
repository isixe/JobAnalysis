import os

from flask import Flask
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

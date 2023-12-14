# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/14 3:22
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : database builder
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models.user import User, Base


class Database():
    """ Database Initialization tool """

    def __init__(self):
        """ Database init """

        self.root = os.path.abspath('..')
        self.url = f'sqlite:///{os.path.join(self.root, "api/identifier.sqlite")}'
        self.engine = create_engine(self.url)
        self.Session = sessionmaker(bind=self.engine)
        self.__initialize_database()
        self.__insert_default_admin_user()

    def __initialize_database(self):
        """ Create database by Base and engine """

        Base.metadata.create_all(self.engine)

    def __insert_default_admin_user(self):
        """ Create user table and insert data """

        session = self.connect()
        admin_user = User(username='admin', password='123456')
        session.add(admin_user)
        session.commit()
        session.close()

    def connect(self):
        """ Database connection """

        return self.Session()

    def close(self):
        """ Database close """

        self.engine.dispose()

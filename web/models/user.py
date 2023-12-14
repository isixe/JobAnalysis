# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/14 3:18
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    username = Column(VARCHAR(20), nullable=False)
    password = Column(VARCHAR(128), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')

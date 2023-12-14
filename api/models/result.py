# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/12/14 3:30
# @Author  : isixe
# @Version : python3.11.2
# @Desc    : $END$
import json


class Result():
    def __init__(self):
        """ Result init """

        self.status = None
        self.message = None
        self.code = None
        self.data = None

    def set_status(self, status: int):
        """ set response status

        :Arg:
         - status: response status code
        """
        self.status = status

    def set_message(self, message: str):
        """ set response message

        :Arg:
         - message: set response message
        """
        self.message = message

    def set_code(self, code: int):
        """ set response code

        :Arg:
         - message: set response message
        """
        self.code = code

    def set_data(self, data: object):
        """ set response data
        :Arg:
         - data: object data
        """
        self.data = data

    def get_status(self):
        """ get response status """

        return self.status

    def get_message(self):
        """ get response message """

        return self.message

    def get_code(self):
        """ get response code """

        return self.code

    def get_data(self):
        """ get response data """
        return self.data

    def to_json(self):
        """ Result convert to json """

        result_dict = {key: value for key, value in vars(self).items() if value is not None}
        result_json = json.dumps(result_dict)
        return result_json

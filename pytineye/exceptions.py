# -*- coding: utf-8 -*-

"""
exceptions.py

Exception class for pytineye.

Copyright (c) 2021 TinEye. All rights reserved worldwide.
"""


class TinEyeAPIError(Exception):
    """Base exception."""

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __repr__(self):
        return "<pytineye.APIError(%i, '%s')>" % (self.code, self.message)

    def __str__(self):
        return """APIError:
                   code    = %s
                   message = %s""" % (
            self.code,
            self.message,
        )


class APIRequestError(Exception):
    """Base exception for APIRequest."""

    pass

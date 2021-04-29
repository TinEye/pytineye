# -*- coding: utf-8 -*-

"""
test_api_request.py

Test APIRequest class.

Copyright (c) 2021 TinEye. All rights reserved worldwide.
"""

import unittest

from pytineye.api_request import APIRequest
from pytineye.exceptions import APIRequestError


class TestAPIRequest(unittest.TestCase):
    """ Test APIRequest class. """

    def setUp(self):
        self.request = APIRequest(
            "https://api.tineye.com/rest/",
            "LCkn,2K7osVwkX95K4Oy",
            "6mm60lsCNIB,FwOWjJqA80QZHh9BMwc-ber4u=t^",
        )

    def tearDown(self):
        pass

    def test_generate_nonce(self):
        """ Test APIRequest._generate_nonce(). """

        allowable_chars = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789-_=.,*^"
        )

        self.assertRaises(
            APIRequestError, lambda: self.request._generate_nonce(nonce_length=-1)
        )
        self.assertRaises(
            APIRequestError, lambda: self.request._generate_nonce(nonce_length=0)
        )
        self.assertRaises(
            APIRequestError, lambda: self.request._generate_nonce(nonce_length=23)
        )

        try:
            self.request._generate_nonce(nonce_length=0)
        except APIRequestError as e:
            self.assertEqual(
                e.args[0], "Nonce length must be an int between 24 and 255 chars"
            )

        try:
            self.request._generate_nonce(nonce_length="character")
        except APIRequestError as e:
            self.assertEqual(
                e.args[0], "Nonce length must be an int between 24 and 255 chars"
            )

        nonce = self.request._generate_nonce(nonce_length=24)
        self.assertEqual(len(nonce), 24)

        for char in nonce:
            self.assertTrue(char in allowable_chars)

        nonce = self.request._generate_nonce(nonce_length=36)
        self.assertEqual(len(nonce), 36)

        for char in nonce:
            self.assertTrue(char in allowable_chars)

    def test_generate_hmac_signature(self):
        """
        Test APIRequest._generate_get_hmac_signature(),
        TestAPIRequest._generate_post_hmac_signature(), and
        TestAPIRequest._generate_hmac_signature().
        """

        signature = self.request._generate_hmac_signature("")
        self.assertEqual(
            signature,
            "70eaf20393eb0605270226d522dfd19d281e64ea513c271c9e6febdd826a5f7c",
        )

        signature = self.request._generate_hmac_signature(" ")
        self.assertEqual(
            signature,
            "5f5f7e12a03ce8ac37ef8e98ac77dad52f0d380752ab4928c9e828949eb4e721",
        )

        signature = self.request._generate_hmac_signature(
            "this is a message to convert"
        )
        self.assertEqual(
            signature,
            "a5cb1334a32b5bb43755393be47aea8182a8557097e0f70803dc85b8d4d18562",
        )

        signature = self.request._generate_hmac_signature(
            "this is another message to convert"
        )
        self.assertEqual(
            signature,
            "ce7c686d266ebeb4e8e9dc1d1cb3d88b72ed8d4f3be41096aa3c397e45ade372",
        )

        nonce = "a_nonce"
        date = 1347910390
        signature = self.request._generate_get_hmac_signature(
            "image_count", nonce, date
        )
        self.assertEqual(
            signature,
            "dfc8b4735ab41c907059b473727bd500645f161398133db1c2ebdf276221d681",
        )

        signature = self.request._generate_get_hmac_signature(
            "remaining_searches", nonce, date, request_params={"param_1": "value"}
        )
        self.assertEqual(
            signature,
            "3b055b83d6e32f1604328306a51ba9b243f52986ba0458a7915d864d00d2f04e",
        )

        boundary = "--boundary!"
        signature = self.request._generate_post_hmac_signature(
            "search", boundary, nonce, date, filename="file"
        )
        self.assertEqual(
            signature,
            "26e789aaaf7e3f0b3c2eea15ba385a1e22da6cf93698ec98ea61627c84e35a5e",
        )

        signature = self.request._generate_post_hmac_signature(
            "search",
            boundary,
            nonce,
            date,
            filename="file",
            request_params={"param_1": "value"},
        )
        self.assertEqual(
            signature,
            "79232caabb7433561142f465cb2e645197bbc5c56a3d3832884d8e24ed128e33",
        )

    def test_sort_params(self):
        """ Test APIRequest._sort_params(). """

        request_params = {}
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(sorted_params, "")

        request_params = {"a_param": "value_1"}
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(sorted_params, "a_param=value_1")

        request_params = {"a_param": "value_1", "b_param": "value_2"}
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(sorted_params, "a_param=value_1&b_param=value_2")

        request_params = {
            "param_1": "value_1",
            "a_param": "value_2",
            "b_param": "value_3",
        }
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(
            sorted_params, "a_param=value_2&b_param=value_3&param_1=value_1"
        )

        request_params = {
            "api_key": "a_key",
            "param_1": "value_1",
            "a_param": "value_2",
            "b_param": "value_3",
        }
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(
            sorted_params, "a_param=value_2&b_param=value_3&param_1=value_1"
        )

        request_params = {
            "api_key": "a_key",
            "param_1": "value_1",
            "api_sig": "a_sig",
            "a_param": "value_2",
        }
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(sorted_params, "a_param=value_2&param_1=value_1")

        request_params = {
            "api_key": "a_key",
            "date": "date",
            "api_sig": "a_sig",
            "nonce": "nonce",
        }
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(sorted_params, "")

        request_params = {"image_url": "valu$_1"}
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(sorted_params, "image_url=valu%24_1")

        request_params = {"image_url": "CAPS!??!?!"}
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(sorted_params, "image_url=caps%21%3f%3f%21%3f%21")

        request_params = {"image_url": "CAPS%21%3f%3f%21%3f%21"}
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(sorted_params, "image_url=caps%2521%253f%253f%2521%253f%2521")

        request_params = {"Image_Url": "CAPS%21%3f%3f%21%3f%21"}
        sorted_params = self.request._sort_params(request_params)
        self.assertEqual(sorted_params, "image_url=caps%2521%253f%253f%2521%253f%2521")

    def test_request_url(self):
        """ Test APIRequest._request_url(). """

        nonce = "a_nonce"
        date = 1345821763

        url = self.request._request_url(
            "search", nonce, date, "api_sig", {"a_param": "value_1"}
        )
        self.assertEqual(
            url,
            (
                "https://api.tineye.com/rest/search/?api_key=LCkn,2K7osVwkX95K4Oy&date=1345821763"
                "&nonce=a_nonce&api_sig=api_sig&a_param=value_1"
            ),
        )

        url = self.request._request_url(
            "search",
            nonce,
            date,
            "api_sig",
            {"param_1": "value_1", "a_param": "value_2", "b_param": "value_3"},
        )
        self.assertEqual(
            url,
            (
                "https://api.tineye.com/rest/search/?api_key=LCkn,2K7osVwkX95K4Oy&date=1345821763"
                "&nonce=a_nonce&api_sig=api_sig&a_param=value_2&b_param=value_3&param_1=value_1"
            ),
        )

        url = self.request._request_url(
            "search", nonce, date, "api_sig", {"image_url": "CAPS?!!?"}
        )
        self.assertEqual(
            url,
            (
                "https://api.tineye.com/rest/search/?api_key=LCkn,2K7osVwkX95K4Oy&date=1345821763"
                "&nonce=a_nonce&api_sig=api_sig&image_url=CAPS%3F%21%21%3F"
            ),
        )

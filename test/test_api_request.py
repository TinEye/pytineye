# -*- coding: utf-8 -*-

"""
test_api_request.py

Test APIRequest class.

Copyright (c) 2016 TinEye. All rights reserved worldwide.
"""

import unittest

from pytineye.api_request import APIRequest
from pytineye.exceptions import APIRequestError


class TestAPIRequest(unittest.TestCase):
    """ Test APIRequest class. """

    def setUp(self):
        self.request = APIRequest(
            'https://api.tineye.com/rest/',
            'LCkn,2K7osVwkX95K4Oy',
            '6mm60lsCNIB,FwOWjJqA80QZHh9BMwc-ber4u=t^')

    def tearDown(self):
        pass

    def test_generate_nonce(self):
        """ Test APIRequest._generate_nonce(). """

        allowable_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789-_=.,*^"

        self.assertRaises(APIRequestError, lambda: self.request._generate_nonce(nonce_length=-1))
        self.assertRaises(APIRequestError, lambda: self.request._generate_nonce(nonce_length=0))
        self.assertRaises(APIRequestError, lambda: self.request._generate_nonce(nonce_length=23))

        try:
            self.request._generate_nonce(nonce_length=0)
        except APIRequestError as e:
            self.assertEquals(e.args[0], 'Nonce length must be an int between 24 and 255 chars')

        try:
            self.request._generate_nonce(nonce_length="character")
        except APIRequestError as e:
            self.assertEquals(e.args[0], 'Nonce length must be an int between 24 and 255 chars')

        nonce = self.request._generate_nonce(nonce_length=24)
        self.assertEquals(len(nonce), 24)

        for char in nonce:
            self.assertTrue(char in allowable_chars)

        nonce = self.request._generate_nonce(nonce_length=36)
        self.assertEquals(len(nonce), 36)

        for char in nonce:
            self.assertTrue(char in allowable_chars)

    def test_generate_hmac_signature(self):
        """
        Test APIRequest._generate_get_hmac_signature(),
        TestAPIRequest._generate_post_hmac_signature(), and
        TestAPIRequest._generate_hmac_signature().
        """

        signature = self.request._generate_hmac_signature('')
        self.assertEquals(signature, '882f24a1cbe144550c79aa37b77cc2fd2ac3cd1c')

        signature = self.request._generate_hmac_signature(' ')
        self.assertEquals(signature, 'e2652d19426f5904635f88fb374043acce49254f')

        signature = self.request._generate_hmac_signature('this is a message to convert')
        self.assertEquals(signature, 'b6ff6b77fc442ac679a2725a5e09d08271e01721')

        signature = self.request._generate_hmac_signature('this is another message to convert')
        self.assertEquals(signature, 'c7ec125f1e07cefd734d9c2f919deb5295a4e5f8')

        nonce = 'a_nonce'
        date = 1347910390
        signature = self.request._generate_get_hmac_signature('image_count', nonce, date)
        self.assertEquals(signature, '8e7bdc3195fce736922d6e622a6c68d8e4b43a55')

        signature = self.request._generate_get_hmac_signature(
            'remaining_searches', nonce, date, request_params={'param_1': 'value'})
        self.assertEquals(signature, '25ea2472cfba2a64b81959f699fdca56537c6eb8')

        boundary = "--boundary!"
        signature = self.request._generate_post_hmac_signature(
            'search', boundary, nonce, date, filename='file')
        self.assertEquals(signature, '7ed0ffdf83e3185d875d87c8b0f9645bfc1becc7')

        signature = self.request._generate_post_hmac_signature(
            'search', boundary, nonce, date, filename='file', request_params={'param_1': 'value'})
        self.assertEquals(signature, '0c661bc12f9319325d542475adcc5d975711597e')

    def test_sort_params(self):
        """ Test APIRequest._sort_params(). """

        request_params = {}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, '')

        request_params = {'a_param': 'value_1'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'a_param=value_1')

        request_params = {'a_param': 'value_1', 'b_param': 'value_2'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'a_param=value_1&b_param=value_2')

        request_params = {'param_1': 'value_1', 'a_param': 'value_2', 'b_param': 'value_3'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'a_param=value_2&b_param=value_3&param_1=value_1')

        request_params = {
            'api_key': 'a_key',
            'param_1': 'value_1',
            'a_param': 'value_2',
            'b_param': 'value_3'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'a_param=value_2&b_param=value_3&param_1=value_1')

        request_params = {
            'api_key': 'a_key',
            'param_1': 'value_1',
            'api_sig': 'a_sig',
            'a_param': 'value_2'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'a_param=value_2&param_1=value_1')

        request_params = {'api_key': 'a_key', 'date': 'date', 'api_sig': 'a_sig', 'nonce': 'nonce'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, '')

        request_params = {'image_url': 'valu$_1'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'image_url=valu%24_1')

        request_params = {'image_url': 'CAPS!??!?!'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'image_url=caps%21%3f%3f%21%3f%21')

        request_params = {'image_url': 'CAPS%21%3f%3f%21%3f%21'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'image_url=caps%21%3f%3f%21%3f%21')

        request_params = {'Image_Url': 'CAPS%21%3f%3f%21%3f%21'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'Image_Url=caps%21%3f%3f%21%3f%21')

    def test_request_url(self):
        """ Test APIRequest._request_url(). """

        nonce = 'a_nonce'
        date = 1345821763

        url = self.request._request_url('search', nonce, date, 'api_sig', {'a_param': 'value_1'})
        self.assertEquals(
            url,
            ('https://api.tineye.com/rest/search/?api_key=LCkn,2K7osVwkX95K4Oy&date=1345821763'
             '&nonce=a_nonce&api_sig=api_sig&a_param=value_1'))

        url = self.request._request_url(
            'search',
            nonce,
            date,
            'api_sig',
            {'param_1': 'value_1', 'a_param': 'value_2', 'b_param': 'value_3'})
        self.assertEquals(
            url,
            ('https://api.tineye.com/rest/search/?api_key=LCkn,2K7osVwkX95K4Oy&date=1345821763'
             '&nonce=a_nonce&api_sig=api_sig&a_param=value_2&b_param=value_3&param_1=value_1'))

        url = self.request._request_url(
            'search',
            nonce, date,
            'api_sig',
            {'image_url': 'CAPS?!!?'})
        self.assertEquals(
            url,
            ('https://api.tineye.com/rest/search/?api_key=LCkn,2K7osVwkX95K4Oy&date=1345821763'
             '&nonce=a_nonce&api_sig=api_sig&image_url=CAPS%3F%21%21%3F'))

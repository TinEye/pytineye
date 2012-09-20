# -*- coding: utf-8 -*-

"""
test_api_request.py

Test APIRequest class.

Copyright (c) 2012 Idee Inc. All rights reserved worldwide.
"""

import time
import unittest

from pytineye.api_request import APIRequest
from pytineye.exceptions import APIRequestError

class TestAPIRequest(unittest.TestCase):
    """ Test APIRequest class. """
    
    def setUp(self):
        self.request = APIRequest('http://api.tineye.com/', 'public_key', 'private_key')

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
        except APIRequestError, e:
            self.assertEquals(e.args[0], 'nonce string must be an int between 24 and 255 chars')

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
        self.assertEquals(signature, '9e53b30cd6c6eb31c276ade9a29dcf5da7fd0f62')

        signature = self.request._generate_hmac_signature(' ')
        self.assertEquals(signature, 'e84c818e22c0db649537f4015ee13efd34044366')

        signature = self.request._generate_hmac_signature('this is a message to convert')
        self.assertEquals(signature, 'b373bc3be782f86d64421f0f3b1b394e9217f61d')

        signature = self.request._generate_hmac_signature('this is another message to convert')
        self.assertEquals(signature, 'fe0bdcae1763be1dd154c9141e03a956c25a068a')

        nonce = 'a_nonce'
        date = 1347910390
        signature = self.request._generate_get_hmac_signature('image_count', nonce, date)
        self.assertEquals(signature, '75acee6ab58785fa04448df232e6f171cd4db819')

        signature = self.request._generate_get_hmac_signature('remaining_searches', nonce, date, request_params={'param_1': 'value'})
        self.assertEquals(signature, '7e6f8ff5c24d10e03d0c962f3d4a7e6df1ade352')

        boundary = "--boundary!"
        signature = self.request._generate_post_hmac_signature('search', boundary, nonce, date, 
                                                               filename='file')
        self.assertEquals(signature, 'caeae30f197efeca6766e546168bc942597dd7a5')

        signature = self.request._generate_post_hmac_signature('search', boundary, nonce, date, 
                                                               filename='file', request_params={'param_1': 'value'})
        self.assertEquals(signature, '0c5f2091631d4ad76207565b0cf9e9daf8e68465')

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

        request_params = {'api_key': 'a_key', 'param_1': 'value_1', 'a_param': 'value_2', 'b_param': 'value_3'}
        sorted_params = self.request._sort_params(request_params)
        self.assertEquals(sorted_params, 'a_param=value_2&b_param=value_3&param_1=value_1')

        request_params = {'api_key': 'a_key', 'param_1': 'value_1', 'api_sig': 'a_sig', 'a_param': 'value_2'}
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

    def test_request_url(self):
        """ Test APIRequest._request_url(). """

        nonce = 'a_nonce'
        date = 1345821763

        url = self.request._request_url('search', nonce, date, 'api_sig', {'a_param': 'value_1'})
        self.assertEquals(url, 'http://api.tineye.com/search/?api_key=public_key&date=1345821763&nonce=a_nonce&api_sig=api_sig&a_param=value_1')

        url = self.request._request_url('search', nonce, date, 'api_sig', {'param_1': 'value_1', 'a_param': 'value_2', 'b_param': 'value_3'})
        self.assertEquals(url, 'http://api.tineye.com/search/?api_key=public_key&date=1345821763&nonce=a_nonce&api_sig=api_sig&a_param=value_2&b_param=value_3&param_1=value_1')

        url = self.request._request_url('search', nonce, date, 'api_sig', {'image_url': 'CAPS?!!?'})
        self.assertEquals(url, 'http://api.tineye.com/search/?api_key=public_key&date=1345821763&nonce=a_nonce&api_sig=api_sig&image_url=caps%3f%21%21%3f')

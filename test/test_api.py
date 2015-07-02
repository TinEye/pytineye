# -*- coding: utf-8 -*-

"""
test_api_request.py

Test TinEyeAPIRequest class.

Copyright (c) 2015 Idée Inc. All rights reserved worldwide.
"""

from datetime import datetime
import unittest

from pytineye.api import Backlink, Match, TinEyeResponse
from pytineye.api import TinEyeAPIRequest


class TestTinEyeAPIRequest(unittest.TestCase):
    """ Test TinEyeAPIRequest class. """

    def setUp(self):
        self.api = TinEyeAPIRequest(
            api_url='https://api.tineye.com/rest/',
            public_key='LCkn,2K7osVwkX95K4Oy',
            private_key='6mm60lsCNIB,FwOWjJqA80QZHh9BMwc-ber4u=t^')

    def tearDown(self):
        pass

    def test_backlink(self):
        """ Test TinEyeAPI.Backlink object. """

        backlink = {'url': 'url', 'crawl_date': '2010-02-19', 'backlink': 'backlink'}
        b = Backlink._from_dict(backlink)
        self.assertEquals(
            repr(b),
            'Backlink(url="url", backlink=backlink, crawl_date=2010-02-19 00:00:00)')
        self.assertEquals(b.url, 'url')
        self.assertEquals(b.crawl_date, datetime(2010, 2, 19, 0, 0))
        self.assertEquals(b.backlink, 'backlink')

        backlink = {'url': 'url', 'crawl_date': '', 'backlink': 'backlink'}
        b = Backlink._from_dict(backlink)
        self.assertEquals(b.url, 'url')
        self.assertEquals(b.crawl_date, datetime(1, 1, 1, 0, 0))
        self.assertEquals(b.backlink, 'backlink')

        backlink = {'url': '', 'crawl_date': '', 'backlink': ''}
        b = Backlink._from_dict(backlink)
        self.assertEquals(b.url, '')
        self.assertEquals(b.crawl_date, datetime(1, 1, 1, 0, 0))
        self.assertEquals(b.backlink, '')

        backlink = {'url': None, 'crawl_date': None, 'backlink': None}
        b = Backlink._from_dict(backlink)
        self.assertEquals(b.url, None)
        self.assertEquals(b.crawl_date, datetime(1, 1, 1, 0, 0))
        self.assertEquals(b.backlink, None)

    def test_match(self):
        """ Test TinEyeAPI.Match object. """

        match = {
            'backlinks': [{'url': 'url', 'crawl_date': '2008-04-27', 'backlink': 'backlink'}],
            'format': 'JPEG', 'overlay': 'overlay', 'height': 297, 'width': 350,
            'image_url': 'image_url', 'filesize': 87918, 'contributor': False,
            'size': 103950, 'query_hash': 'dca08fc6b2ec4b9e04f94a4e29223f6af3dd6555'}
        m = Match._from_dict(match)
        self.assertEquals(repr(m), 'Match(image_url="image_url", width=350, height=297)')
        self.assertEquals(len(m.backlinks), 1)
        self.assertEquals(m.format, 'JPEG')
        self.assertEquals(m.overlay, 'overlay')
        self.assertEquals(m.height, 297)
        self.assertEquals(m.width, 350)
        self.assertEquals(m.image_url, 'image_url')
        self.assertEquals(m.filesize, 87918)
        self.assertEquals(m.contributor, False)
        self.assertEquals(m.size, 103950)

        match = {
            'backlinks': [
                {'url': 'url', 'crawl_date': '2008-04-27', 'backlink': 'backlink'},
                {'url': 'url', 'crawl_date': '2009-04-27', 'backlink': 'backlink'}],
            'format': 'JPEG', 'overlay': 'overlay', 'height': 297, 'width': 350,
            'image_url': 'image_url', 'filesize': 87918, 'contributor': True,
            'size': 103950}
        m = Match._from_dict(match)
        self.assertEquals(len(m.backlinks), 2)
        self.assertEquals(m.format, 'JPEG')
        self.assertEquals(m.overlay, 'overlay')
        self.assertEquals(m.height, 297)
        self.assertEquals(m.width, 350)
        self.assertEquals(m.image_url, 'image_url')
        self.assertEquals(m.filesize, 87918)
        self.assertEquals(m.contributor, True)
        self.assertEquals(m.size, 103950)

        match = {
            'backlinks': [],
            'format': '', 'overlay': '',
            'image_url': 'image_url', 'filesize': 87918, 'contributor': True,
            'size': 103950}
        m = Match._from_dict(match)
        self.assertEquals(len(m.backlinks), 0)
        self.assertEquals(m.format, '')
        self.assertEquals(m.overlay, '')
        self.assertEquals(m.height, None)
        self.assertEquals(m.width, None)
        self.assertEquals(m.image_url, 'image_url')
        self.assertEquals(m.filesize, 87918)
        self.assertEquals(m.contributor, True)
        self.assertEquals(m.size, 103950)

    def test_tineye_response(self):
        """ Test TinEyeAPI.TinEyeResponse object. """

        matches = {
            'results': {
                'matches': [
                    {
                        'backlinks': [],
                        'format': '',
                        'overlay': '',
                        'height': 297,
                        'width': 350,
                        'image_url': '',
                        'filesize': 87918,
                        'contributor': True,
                        'size': 103950
                    }
                ]
            }
        }
        r = TinEyeResponse._from_dict(matches)
        self.assertEquals(
            repr(r),
            'TinEyeResponse(matches="[Match(image_url="", width=350, height=297)]", total_results=0)'),
        self.assertEquals(len(r.matches), 1)
        self.assertEquals(r.matches[0].height, 297)
        self.assertEquals(r.matches[0].width, 350)

        matches = {
            'results': {
                'matches': [
                    {
                        'backlinks': [],
                        'format': '',
                        'overlay': '',
                        'height': 297,
                        'width': 350,
                        'image_url': '',
                        'filesize': 87918,
                        'contributor': True,
                        'size': 103950
                    },
                    {
                        'backlinks': [],
                        'format': '',
                        'overlay': '',
                        'height': 200,
                        'width': 300,
                        'image_url': '',
                        'filesize': 87918,
                        'contributor': True,
                        'size': 103950
                    }
                ]
            }
        }
        r = TinEyeResponse._from_dict(matches)
        self.assertEquals(len(r.matches), 2)
        self.assertEquals(r.matches[1].height, 200)
        self.assertEquals(r.matches[1].width, 300)

        matches = {'results': {'matches': []}}
        r = TinEyeResponse._from_dict(matches)
        self.assertEquals(len(r.matches), 0)

    def test_calls(self):
        """ Test methods with API sandbox. """

        # Test search_url with sandbox
        response = self.api.search_url('http://www.tineye.com/images/meloncat.jpg')
        self.assertEqual(len(response.matches), 100)
        self.assertTrue(response.total_results > 1000)

        response = self.api.search_url('http://www.tineye.com/images/meloncat.jpg', limit=10)
        self.assertEqual(len(response.matches), 10)
        self.assertTrue(response.total_results > 1000)

        # Test search_data with sandbox
        filename = "test/images/meloncat.jpg"
        data = ""
        with open(filename, 'rb') as fp:
            data = fp.read()
        response = self.api.search_data(data)
        self.assertEqual(len(response.matches), 100)
        self.assertTrue(response.total_results > 1000)

        response = self.api.search_data(data, limit=10)
        self.assertEqual(len(response.matches), 10)
        self.assertTrue(response.total_results > 1000)

        # Test remaining_searches with sandbox
        remaining_searches = self.api.remaining_searches()
        self.assertEqual(remaining_searches['remaining_searches'], 5000)
        self.assertTrue('start_date' in remaining_searches)
        self.assertTrue('expire_date' in remaining_searches)
        self.assertTrue(isinstance(remaining_searches['start_date'], datetime))
        self.assertTrue(isinstance(remaining_searches['expire_date'], datetime))

        # Test image_count with sandbox
        image_count = self.api.image_count()
        self.assertTrue(image_count > 10000000000)

    def test_total_results_in_response(self):
        """ Test if TinEyeAPI.TinEyeResponse contains total_results. """

        response = {
            'results': {'total_results': 123, 'matches': []}
        }
        r = TinEyeResponse._from_dict(response)
        self.assertEqual(r.total_results, 123)

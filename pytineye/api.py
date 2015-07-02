# -*- coding: utf-8 -*-

"""
api.py

Python library to ease communication with the TinEye API server.

Copyright (c) 2015 Idée Inc. All rights reserved worldwide.
"""

from datetime import datetime
import httplib
import simplejson
import time

from api_request import APIRequest
from exceptions import TinEyeAPIError

import urllib3


class TinEyeResponse(object):
    """
    Represents a response from the API.

    Attributes:

    - `matches`, a list of Match objects.
    - `total_results`, total number of results.
    """

    def __init__(self, matches, total_results=None):
        self.matches = matches
        self.total_results = total_results or 0

    def __repr__(self):
        return '%s(matches="%s", total_results=%s)' % \
            (self.__class__.__name__, self.matches, self.total_results)

    @staticmethod
    def _from_dict(result_json):
        """
        Takes parsed JSON from the API server and turns it into a
        TinEyeResponse object.

        - `result_json`, the parsed JSON object.

        Returns: a TinEyeResponse object.
        """

        if not isinstance(result_json, dict):
            raise TinEyeAPIError("500", ["Please pass in a dictionary to _from_dict()"])

        matches = []
        if 'results' in result_json:
            results = result_json['results']
            if 'matches' in results:
                for m in results.get('matches'):
                    match = Match._from_dict(m)
                    matches.append(match)
        total_results = results.get('total_results')

        return TinEyeResponse(matches=matches, total_results=total_results)


class Match(object):
    """
    Represents an image match.

    Attributes:

    - `image_url`, link to the result image.
    - `width`, image width in pixels.
    - `height`, image height in pixels.
    - `size`, image area in pixels.
    - `format`, image format.
    - `filesize`, image size in bytes.
    - `overlay`, overlay URL.
    - `backlinks`, a list of Backlink objects pointing to
      the original websites and image URLs.
    - `contributor`, whether this is a TinEye contributor image.
    """

    def __init__(self, image_url, width, height, size, format,
                 filesize, overlay, contributor, backlinks=None):
        self.image_url = image_url
        self.width = width
        self.height = height
        self.size = size
        self.format = format
        self.filesize = filesize
        self.overlay = overlay
        self.backlinks = backlinks
        self.contributor = contributor

    def __repr__(self):
        return '%s(image_url="%s", width=%i, height=%i)' % \
               (self.__class__.__name__, self.image_url, self.width, self.height)

    @staticmethod
    def _from_dict(match_json):
        """
        Takes parsed JSON from the API server and turns it into a
        Match object.

        - `match_json`, the parsed JSON object.

        Returns: a Match object.
        """

        if not isinstance(match_json, dict):
            raise TinEyeAPIError("500", ["Please pass in a dictionary to _from_dict()"])

        backlinks = []
        if 'backlinks' in match_json:
            for b in match_json['backlinks']:
                backlinks.append(Backlink._from_dict(b))
        match = Match(
            image_url=match_json.get('image_url'),
            width=match_json.get('width'),
            height=match_json.get('height'),
            size=match_json.get('size'),
            format=match_json.get('format'),
            filesize=match_json.get('filesize'),
            overlay=match_json.get('overlay'),
            contributor=match_json.get('contributor'),
            backlinks=backlinks)
        return match


class Backlink(object):
    """
    Represents a backlink for an image.

    Attributes:

    - `url`, the image URL to the image.
    - `backlink`, the original website URL.
    - `crawl_date`, the date the image was crawled.
    """

    def __init__(self, url=None, backlink=None, crawl_date=None):
        self.url = url
        self.backlink = backlink
        self.crawl_date = crawl_date

    def __repr__(self):
        return '%s(url="%s", backlink=%s, crawl_date=%s)' % \
               (self.__class__.__name__, self.url, self.backlink, str(self.crawl_date))

    @staticmethod
    def _from_dict(backlink_json):
        """
        Takes parsed JSON from the API server and turns it into a
        Backlink object.

        - `backlink_json`, the parsed JSON object.

        Returns: a Backlink object.
        """

        if not isinstance(backlink_json, dict):
            raise TinEyeAPIError("500", ["Please pass in a dictionary to _from_dict()"])

        crawl_date = datetime.min
        if backlink_json.get('crawl_date'):
            crawl_date = time.strptime(backlink_json.get('crawl_date'), '%Y-%m-%d')
            crawl_date = datetime(*crawl_date[:6])
        return Backlink(
            url=backlink_json.get('url'),
            backlink=backlink_json.get('backlink'),
            crawl_date=crawl_date)


class TinEyeAPIRequest(object):
    """
    Class to ease communication with the TinEye API server.

    Establish a connection to the API:

        >>> from pytineye import TinEyeAPIRequest
        >>> api = TinEyeAPIRequest(
        ...     'https://api.tineye.com/rest/',
        ...     'your_public_key',
        ...     'your_private_key')

    Searching for an image using an image URL:

        >>> api.search_url(url='http://tineye.com/images/meloncat.jpg')
        TinEyeResponse(...)

    Searching for an image using image data:

        >>> fp = open('meloncat.jpg', 'rb')
        >>> data = fp.read()
        >>> api.search_data(data=data)
        TinEyeResponse(...)
        >>> fp.close()

    Getting information about your search bundle:

        >>> api.remaining_searches()
        {'expire_date': datetime.datetime(2012, 9, 28, 11, 11, 31),
         'remaining_searches': 854,
         'start_date': datetime.datetime(2011, 9, 29, 11, 11, 31)}

    Getting an image count:

        >>> api.image_count()
        2180913080

    """

    def __init__(self, api_url='https://api.tineye.com/rest/', public_key=None, private_key=None):
        self.http = urllib3.connection_from_url(api_url)
        self.request = APIRequest(api_url, public_key, private_key)

    def _request(self, method, params=None, image_file=None, **kwargs):
        """
        Send request to API and process results.

        - `method`, API method to call.
        - `params`, dictionary of fields to send to the API call.
        - `image_file`, tuple containing info (filename, data) about image to send.

        Returns: a JSON parsed object.
        """

        # Pass in any extra keyword arguments as parameters to the API call
        if not params:
            params = {}
        params.update(kwargs)

        try:
            obj = None
            response = None

            # If an image file was provided, send a POST request, else send a GET request
            if image_file is None:
                request_string = self.request.get_request(method, params)
                response = self.http.request('GET', request_string)
            else:
                filename = image_file[0]
                request_string, boundary = self.request.post_request(method, filename, params)
                response = self.http.request_encode_body(
                    'POST', request_string,
                    fields={'image_upload': image_file},
                    multipart_boundary=boundary)
            # Parse the JSON into a Python object
            obj = simplejson.loads(response.data)

        except simplejson.decoder.JSONDecodeError, e:
            raise TinEyeAPIError("500", ["Could not decode JSON: %s" % e])
        except Exception, e:
            raise e

        # Check the result of the API call
        if response.status != httplib.OK or obj.get('code') != httplib.OK:
            raise TinEyeAPIError(obj['code'], obj.get('messages'))

        return obj

    def search_url(
            self, url, offset=0, limit=100, sort='score',
            order='desc', **kwargs):
        """
        Perform searches on the TinEye index using an image URL.

        - `url`, the URL of the image that will be searched for, must be urlencoded.
        - `offset`, offset of results from the start, defaults to 0.
        - `limit`, number of results to return, defaults to 100.
        - `sort`, sort results by score, file size (size), or crawl date (crawl_date),
          defaults to descending (desc).
        - `order`, sort results by ascending (asc) or descending criteria.
        - `kwargs`, to pass extra arguments intended for debugging.

        Returns: a TinEye Response object.
        """

        params = {
            'image_url': url,
            'offset': offset,
            'limit': limit,
            'sort': sort,
            'order': order}

        obj = self._request('search', params, **kwargs)

        return TinEyeResponse._from_dict(obj)

    def search_data(
            self, data, offset=0, limit=100,
            sort='score', order='desc', **kwargs):
        """
        Perform searches on the TinEye index using image data.

        - `data`, image data to use for searching.
        - `offset`, offset of results from the start, defaults to 0.
        - `limit`, number of results to return, defaults to 100.
        - `sort`, sort results by score, file size (size), or crawl date (crawl_date),
          defaults to descending (desc).
        - `order`, sort results by ascending (asc) or descending criteria.
        - `kwargs`, to pass extra arguments intended for debugging.

        Returns: a TinEye Response object.
        """

        params = {
            'offset': offset,
            'limit': limit,
            'sort': sort,
            'order': order}

        image_file = ("image.jpg", data)
        obj = self._request('search', params=params, image_file=image_file, **kwargs)

        return TinEyeResponse._from_dict(obj)

    def remaining_searches(self, **kwargs):
        """
        Lists the number of searches you have left in your current active block.

        - `kwargs`, to pass extra arguments intended for debugging.

        Returns: a dictionary with remaining searches, start time and end time of block.
        """

        obj = self._request('remaining_searches', **kwargs)

        results = obj.get('results')

        start_date = time.strptime(results.get('start_date'), '%Y-%m-%d %X UTC')
        start_date = datetime(*start_date[:6])
        expire_date = time.strptime(results.get('expire_date'), '%Y-%m-%d %X UTC')
        expire_date = datetime(*expire_date[:6])

        return {'remaining_searches': results.get('remaining_searches'),
                'start_date': start_date,
                'expire_date': expire_date}

    def image_count(self, **kwargs):
        """
        Lists the number of indexed images on TinEye.

        - `kwargs`, to pass extra arguments intended for debugging.

        Returns: TinEye image count.
        """

        obj = self._request('image_count', **kwargs)
        return obj.get('results')

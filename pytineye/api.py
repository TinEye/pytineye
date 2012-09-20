"""
api.py

Python library to ease communication with the TinEye API server.

Copyright (c) 2012 Idee Inc. All rights reserved worldwide.
"""

import httplib
import simplejson
import time
import urllib3

from api_request import APIRequest
from exceptions import TinEyeAPIError
from datetime import datetime

class TinEyeResponse(object):
    """
    Represents a response from the API.

    Attributes:

    - `matches`, a list of Match objects.
    """

    def __init__(self, matches):
        self.matches = matches

    def __repr__(self):
        return "%s(matches=\"%s\")" % \
               (self.__class__.__name__, self.matches)

    @staticmethod
    def from_dict(r):
        """
        Takes parsed the JSON from the API server and turn it into a
        TinEyeResponse object.

        - `r`, the parsed JSON object.

        Returns: a TinEyeResponse object.
        """
        matches = []
        if 'results' in r:
            results = r['results']
            if 'matches' in results:
                for m in results.get('matches'):
                    match = Match.from_dict(m)
                    matches.append(match)
        return TinEyeResponse(matches)

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
        return "%s(image_url=\"%s\", width=%i, height=%i)" % \
               (self.__class__.__name__, self.image_url, self.width, self.height)

    @staticmethod
    def from_dict(m):
        """
        Takes parsed JSON from the API server and turn it into a
        Match object.

        - `m`, the parsed JSON object.

        Returns: a Match object.
        """
        backlinks = []
        if 'backlinks' in m:
            for b in m['backlinks']:
                backlinks.append(Backlink.from_dict(b))
        match = Match(image_url=m.get('image_url'),
                      width=m.get('width'),
                      height=m.get('height'),
                      size=m.get('size'),
                      format=m.get('format'),
                      filesize=m.get('filesize'),
                      overlay=m.get('overlay'),
                      contributor=m.get('contributor'),
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
        return "%s(url=\"%s\", backlink=%s, crawl_date=%s)" % \
               (self.__class__.__name__, self.url, self.backlink, str(self.crawl_date))

    @staticmethod
    def from_dict(b):
        """
        Takes parsed JSON from the API server and turn it into a
        Backlink object.

        - `b`, the parsed JSON object.

        Returns: a Backlink object.
        """
        crawl_date = datetime.min
        if b.get('crawl_date'):
            crawl_date = time.strptime(b.get('crawl_date'), '%Y-%m-%d')
            crawl_date = datetime(*crawl_date[:6])
        return Backlink(url=b.get('url'), backlink=b.get('backlink'), crawl_date=crawl_date)

class TinEyeAPIRequest(object):
    """
    Class to ease communication with the TinEye API server. 

    Establish a connection to the API:

        >>> from pytineye import TinEyeAPIRequest
        >>> api = TinEyeAPIRequest('http://api.tineye.com/rest/', 'your_public_key', 'your_private_key')

    Searching for an image using an image URL:

        >>> api.search_url(url='http://www.tineye.com/images/meloncat.jpg')
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

    def __init__(self, api_url='http://api.tineye.com/rest/', public_key=None, private_key=None):
        self.http = urllib3.connection_from_url(api_url)
        self.request = APIRequest(api_url, public_key, private_key)

    def _request(self, method, params={}, image_file=None, **kwargs):
        """
        Send request to API and process results.

        - `method`, API method to call.
        - `params`, dictionary of fields to send to the API call.
        - `image_file`, an image to send.

        Returns: a JSON parsed object.
        """

        # Pass in any extra method arguments as parameters to the API call
        params.update(kwargs)

        try:
            obj = None
            repsonse = None

            # If an image file was provided, send a POST request, else send a GET request
            if image_file == None:
                request_string = self.request.get_request(method, params)
                response = self.http.request('GET', request_string)
            else:
                filename = image_file[0]
                request_string, boundary = self.request.post_request(method, filename, params)
                response = self.http.request_encode_body('POST', request_string, 
                                                         fields={'image_upload': image_file},
                                                         multipart_boundary=boundary)

            # Parse the JSON into a Python object
            obj = simplejson.loads(response.data)

        except simplejson.decoder.JSONDecodeError, e:
            raise TinEyeAPIError("500", ["Could not decode JSON: %s" % e])
        except Exception, e:
            raise e

        # Check if the result of the API call
        if response.status != httplib.OK or obj.get('code') != httplib.OK:
            raise TinEyeAPIError(obj['code'], obj.get('messages'))

        return obj

    def search_url(self, url, offset=0, limit=100, sort='score', 
                   order='desc', **kwargs):
        """
        Perform searches on the TinEye index using an image URL.

        - `url`, the URL of the image that will be searched for, must be urlencoded.
        - `offset`, offset of results from the start, defaults to 0.
        - `limit`, quantity of results to return, defaults to 100.
        - `sort`, sort results by score, file size (size), or crawl date (crawl_date), 
          defaults to desc.
        - `order`, sort results by ascending (asc) or descending criteria.

        Returns: a TinEye Response object.
        """

        params = {'image_url': url,
                  'offset': offset,
                  'limit': limit,
                  'sort': sort,
                  'order': order}

        obj = self._request('search', params, **kwargs)

        return TinEyeResponse.from_dict(obj)

    def search_data(self, data, offset=0, limit=100,
                    sort='score', order='desc', **kwargs):
        """
        Perform searches on the TinEye index using image data.

        - `data`, image data to use for searching.
        - `offset`, offset of results from the start, defaults to 0.
        - `limit`, quantity of results to return, defaults to 100.
        - `sort`, sort results by score, file size (size), or crawl date (crawl_date),
          defaults to desc.
        - `order`, sort results by ascending (asc) or descending criteria.

        Returns: a TinEye Response object.
        """

        params = {'offset': str(offset),
                  'limit': limit,
                  'sort': sort,
                  'order': order}

        image_file = ("image.jpg", data)
        obj = self._request('search', params=params, image_file=image_file, **kwargs)

        return TinEyeResponse.from_dict(obj)

    def remaining_searches(self, **kwargs):
        """
        Lists the number of searches you have left in your current active block.

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

        Returns: TinEye image count.
        """

        obj = self._request('image_count', **kwargs)
        return obj.get('results')

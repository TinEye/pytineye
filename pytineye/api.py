# -*- coding: utf-8 -*-

"""
api.py

Python library to ease communication with the TinEye API server.

Copyright (c) 2021 TinEye. All rights reserved worldwide.
"""

import http.client
import json
import time
from datetime import datetime

import certifi
import urllib3

from .exceptions import TinEyeAPIError

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class TinEyeResponse(object):
    """
    Represents a response from the API.

    Attributes:

    - `matches`, a list of Match objects.
    - `stats`, stats for this search.
    """

    def __init__(self, matches, stats):
        self.matches = matches
        self.stats = stats

    def __repr__(self):
        return "%s(matches=%s, stats=%s)" % (
            self.__class__.__name__,
            self.matches,
            self.stats,
        )

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
        stats = {}

        if "results" in result_json:
            results = result_json["results"]
            if "matches" in results:
                for m in results.get("matches"):
                    match = Match._from_dict(m)
                    matches.append(match)
        if "stats" in result_json:
            stats = result_json["stats"]

        return TinEyeResponse(
            matches=matches,
            stats=stats,
        )


class Match(object):
    """
    Represents an image match.

    Attributes:

    - `image_url`, link to the result image.
    - `domain`, domain this result was found on.
    - `score`, a number (0 to 100) that indicates how closely the images match.
    - `width`, image width in pixels.
    - `height`, image height in pixels.
    - `size`, image area in pixels.
    - `format`, image format.
    - `filesize`, image size in bytes.
    - `overlay`, overlay URL.
    - `backlinks`, a list of Backlink objects pointing to
      the original websites and image URLs.
    - `tags`, whether this match belongs to a collection or stock domain.
    """

    def __init__(
        self,
        image_url,
        domain,
        score,
        width,
        height,
        size,
        image_format,
        filesize,
        overlay,
        tags=None,
        backlinks=None,
    ):
        self.image_url = image_url
        self.domain = domain
        self.score = score
        self.width = width
        self.height = height
        self.size = size
        self.format = image_format
        self.filesize = filesize
        self.overlay = overlay
        self.backlinks = backlinks
        if not tags:
            self.tags = []
        else:
            self.tags = tags

    def __repr__(self):
        return '%s(image_url="%s", score=%.2f, width=%i, height=%i)' % (
            self.__class__.__name__,
            self.image_url,
            self.score,
            self.width,
            self.height,
        )

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
        if "backlinks" in match_json:
            for b in match_json["backlinks"]:
                backlinks.append(Backlink._from_dict(b))
        match = Match(
            image_url=match_json.get("image_url"),
            domain=match_json.get("domain"),
            score=match_json.get("score"),
            width=match_json.get("width"),
            height=match_json.get("height"),
            size=match_json.get("size"),
            image_format=match_json.get("format"),
            filesize=match_json.get("filesize"),
            overlay=match_json.get("overlay"),
            tags=match_json.get("tags"),
            backlinks=backlinks,
        )
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
        return '%s(url="%s", backlink="%s", crawl_date=%s)' % (
            self.__class__.__name__,
            self.url,
            self.backlink,
            str(self.crawl_date),
        )

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
        if backlink_json.get("crawl_date"):
            crawl_date = time.strptime(backlink_json.get("crawl_date"), "%Y-%m-%d")
            crawl_date = datetime(*crawl_date[:6])
        return Backlink(
            url=backlink_json.get("url"),
            backlink=backlink_json.get("backlink"),
            crawl_date=crawl_date,
        )


class TinEyeAPIRequest(object):
    """
    Class to ease communication with the TinEye API server.

    Establish a connection to the API:

        >>> from pytineye import TinEyeAPIRequest
        >>> api = TinEyeAPIRequest(
        ...     api_url='https://api.tineye.com/rest/',
        ...     api_key='your_api_key'
        ... )

    Searching for an image using an image URL:

        >>> api.search_url(url='https://tineye.com/images/meloncat.jpg')
        TinEyeResponse(...)

    Searching for an image using image data:

        >>> fp = open('meloncat.jpg', 'rb')
        >>> data = fp.read()
        >>> api.search_data(data=data)
        TinEyeResponse(...)
        >>> fp.close()

    Getting information about your search bundle:

        >>> api.remaining_searches()
        {'bundles': [{'expire_date': datetime.datetime(2023, 3, 9, 14, 9, 12),
           'remaining_searches': 7892,
           'start_date': datetime.datetime(2021, 3, 10, 14, 9, 12)},
          {'expire_date': datetime.datetime(2019, 3, 23, 9, 52, 46),
           'remaining_searches': 50000,
           'start_date': datetime.datetime(2021, 3, 24, 9, 52, 45)}],
         'total_remaining_searches': 57892}

    Getting an image count:

        >>> api.image_count()
        48560880094

    """

    def __init__(
        self,
        api_url="https://api.tineye.com/rest/",
        api_key="",
    ):
        self.http_pool = urllib3.PoolManager(
            cert_reqs="CERT_REQUIRED",
            ca_certs=certifi.where(),
            timeout=urllib3.Timeout(connect=15.0, read=60.0),
        )
        self.api_url = api_url
        self.api_key = api_key

    def _request(self, method, params=None, **kwargs):
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

        headers = {"x-api-key": self.api_key}
        api_url_search = urljoin(self.api_url, "/rest/%s/" % method)

        try:
            obj = None
            response = None

            # If an image file was provided, send a POST request, else send a GET request
            if "image_upload" not in params:
                response = self.http_pool.request(
                    method="GET", url=api_url_search, fields=params, headers=headers
                )
            else:
                response = self.http_pool.request_encode_body(
                    method="POST",
                    url=api_url_search,
                    fields=params,
                    headers=headers,
                )
            # Parse the JSON into a Python object
            obj = json.loads(response.data.decode("utf-8"))

        except ValueError as e:
            raise TinEyeAPIError("500", ["Could not decode JSON: %s" % e])

        # Check the result of the API call
        if response.status != http.client.OK or obj.get("code") != http.client.OK:
            raise TinEyeAPIError(obj["code"], obj.get("messages"))

        return obj

    def search_url(
        self, url, offset=0, limit=100, sort="score", order="desc", **kwargs
    ):
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
            "image_url": url,
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
        }
        obj = self._request("search", params, **kwargs)

        return TinEyeResponse._from_dict(obj)

    def search_data(
        self, data, offset=0, limit=100, sort="score", order="desc", **kwargs
    ):
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
            "image_upload": ("image.jpg", data),
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
        }
        obj = self._request("search", params=params, **kwargs)

        return TinEyeResponse._from_dict(obj)

    def remaining_searches(self, **kwargs):
        """
        Lists the number of searches you have left in your current active block.

        - `kwargs`, to pass extra arguments intended for debugging.

        Returns: a dictionary with remaining searches, start time and end time of block.
        """

        bundle_list = []

        obj = self._request("remaining_searches", **kwargs)

        results = obj.get("results")

        for bundle in results.get("bundles"):

            start_date = time.strptime(bundle.get("start_date"), "%Y-%m-%d %X UTC")
            start_date = datetime(*start_date[:6])
            expire_date = time.strptime(bundle.get("expire_date"), "%Y-%m-%d %X UTC")
            expire_date = datetime(*expire_date[:6])

            bundle_list.append(
                {
                    "remaining_searches": bundle.get("remaining_searches"),
                    "start_date": start_date,
                    "expire_date": expire_date,
                }
            )

        return {
            "bundles": bundle_list,
            "total_remaining_searches": results.get("total_remaining_searches"),
        }

    def image_count(self, **kwargs):
        """
        Lists the number of indexed images on TinEye.

        - `kwargs`, to pass extra arguments intended for debugging.

        Returns: TinEye image count.
        """

        obj = self._request("image_count", **kwargs)
        return obj.get("results")

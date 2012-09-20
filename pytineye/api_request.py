"""
api_request.py

Provides authentication with the TinEye API server.
For more information see https://api.tineye.com/documentation/authentication

Copyright (c) 2012 Idee Inc. All rights reserved worldwide.
"""

import hmac
import hashlib
import mimetools
import sys
import time
import urllib

if sys.version_info < (2, 5):
    import sha

from Crypto.Random import random
from exceptions import APIRequestError

class APIRequest(object):
    """ Class providing authentication with the TinEye API server. """

    # Nonce length
    min_nonce_length = 24
    max_nonce_length = 255
    nonce_allowable_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789-_=.,*^"

    def __init__(self, api_url, public_key, private_key):
        self.api_url = api_url
        self.public_key = public_key
        self.private_key = private_key

    def _generate_nonce(self, nonce_length=24):
        """
        Generate a nonce.

        - `nonce_length`, length of the generated nonce.

        Returns: a nonce.
        """
        if nonce_length < self.min_nonce_length or nonce_length > self.max_nonce_length \
           or not str(nonce_length).isdigit():
            raise APIRequestError("nonce string must be an int between %d and %d chars" % \
                                            (self.min_nonce_length, self.max_nonce_length))

        rand = random.StrongRandom()

        nonce = ""
        for i in range(0, nonce_length):
            nonce += self.nonce_allowable_chars[rand.randint(0, len(self.nonce_allowable_chars) - 1)]

        return nonce

    def _generate_get_hmac_signature(self, method, nonce, date, request_params={}):
        """
        Generate the HMAC signature hash for a GET request.

        - `method`, the API method being called.
        - `nonce`, a nonce.
        - `date`, the date of the request.
        - `request_params`, dictionary of other search parameters.

        Returns: an HMAC signature hash.
        """
        http_verb = "GET"

        param_str = self._sort_params(request_params)
        request_url = '%s%s/' % (self.api_url, method)
        to_sign = self.private_key + http_verb + str(date) + nonce + request_url + param_str

        return self._generate_hmac_signature(to_sign)

    def _generate_post_hmac_signature(self, method, boundary, nonce, date, filename, request_params={}):
        """
        Generate the HMAC signature hash for a POST request.

        - `method`, the API method being called.
        - `boundary`, the HTTP request's boundary string.
        - `nonce`, a nonce.
        - `date`, the date of the request.
        - `filename`, filename of the image being uploaded.
        - `request_params`, dictionary of other search parameters.

        Returns: an HMAC signature hash.
        """

        http_verb = "POST"
        content_type = "multipart/form-data; boundary=%s" % boundary

        param_str = self._sort_params(request_params)
        request_url = '%s%s/' % (self.api_url, method)
        to_sign = self.private_key + http_verb + content_type + urllib.quote_plus(filename).lower() + \
                  str(date) + nonce + request_url + param_str

        return self._generate_hmac_signature(to_sign)

    def _generate_hmac_signature(self, to_sign):
        """
        Generate the HMAC signature hash given a message to sign.

        - `to_sign`, the message to sign.

        Returns: HMAC signature hash.
        """

        signature = ""
		# Standard hashlib only available after Python 2.5
        if sys.version_info >= (2, 5):
            signature = hmac.new(self.private_key, to_sign, hashlib.sha1)
        else:
            signature = hmac.new(self.private_key, to_sign, sha)

        return signature.hexdigest()

    def _sort_params(self, request_params):
        """
        Helper method to sort request parameters.
        If request_params has the image_url parameter it is URL
        encoded and then lowercased.

        - `request_params`, list of extra search parameters.

        Returns: the search parameters in alphabetical order in query
            string params.
        """

        keys = []
        unsorted_params = {}

        for key in request_params.keys():
            # Sort the parameters if they are not part of the following list
            if key.lower() not in ["api_key", "api_sig", "date", "nonce", "image_upload"]:
                # If the parameter is image_url, URL encode the image URL then lowercase it
                if key.lower() == "image_url":
                    value = request_params[key]
                    if "%" not in value:
                        value = urllib.quote_plus(value, "~")
                    unsorted_params[key.lower()] = value.lower()
                else:
                    unsorted_params[key.lower()] = request_params[key]
                keys.append(key)

        keys.sort()
        sorted_pairs = []

        # Return a query string
        for key in keys: 
            sorted_pairs.append("%s=%s" % (key, unsorted_params[key]))

        return "&".join(sorted_pairs)

    def _request_url(self, method, nonce, date, api_signature, request_params):
        """
        Helper method to generate a URL to call given a method,
        a signature and parameters.

        - `method`, the API call to be return.
        - `api_signature`, the signature to be included with the URL.
        - `request_params`, the parameters to be included with the URL.

        Returns: The API URL to send a request to.
        """

        base_url = '%s%s/' % (self.api_url, method)

        request_url = "%s?api_key=%s&date=%s&nonce=%s&api_sig=%s"

        request_url = request_url % (base_url,
                                     self.public_key,
                                     str(date),
                                     nonce,
                                     api_signature)

        # Need to sort all other parameters
        extra_params = self._sort_params(request_params)

        if extra_params != "":
            request_url += "&" + extra_params

        return request_url

    def get_request(self, method, request_params={}):
        """
        Generate an API GET request string.

        - `method`, API method being called.
        - `request_params`, the list of search parameters.

        Returns: a URL to send the search request to including the search parameters.
        """
        # Have to generate a nonce and date to use in generating a POST request signature
        nonce = self._generate_nonce()
        date = int(time.time())

        api_signature = self._generate_get_hmac_signature(method, nonce, date,
                                                          request_params=request_params)

        return self._request_url(method, nonce, date, api_signature, request_params)

    def post_request(self, method, filename, request_params={}):
        """
        Generate an API POST request string for an image upload search.

        The POST request string can be sent as is to issue the POST
        request to the API server.

        - `method`, API method being called.
        - `filename`, the filename of the image that is being searched for.
        - `request_params`, the list of search parameters.

        Returns:

        - `request_url`, the URL to send the search to.
        - `boundary`, the boundary to be used in the POST request.
        """
        if filename is None or len(str(filename).strip()) == 0:
            raise APIRequestError("Must specify an image to search for.")

        # Have to generate a boundary, nonce, and date to use in generating a POST request signature
        boundary = mimetools.choose_boundary()
        nonce = self._generate_nonce()
        date = int(time.time())

        api_signature = self._generate_post_hmac_signature("search", boundary, nonce, date, filename,
                                                           request_params=request_params)

        return self._request_url(method, nonce, date, api_signature, request_params), boundary

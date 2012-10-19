# -*- coding: utf-8 -*-
# Copyright 2010-2012 Internap Network Services Corporation and Mochila
# Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import simplejson
import urllib
import urllib2
import datetime
import hashlib
import base64
import gzip
import StringIO

try:
    import xml.etree.ElementTree as etree
except:
    from lxml import etree

from hapi.dictobject import DictObject

ENDPOINT = "http://api.voxel.net/version/1.0"
SSLENDPOINT = "https://api.voxel.net/version/1.0"

'''
This is a client library for Voxel's hAPI interface to
their infrastructure.

It aims to be Pythonesque in its usage, allowing you to
access hAPI as if it were a Python library, thus:

1==
hAPI = hapi.Client("<MYKEY>", "<MYSECRET>")
print hAPI.voxel.devices.list( device_id = "12542")
print hAPI.voxel.voxcloud.status(device_id = "12542")

2==
hAPI = hapi.Client()
hAPI.authenticate("<MYID>", "<MYPASSWORD>")
print hAPI.voxel.devices.list( device_id = "12542")
print hAPI.voxel.voxcloud.status(device_id = "12542")

Thus, this client will continue to work if new methods are
added to hAPI.

By default, results are converted from XML to DictObject objects. See
the documentation for DictObject for more details.

You can also retrieve the raw XML output  (see set_xmlout)

'''


class Client:
    __endpoint = ENDPOINT
    __username = None
    __password = None
    __compression = True
    __xmlout = False
    __headers = None

    def __init__(self, key=None, secret=None, ssl=False):
        self.methodparts = []
        self.key = key
        self.secret = secret
        if(ssl == True):
            __endpoint = SSLENDPOINT

    def set_xmlout(self, xmlout):
        self.methodparts = []
        self.__xmlout = xmlout

    def set_endpoint(self, endpoint):
        self.methodparts = []
        self.__endpoint = endpoint

    def set_compression(self, enable=True):
        self.methodparts = []
        self.__compression = enable

    def set_headers(self, headers):
        self.__headers = headers

    def get_headers(self):
        return self.__headers

    def get_compression(self):
        self.methodparts = []
        return self.__compression

    def __get_secure_endpoint(self):
        if(len(self.__endpoint) < 7):
            raise hAPIException("endpoint too short, should be something like http://api.voxel.net")
        authEndpoint = None
        trim = 0
        if(self.__endpoint[:7] == "http://"):
            trim = 7
        elif(self.__endpoint[:8] == "https://"):
            trim = 8
        return ("https://" + self.__endpoint[trim:])

    def reset_password(self, user, email):
        self.__user = user
        authEndpoint = self.__get_secure_endpoint()
        params = {'method': 'voxel.hapi.users.reset_password',
                   'format': 'xml',
                   'username': user,
                   'email': email}

        #we do not want compression in this case
        resp = self.__call_hapi_basic(authEndpoint, params, False)
        return resp

    def authenticate(self, user, password):
        self.__username = user
        self.__password = password
        self.methodparts = []

        authEndpoint = self.__get_secure_endpoint()
        params = {'method': 'voxel.hapi.authkeys.read', 'format': 'xml'}

        userpass = base64.encodestring("%s:%s" % (self.__username, self.__password))[:-1]
        header = ('Authorization', 'Basic ' + userpass)

        #we do not want compression in this case
        response = self.__call_hapi_basic(authEndpoint, params, False, header)
        xml = etree.fromstring(response)
        status = xml.attrib["stat"]

        if status == "ok":
            dict = DictObject(xml=xml)
            self.key = dict.authkey['key']
            self.secret = dict.authkey['secret']
            return dict
        elif status == "fail":
            code = xml.find("err").attrib["code"]
            msg = xml.find("err").attrib["msg"]
            raise Exception("Error %s: %s" % (code, msg))
        else:
            raise Exception("Invalid XML: %s" % response)

    def __call_hapi_basic(self, endPoint, params, compression, header=None):
        self.methodparts = []
        url = endPoint + "?%s" % urllib.urlencode(params)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Voxel hAPI Python Client2; $Revision: 5990 $')

        if(compression == True):
            req.add_header('Accept-Encoding', 'gzip,deflate')

        if(header != None):
            req.add_header(header[0], header[1])

        resource = urllib2.urlopen(req)

        return self.__decode_content(resource)

    def __getattr__(self, name):
        self.methodparts.append(name)
        return self

    '''
    This method checks if the data is compressed using gzip.
    If so then the data is uncompressed and returned.
    '''
    def __decode_content(self, http_resource):
        self.methodparts = []
        headers = http_resource.info()
        self.set_headers(headers)
        #print(headers)
        if(headers.get('Content-Encoding') == 'gzip'):
            #print "Compressed data"
            data = StringIO.StringIO(http_resource.read())
            return gzip.GzipFile(fileobj=data).read()
        else:
            return http_resource.read()

    def __call__(self, ** params):
        method = ".".join(self.methodparts)
        self.methodparts = []
        if ("method" in params and len(method)):
            params["method"] = method + '.' + params["method"]
        elif (len(method)):
            params["method"] = method

        params["key"] = self.key
        params["timestamp"] = datetime.datetime.utcnow().isoformat() + "+0000"
        keys = params.keys()
        keys.sort()

        md5 = hashlib.md5()
        md5.update(self.secret)
        for key in keys:
            if params[key]:
                if not params[key] is None:
                    md5.update("%s%s" % (key, params[key]))
                else:
                    md5.update(key)
        params['api_sig'] = md5.hexdigest()

        data = self.__call_hapi_basic(self.__endpoint, params, True)
        if self.__xmlout:
            return data
        else:
            xml = etree.fromstring(data)
            status = xml.attrib["stat"]
            if status == "ok":
                return DictObject(xml=xml)
            elif status == "fail":
                code = xml.find("err").attrib["code"]
                msg = xml.find("err").attrib["msg"]
                raise Exception("Error %s: %s" % (code, msg))
            else:
                raise Exception("Invalid XML: %s" % data)

    def id_from_label(self, label):
        result = self.voxel.devices.list()

        for device in result.devices.device:
            if device.label == label or device.label.startswith(label + "."):
                return device.id
        raise Exception("No device found with label %s" % label)

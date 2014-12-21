# Copyright (c) 2014 Julian Paul Glass. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

class _Exceptions(Exception):
    def __init__(self):
        self._message = None
        self._template = None

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        if sys.version < 3:
            self._message = value.encode('utf-8')
        else:
            self._message = value

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        if sys.version < 3:
            self._template = value.encode('utf-8')
        else:
            self._template = value

class GoogleAPIError(_Exceptions):
    def __init__(self, APIName, json):
        _Exceptions.__init__(self)
        self.template = '({0}) {1}: {2}: {3}'
        self.message = self.template.format(APIName, json['error']['code'],
            json['error']['message'], json['error']['errors'][0]['reason'])

    def __str__(self):
        return repr(self.message)

class APIError(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return repr(self.message)

class CSEAPIError(APIError):
    pass


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

class GoogleAPIError(Exception):
    def __init__(self, json):
        self.message = json['error']['message']
        self.code = json['error']['code']
        self.reason = json['error']['errors'][0]['reason']
    def __str__(self):
        return repr(' '+str(self.code)+': '.join((self.message, self.reason)))

def evalErrors(apiname, response):
    if response.status_code >= 400:
        raise GoogleAPIError(response.json())

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

import json

from .exceptions import evalErrors
from .utils import ItemIndexTree

try:
    import requests
except:
    raise ImportError('Please install the requests package')

class Items(ItemIndexTree):
    """Request Page Item instance."""
    def __init__(self, data=None, items=None):
        super(Items, self).__init__()
        self.data = data
        if isinstance(items, list):
            for d in items:
                self.append(Items(data=d))

    def __repr__(self):
        if self.parent is None:
            return 'ROOT ItemIndex Current Item: '+self.current.__repr__()
        else:
            return '\"{0}\"'.format(self.title)

    def next(self):
        super(Items, self).next()
        return self.current

    def previous(self):
        super(Items, self).previous()
        return self.current

    @property
    def title(self):
        if self.parent is None:
            return self.current.data['title']
        return self.data['title']

    @property
    def link(self):
        if self.parent is None:
            return self.current.data['link']
        return self.data['link']

    @property
    def snippet(self):
        if self.parent is None:
            return self.current.data['snippet']
        return self.data['snippet']

class Pages(ItemIndexTree):
    """Request Page instance."""
    def __init__(self, data=None):
        super(Pages, self).__init__()
        if data:
            self.data = data['queries']['request'][0]
            self.items = Items(items=data['items'])
        else:
            self.data = None
            self.items = None

    def __repr__(self):
        if self.parent is None:
            return 'ROOT ItemIndex Current Item: '+self.current.__repr__()
        else:
            return '\"{0}\" startIndex: {1}'.format(self.title,
                str(self.startIndex))
    
    def next(self):
        super(Pages, self).next()
        return self.current

    def previous(self):
        super(Pages, self).previous()
        return self.current

    @property
    def startIndex(self):
        if self.parent is None:
            return self.current.data['startIndex']
        return self.data['startIndex']
    
    @property
    def title(self):
        if self.parent is None:
            return self.current.data['title']
        return self.data['title']

    @property
    def count(self):
        if self.parent is None:
            return self.current.data['count']
        return self.data['count']
        
class API(dict):
    """API management class."""
    def __init__(self, apiKey):
        self.setAPIkey(apiKey)
    def setAPIkey(self, apiKey):
        if apiKey is None:
            raise InvalidAPI('API key is cannot be None.')
        self['key'] = apiKey
    def valdiate(self):
        pass
         
class CSE(API):
    """Custom Search Engine."""
    url = 'https://www.googleapis.com/customsearch/v1'
    def __init__(self, api_key, engineID, query, opts):
        super(CSE, self).__init__(api_key)
        self.setEngine(engineID)
        self['q'] = query
        self.pages = Pages()
        self.response = None
        self._test_feed = None

    def setEngine(self, engineID):
        if engineID is None:
            raise InvalidCSEngine('Engine ID cannot be None.')
        self['cx'] = engineID

    @property
    def start(self):
        return self.get('start')

    def next(self):
        if not self.pages:
            self._execute()
        else:
            try:
                self.pages.next()
            except:
                self['start'] = self.pages.current.startIndex + self.pages.current.count
                self._execute()
                self.pages.next()
            
        return self.pages.current

    def previous(self):
        self.pages.previous()
        self['start'] = self.pages.current.startIndex
        return self.pages.current

    def _execute(self):
        if self._test_feed:
            self.pages.append(Pages(json.loads(self._test_feed)))
            self._test_feed = None
            return
        response = requests.get(self.url, params=self)
        if response.status_code == 200:
            self.response = response
            self.pages.append(Pages(self.response.json()))
            with open('sample.json', 'w') as f:
                f.write(self.response.content)
        else:
            return evalErrors('CSE', response)

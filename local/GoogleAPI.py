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
import json
import HTMLParser
import urlparse

from .exceptions import *
from .utils import ItemIndexTree

try:
    import requests
except:
    raise ImportError('Please install the requests package')

htmlparser = HTMLParser.HTMLParser()

def recode(s):
    if sys.version_info[0] < 2:
        return s.encode()
    return s

def reformat(s):
    return recode(htmlparser.unescape(urlparse.unquote(s)))

def searchEngine(engine, query, params, **kwargs):
    if engine == 'cse':
        cls = CSE
    else:
        cls = Legacy
    return cls(query, params, **kwargs)


class BaseItems(ItemIndexTree):
    """Base Items Class."""
    def __init__(self, data=None, items=None):
        ItemIndexTree.__init__(self)
        self.data = data
        if isinstance(items, list):
            for d in items:
                self.append(self.__class__(data=d))
        self._title = None
        self._link = None
        self._snippet = None
    
    def __repr__(self):
        if self.parent is None:
            return recode('ROOT ItemIndex Current Item: ')+self.current.__repr__()
        else:
            return recode('\"{0}\"').format(self.title)
    
    def next(self):
        super(BaseItems, self).next()
        return self.current

    def previous(self):
        super(BaseItems, self).previous()
        return self.current
    
    @property
    def title(self):
        if self.parent is None:
            return reformat(self.current.data[self._title])
        return reformat(self.data[self._title])

    @property
    def link(self):
        if self.parent is None:
            return reformat(self.current.data[self._link])
        return reformat(self.data[self._link])

    @property
    def snippet(self):
        if self.parent is None:
            return reformat(self.current.data[self._snippet])
        return reformat(self.data[self._snippet])


class LegacyItems(BaseItems):
    """Legacy Item Class."""
    def __init__(self, data=None, items=None):
        super(LegacyItems, self).__init__(data=data, items=items)
        self._link = 'url'
        self._title = 'titleNoFormatting'
        self._snippet = 'content'


class CSEItems(BaseItems):
    """Request Page Item instance."""
    def __init__(self, data=None, items=None):
        super(CSEItems, self).__init__(data=data, items=items)
        self._link = 'link'
        self._title = 'title'
        self._snippet = 'snippet'


class BasePages(ItemIndexTree):
    """Base class for Pages."""
    def __init__(self):
        super(BasePages, self).__init__()
        self.data = None
        self.items = None
    
    def __repr__(self):
        if self.parent is None:
            return 'ROOT ItemIndex Current Item: '+self.current.__repr__()
        else:
            return '\"{0}\" startIndex: {1}'.format(self.title,
                str(self.startIndex))
    
    @property
    def currentItem(self):
        return self.items.current
    
    def next(self):
        super(BasePages, self).next()
        return self.current

    def previous(self):
        super(BasePages, self).previous()
        return self.current

    def nextItem(self):
        return self.items.next()

    def previousItem(self):
        return self.items.previous()
    
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


class LegacyPages(BasePages):
    """Legacy Page instances."""
    ItemsClass = LegacyItems

    def __init__(self, data=None):
        super(LegacyPages, self).__init__()
        if data:
            self.data = data['responseData']
            self.items = self.ItemsClass(items=data['responseData']['results'])
            cpi = self.data['cursor']['currentPageIndex']
            if cpi > 0:
                self.data['startIndex'] = cpi * len(self.items)
            else:
                self.data['startIndex'] = cpi
            self.data['title'] = 'Legacy API Search Results'
            self.data['count'] = len(self.items)
    

class CSEPages(BasePages):
    """Request Page instances."""
    ItemsClass = CSEItems
    def __init__(self, data=None):
        super(CSEPages, self).__init__()
        if data:
            self.data = data['queries']['request'][0]
            self.items = self.ItemsClass(items=data['items'])


class API(object):
    """API management class."""
    def __init__(self, **kwargs):
        if not kwargs.get('api_key'):
            raise APIError('API key required.')
        self.value = self.validate(kwargs['api_key'])
    def __call__(self):
        return self.value
    
    def validate(self, value):
        if False:
            raise APIError('API Key Invalid')
        return value


class EngineBase(dict):
    """Base Engine class."""
    url = None
    _test_feed = False

    def __init__(self, query, params, **kwargs):
        self['q'] = query
        self.pages = None
        self.response = None
        try:
            self.maxPages = params.pop('maxPages')
        except:
            self.maxPages = 1

    def next(self):
        if not self.pages:
            self._execute()
            self.pages.next()
        else:
            try:
                if self.maxPages > len(self.pages) and self.maxPages != 0:
                    self['start'] = self.pages.current.startIndex + \
                        self.pages.current.count
                    self._execute()
            finally:
                self.pages.next()

        return self.pages.current
    
    def previous(self):
        self.pages.previous()
        self['start'] = self.pages.current.startIndex
        return self.pages.current
    
    @property
    def currentPage(self):
        return self.pages.current

    def _execute(self):
        if self._test_feed:
            self._test_feed = False
        else:
            response = requests.get(self.url, params=self)
            self.response = response
        if self.eval_status_code(self.response) == 200:
            self.pages.append(self.Pages(self.response.json()))
        else:
            raise GoogleAPIError(self.__class__, self.response)


class Legacy(EngineBase):
    """Legacy Search Engine."""
    Pages = LegacyPages
    url = 'http://ajax.googleapis.com/ajax/services/search/web'

    def __init__(self, query, params, **kwargs):
        super(Legacy, self).__init__(query, params, **kwargs)
        self['v'] = '1.0'
        self.setNumber(params.get('number'))
        self.pages = self.Pages()

    def setNumber(self, n):
        if type(n) is not int:
            return
        if n > 8: #max limit
            n = 8
        self['rsz'] = n

    def eval_status_code(self, response):
        return response.json()['responseStatus']


class CSE(EngineBase):
    """Google Custom Search Engine."""
    Pages = CSEPages
    url = 'https://www.googleapis.com/customsearch/v1'

    def __init__(self, query, params, **kwargs):
        super(CSE, self).__init__(query, params, **kwargs)
        self['key'] = API(**kwargs)()
        try:
            self.setEngine(kwargs.pop('engine_id'))
        except:
            self.setEngine(None)
        
        self.setNumber(params.get('number'))
        self.pages = self.Pages()

    def setEngine(self, engine_id):
        if engine_id is None:
            raise CSEAPIError('Engine ID cannot be None.')
        self['cx'] = engine_id

    def setNumber(self, n):
        if type(n) == int:
            self['num'] = n

    def eval_status_code(self, response):
        return response.status_code

# vim:set ts=4 sw=4 et tw=79:

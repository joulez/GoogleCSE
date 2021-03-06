import sys
import unittest
import json
from .GoogleAPI import CSE, Legacy
from .exceptions import *

def recode(s):
    if sys.version_info[0] < 3:
        s = s.encode()
    return s


class DResponse(object):
    def __init__(self, data):
        self._json = data
    def json(self):
        return self._json


class TestCSE(unittest.TestCase):
    def setUp(self):
        q = 'python docs'
        opts = {'number': 1} 
        self.engine = CSE(q, opts, api_key='testkey', engine_id='TestEngine')

    def testGoogleAPIErrors(self):
        with open('sample400Error.json', 'r') as f:
            j = json.loads(f.read())
               
        self.engine._test_feed = True
        self.engine.response = DResponse(j[0])
        self.engine.response.status_code = \
                self.engine.response._json['error']['code']
        self.assertRaisesRegexp(GoogleAPIError, '\(CSE\) 400:.*: keyInvalid',
                self.engine.next)
        self.engine._test_feed = True
        self.engine.response = DResponse(j[1])
        self.engine.response.status_code = \
                self.engine.response._json['error']['code']
        self.assertRaisesRegexp(GoogleAPIError, '\(CSE\) 400:.*$',
                self.engine.next)
        
        self.engine._test_feed = True
        self.engine.response = DResponse(j[2])
        self.engine.response.status_code = \
                self.engine.response._json['error']['code']
        self.assertRaisesRegexp(GoogleAPIError, '\(CSE\) 500:.*$',
                self.engine.next)

        self.engine._test_feed = True
        self.engine.response = DResponse(j[3])
        self.engine.response.status_code = \
                self.engine.response._json['error']['code']
        self.assertRaisesRegexp(GoogleAPIError, '\(CSE\) 403:.*',
                self.engine.next)

    def testCSENoResults(self):
        self.engine = CSE('python docs', {'number': 1}, api_key='testkey', 
                engine_id='TestEngine')
        with open('sampleNoResults.json', 'r') as f:
            j = json.loads(f.read())

        self.engine._test_feed = True
        self.engine.response = DResponse(j)
        self.engine.response.status_code = 200
        page = self.engine.next()
        self.assertEqual(page.count, 0)

    def test01Pages(self):
        self.engine.maxPages = 2
        with open('sampleResultsP1.json') as f:
            j = json.loads(f.read())
        
        def feed():
            self.engine._test_feed = True
            self.engine.response = DResponse(j)
            self.engine.response.status_code = 200
        feed()
        page = self.engine.next()
        self.assertEqual(page.title, 
                recode('Google Custom Search - python docs'))
        self.assertEqual(len(self.engine.pages), 1)
        self.assertEqual(len(page.items), 10)

        with open('sampleResultsP2.json') as f:
            j = json.loads(f.read())

        feed()
        self.engine.next()
        self.assertEqual(len(self.engine.pages), 2)
        self.assertEqual(self.engine.currentPage.startIndex, 11)
        self.engine.previous()
        self.assertEqual(self.engine.currentPage.startIndex, 1)
        self.engine.next()
        self.assertRaises(IndexError, self.engine.next)
        self.engine.previous()
        self.assertRaises(IndexError, self.engine.previous)
        self.assertEqual(self.engine.currentPage.startIndex, 1)

        ##Item tests
        page = self.engine.currentPage
        item = page.nextItem()
        self.assertRegexpMatches(item.title,
            recode('Overview.*Python.*documentation'))
        item = page.nextItem()
        self.assertRegexpMatches(item.title,
            recode('Our.*Python\.org'))
        item = page.previousItem()
        self.assertRegexpMatches(item.title,
            recode('Overview.*Python.*documentation'))
        self.assertRaises(IndexError, page.previousItem)

        #next page
        page = self.engine.next()
        item = page.nextItem()
        self.assertRegexpMatches(item.title,
            recode('Python\sRuntime\sEnvironment.*Google\sCloud\sPlatform'))

        #previous page
        page = self.engine.previous()
        item = page.currentItem
        self.assertRegexpMatches(item.title,
            recode('Overview.*Python.*documentation'))

    def testLegacyErrors(self):
        with open('sampleLegacyError.json', 'r') as f:
            j = json.loads(f.read())
        q = 'python docs'
        opts={'start': 0}
        self.engine = Legacy(q, opts)
        self.engine._test_feed = True
        self.engine.response = DResponse(j)
        self.engine.response.status_code = 200
        self.assertRaisesRegexp(GoogleAPIError, '\(Legacy\)\s400:\sinvalid\s'
                'resultSize', self.engine.next)

    def testLegacyPage(self):
        with open('sampleLegacyItems.json', 'r') as f:
            j = json.loads(f.read())
        q = 'python docs'
        opts={'start': 0}
        self.engine = Legacy(q, opts)
        self.engine._test_feed = True
        self.engine.response = DResponse(j)
        self.engine.response.status_code = 200
        self.engine.next()

    def testLegacyItems(self):
        with open('sampleLegacyItems.json', 'r') as f:
            j = json.loads(f.read())
        q = 'python docs'
        opts={'start': 0}
        self.engine = Legacy(q, opts)
        self.engine._test_feed = True
        self.engine.response = DResponse(j)
        self.engine.response.status_code = 200
        self.engine.next()
        page = self.engine.currentPage
        item = page.nextItem()
        self.assertRegexpMatches(item.title,
            recode('Overview.*Python.*documentation'))
        item = page.nextItem()
        self.assertRegexpMatches(item.title,
            recode('Our.*Python\.org'))
        item = page.previousItem()
        self.assertRegexpMatches(item.title,
            recode('Overview.*Python.*documentation'))
        self.assertRaises(IndexError, page.previousItem)

        #next page error
        self.assertRaises(IndexError, self.engine.next)
    
    def testLegacyNoResults(self):
        self.engine = Legacy('', {})
        with open('sampleLegacyNoResults.json', 'r') as f:
            j = json.loads(f.read())
        self.engine._test_feed = True
        self.engine.response = DResponse(j)
        self.engine.response.status_code = 200
        page = self.engine.next()
        self.assertEqual(page.count, 0)


    def testLegacyRealRequests(self):
        """No rate limits on real requests."""
        q = 'python docs'
        self.engine = Legacy(q, {})
        self.engine.next()
        page = self.engine.currentPage
        item = page.nextItem()
        self.assertRegexpMatches(item.title,
            recode('Overview.*Python.*documentation'))
        item = page.nextItem()
        self.assertRegexpMatches(item.title,
            recode('.*'))
        item = page.previousItem()
        self.assertRegexpMatches(item.title,
            recode('Overview.*Python.*documentation'))
        self.assertRaises(IndexError, page.previousItem)
        #next page error
        self.assertRaises(IndexError, self.engine.next)

        #next page safe
        self.engine.maxPages = 2
        page = self.engine.next()
        self.assertEqual(page.startIndex, 4)
        page = self.engine.previous()

# vim:set ts=4 sw=4 et tw=79:

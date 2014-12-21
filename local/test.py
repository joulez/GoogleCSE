import sys
import unittest
import json
from GoogleAPI import CSE
from exceptions import *

def consist(s):
    if sys.version_info[0] < 3:
        s = s.encode('utf-8')
    return s


class DResponse(object):
    def __init__(self):
        self._json = None
    def json(self):
        return self._json

class TestCSE(unittest.TestCase):
    def setUp(self):
        q = 'python docs'
        opts = {'number': 1} 
        self.cse = CSE(q, opts, api_key='testkey', engineID='TestEngine')

    def testGoogleAPIErrors(self):
        with open('sample400Error.json', 'r') as f:
            j = json.loads(f.read())
               
        self.cse._test_feed = True
        self.cse.response = DResponse()
        self.cse.response._json = j[0]
        self.cse.response.status_code = self.cse.response._json['error']['code']
        self.assertRaisesRegexp(GoogleAPIError, '^.\(CSE\) 400: Bad Request: keyInvalid')
        
        self.cse._test_feed = True
        self.cse.response = DResponse()
        self.cse.response._json = j[1]
        self.cse.response.status_code = self.cse.response._json['error']['code']
        self.assertRaisesRegexp(GoogleAPIError, '^.\(CSE\) 400: *.$')
        
        self.cse._test_feed = True
        self.cse.response = DResponse()
        self.cse.response._json = j[2]
        self.cse.response.status_code = self.cse.response._json['error']['code']
        self.assertRaisesRegexp(GoogleAPIError, '^.\(CSE\) 500: *.$')

        self.cse._test_feed = True
        self.cse.response = DResponse()
        self.cse.response._json = j[3]
        self.cse.response.status_code = self.cse.response._json['error']['code']
        self.assertRaisesRegexp(GoogleAPIError, '^.\(CSE\) 403: *.$')

    def test01Pages(self):
        self.cse.maxPages = 2
        with open('sampleResultsP1.json') as f:
            j = json.loads(f.read())
        
        def feed():
            self.cse._test_feed = True
            self.cse.response = DResponse()
            self.cse.response._json = j
            self.cse.response.status_code = 200
        feed()
        page = self.cse.next()
        self.assertEqual(consist(page.title), 
                consist('Google Custom Search - python docs'))
        self.assertEqual(len(self.cse.pages), 1)
        self.assertEqual(len(page.items), 10)

        with open('sampleResultsP2.json') as f:
            j = json.loads(f.read())

        feed()
        self.cse.next()
        self.assertEqual(len(self.cse.pages), 2)
        self.assertEqual(self.cse.currentPage.startIndex, 11)
        self.cse.previous()
        self.assertEqual(self.cse.currentPage.startIndex, 1)
        self.cse.next()
        self.assertRaises(IndexError, self.cse.next)
        self.cse.previous()
        self.assertRaises(IndexError, self.cse.previous)
        self.assertEqual(self.cse.currentPage.startIndex, 1)

        ##Item tests
        page = self.cse.currentPage
        item = page.nextItem()
        self.assertRegexpMatches(consist(item.title),
            consist('Overview.*Python.*documentation'))
        item = page.nextItem()
        self.assertRegexpMatches(consist(item.title),
            consist('Our.*Python\.org'))
        item = page.previousItem()
        self.assertRegexpMatches(consist(item.title),
            consist('Overview.*Python.*documentation'))
        self.assertRaises(IndexError, page.previousItem)

        #next page
        page = self.cse.next()
        item = page.nextItem()
        self.assertRegexpMatches(consist(item.title),
            consist('Python\sRuntime\sEnvironment.*Google\sCloud\sPlatform'))

        #previous page
        page = self.cse.previous()
        item = page.currentItem
        self.assertRegexpMatches(consist(item.title),
            consist('Overview.*Python.*documentation'))
        

# vim:set ts=4 sw=4 et tw=79:

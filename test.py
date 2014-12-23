###
# Copyright (c) 2014, Julian Paul Glass
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


###
import os
import json
from supybot.test import *
from .local.test import DResponse

dir = os.path.dirname(__file__)

def consist(s):
    if sys.version_info[0] < 3:
        return s.encode()
    return s

class GoogleCSETestCase(PluginTestCase):
    plugins = ('GoogleCSE',)
    def setUp(self, *args, **kwargs):
        PluginTestCase.setUp(self, *args, **kwargs)
        self.plugin = self.irc.getCallback('googlecse')
    def test10NoSearchEngine(self):
        self.plugin = self.irc.getCallback('googlecse')
        with open(os.path.join(dir, 'local', 'sampleResultsP1.json'), 'r') as f:
            response = DResponse(json.loads(f.read()))
            response.status_code = 200
        self.plugin._test_feed(response)
        engineID = 'ENGINE'
        apikey = 'API'
        self.assertNotError('config plugins.googlecse.engineapi cse')
        self.assertNotError('config plugins.googlecse.apikey'
            ' {0}'.format(apikey))
        error = 'Error: A search engine is not configured for channel #test'
        self.assertError('googlecse next')
        self.assertError('googlecse previous')
        self.assertError('googlecse search python docs')
        self.assertNotError(consist('googlecse search --engine {0} python'
            ' docs').format(engineID))
        self.assertNotError('googlecse next')
        self.assertError('googlecse next')
        self.assertNotError('googlecse previous')
        self.assertNotError('googlecse previous')
        self.assertError('googlecse previous')
        self.plugin.engine.maxPages = 2
        with open(os.path.join(dir, 'local', 'sampleResultsP2.json'), 'r') as\
            f:
            response = DResponse(json.loads(f.read()))
            response.status_code = 200
        self.plugin._test_feed(response)
        self.assertNotError('config plugins.googlecse.maxpages 2')
        self.assertNotError('googlecse about')
        self.plugin._test_feed(None)
        self.assertError('googlecse search --engine ENGINE \'\' ')
   
    def test20NoResults(self):
        fpath = os.path.join(dir, 'local', 'sampleNoResults.json')
        with open(fpath, 'r') as f:
            response = DResponse(json.loads(f.read()))
            response.status_code = 200
        self.plugin._test_feed(response)
        self.assertNotError('config plugins.googlecse.engineapi cse')
        self.assertResponse('googlecse search --engine ENGINE NONE',
                'No results found.')
    
    def testResults(self):
        fpath = os.path.join(dir, 'local', 'sampleLegacyItems.json')
        with open(fpath, 'r') as f:
            response = DResponse(json.loads(f.read()))
            response.status_code = 200
        self.plugin._test_feed(response)
        self.assertNotError('config plugins.googlecse.engineapi legacy')
        self.assertNotError('config plugins.googlecse.maxpageresults 4')
        self.assertNotError('config plugins.googlecse.maxdisplayresults 1')
        self.assertError('googlecse next')
        self.assertNotError('googlecse search --engine ENGINE python docs')
        self.assertNotError('googlecse next')
        self.assertNotError('googlecse next')
        self.assertError('googlecse next')
        self.assertError('googlecse next')
        self.assertNotError('googlecse previous')
        self.assertNotError('googlecse previous')
        self.assertError('googlecse previous')
        
    def test20LegacyNoResults(self):
        fpath = os.path.join(dir, 'local', 'sampleLegacyNoResults.json')
        with open(fpath, 'r') as f:
            response = DResponse(json.loads(f.read()))
            response.status_code = 200
        self.plugin._test_feed(response)
        self.assertNotError('config plugins.googlecse.engineapi legacy')
        self.assertResponse('googlecse search --engine ENGINE NONE',
                'No results found.')
    
    def test20LegacyResults(self):
        fpath = os.path.join(dir, 'local', 'sampleLegacyItems.json')
        with open(fpath, 'r') as f:
            response = DResponse(json.loads(f.read()))
            response.status_code = 200
        self.plugin._test_feed(response)
        self.assertNotError('config plugins.googlecse.engineapi legacy')
        self.assertNotError('config plugins.googlecse.maxpageresults 4')
        self.assertNotError('config plugins.googlecse.maxdisplayresults 1')
        self.assertError('googlecse next')
        self.assertNotError('googlecse search --engine ENGINE python docs')
        self.assertNotError('googlecse next')
        self.assertNotError('googlecse next')
        self.assertError('googlecse next')
        self.assertError('googlecse next')
        self.assertNotError('googlecse previous')
        self.assertNotError('googlecse previous')
        self.assertError('googlecse previous')
        
    def test20LegacyEngine(self):
        self.plugin = self.irc.getCallback('googlecse')
        self.plugin._test_response = None
        self.assertResponse('config plugins.googlecse.engineapi','cse')
        self.assertNotError('config plugins.googlecse.engineapi legacy')
        self.assertNotError('config plugins.googlecse.maxdisplayresults 1')
        self.assertNotError('config plugins.googlecse.maxpageresults 5')
        self.assertNotError('config plugins.googlecse.maxPages 2')
        self.assertNotError('googlecse search python docs')
        self.assertNotError('googlecse next')
        self.assertNotError('googlecse previous')
        self.assertNotError('googlecse nextpage')
        self.assertNotError('googlecse previouspage')

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

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
    def testNoSearchEngine(self):
        plugin = self.irc.getCallback('googlecse')
        with open(os.path.join(dir, 'local', 'sampleResultsP1.json'), 'r') as f:
            response = DResponse()
            response.status_code = 200
            response._json = json.loads(f.read())
        plugin._test_feed(response)
        engine = 'ENGINE'
        apikey = 'API'
        self.assertNotError('config plugins.googlecse.apikey'
            ' {0}'.format(apikey))
        error = 'Error: A search engine is not configured for channel #test'
        self.assertError('googlecse search python docs')
        self.assertResponse(consist('googlecse search --engine {0} python'
            ' docs').format(consist(engine)),'')
        self.assertResponse('googlecse next','')
        self.assertResponse('googlecse previous', '')


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

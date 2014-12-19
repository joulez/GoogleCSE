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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('GoogleCSE')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

from .local import GoogleAPI

def validateEngine(irc, msg, args, state):
    """Validate engines."""
    callConverter('somethingWithoutSpaces', irc, msg, args, state)

addConverter('validateEngine', validateEngine)

class GoogleCSE(callbacks.Plugin):
    """The GoogleCSE plugin enables searching via their CSEv1 API"""

    def __init__(self, irc):
        self.__parent = super(GoogleCSE, self)
        self.__parent.__init__(irc)

    def _error(self, error):
        self.irc.error(error, Raise=True)

    def getEngine(self, channel):
        if channel.startswith('#'):
            return self.registryValue('defaultEngine', channel)
        return self.registryValue('defaultEngine')

    def getAPIKey(self, channel):
        apikey = self.registryValue('apikey')
        if not apikey:
            self.irc.error('Please add an API key to the default configuration.',
                Raise=True)
        return apikey

    def getDefaultOpts(self, channel):
        opts = {}
        opts['number'] = self.registryValue('number', channel)
        opts['snippet'] = self.registryValue('includeSnippet', channel)
        opts['safe'] = self.registryValue('safeLevel', channel)
        return opts

    def format(self, page, opts):
        l = []
        ctr = 0
        try:
            while True and ctr < opts['number']:
                ctr += 1
                item = page.items.next()
                title = item.title.encode('utf-8')
                link = item.link.encode('utf-8')
                value = '{0}: <{1}>'.format(ircutils.bold(title), link)
                if opts['snippet']:
                    value += u' {0}'.format(item.snippet.encode('utf-8'))
                l.append(value)
        except:
            return l
        return l

    @wrap([getopts({'engine': 'somethingWithoutSpaces', 'number': 'Int'}), 'text'])
    def search(self, irc, msg, args, opts, query):
        """<query>
        Standard basic search. Uses the channel configured engine by default.
        See plugins.googlecse.defaultEngine
        """
        self.irc = irc
        _opts = self.getDefaultOpts(msg.args[0])
        for option, arg in opts:
            _opts[option] = arg
        engine = self.getEngine(msg.args[0]) or _opts.get('engine')
        apikey = self.getAPIKey(msg.args[0])

        if not engine:
            self._error('A search engine is required use --engine or'
                    ' configure a default engine for the channel')

        cse = GoogleAPI.CSE(apikey, engine, query, _opts)
        page = cse.next()
        fList = self.format(page, _opts)
        joiner = ' | '
        ctr = 0
        if len(fList) > 1:
            ctr += 1
            output = joiner.join('#{0} {1}'.format(str(ctr), i) for i in fList)
        else:
            output = fList[0]
        self.irc.reply(output)

    @wrap
    def test(self, irc, msg, args, query):
        """Test"""
        pass

Class = GoogleCSE

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

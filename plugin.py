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

def isChannel(s):
    return True if s.startswith('#') else False

class GoogleCSE(callbacks.Plugin):
    """The GoogleCSE plugin enables searching via their CSEv1 API"""
    home = 'https://github.com/joulez/GoogleCSE'
    searchOpts = ('number', 'snippet', 'safe')

    def __init__(self, irc):
        self.__parent = super(GoogleCSE, self)
        self.__parent.__init__(irc)
        self._test_response = None
        self.opts = {}

    def _error(self, error):
        self.irc.error(error, Raise=True)

    def getEngine(self, channel):
        if channel.startswith('#'):
            return self.registryValue('defaultEngine', channel)
        return self.registryValue('defaultEngine')

    def getAPIKey(self):
        apikey = self.registryValue('apikey')
        if not apikey:
            self.irc.error('Please add an API key to the default configuration.',
                Raise=True)
        return apikey

    def setOpts(self, channel, opts):
        self.opts['number'] = self.registryValue('maxPageResults', channel)
        self.opts['maxDisplayResults'] = self.registryValue('maxDisplayResults',
                channel)
        self.opts['snippet'] = self.registryValue('includeSnippet', channel)
        self.opts['safe'] = self.registryValue('safeLevel', channel)
        self.opts['maxPages'] = self.registryValue('maxPages', channel)
        for option, arg in opts:
            self.opts[option] = arg

    def formatOutput(self, channel, page, nav):
        l = []
        ctr = 0
        max = self.registryValue('maxDisplayResults')
        def setFormat(title, link):
            v= format('%s: %u', ircutils.bold(item.title), item.link)
            if self.opts['snippet']:
                v += format(' %s',(item.snippet))
            return v

        if isChannel(channel):
            max = self.registryValue('maxDisplayResults', channel)
        try:
            while ctr < max:
                ctr += 1
                if nav == 'next':
                    item = page.nextItem()
                    l.append(setFormat(item.title, item.link))
                else:
                    item = page.previousItem()
                    l.insert(0, setFormat(item.title, item.link))
        except:
            return l
        return l

    def _next(self):
        if self._test_response:
            self.cse.response = self._test_response
            self.cse._test_feed = True
        return self.cse.next()
        

    @wrap([getopts({'engine': 'somethingWithoutSpaces', 'number': 'Int',
        'snippet': ''}), 'text'])
    def search(self, irc, msg, args, opts, query):
        """<query>
        Standard basic search. Uses the channel configured engine by default.
        See plugins.googlecse.defaultEngine
        """
        self.irc = irc
        self.setOpts(msg.args[0], opts)
        engine = self.getEngine(msg.args[0]) or self.opts.get('engine')
        apikey = self.getAPIKey()

        if not engine:
            self._error('A search engine is required use --engine or'
                    ' configure a default engine for the channel')

        self.cse = GoogleAPI.CSE(query, self.opts, api_key=apikey, 
            engine_id=engine)
        page = self._next()
        fList = self.formatOutput(msg.args[0], page, 'next')
        return self.printResults(irc, fList)

    @wrap
    def next(self, irc, msg, args):
        """Return next list of items."""
        if self.cse:
            page = self.cse.currentPage
            fList = self.formatOutput(msg.args[0], page, 'next')
            return self.printResults(irc, fList)

    @wrap
    def previous(self, irc, msg, args):
        """Return previous list of items."""
        if self.cse:
            page = self.cse.currentPage
            fList = self.formatOutput(msg.args[0], page, 'previous')
            return self.printResults(irc, fList)

    @wrap
    def nextpage(self, irc, msg, args):
        """Cue the next page."""
        try:
            if self.cse:
                page = self.cse.next()
            else:
                return
        except:
            return irc.error('No next pages.')
        return irc.reply(format('Current page startIndex: %i',page.startIndex))

    @wrap
    def previouspage(self, irc, msg, args):
        """Cue the previous page."""
        try:
            if self.cse:
                page = self.cse.previous()
            else:
                return
        except:
            return irc.error('No previous pages.')
        return irc.reply(format('Current page startIndex: %i',page.startIndex))

    def printResults(self, irc, L):
        if not L:
            return
        if len(L) > 1:
            self.irc.replies(L)
        else:
            self.irc.reply(L[0])

    @wrap(['text'])
    def cache(self, irc, msg, args, query):
        """<query>
        Search the cache for matches and load the results.
        """
        self.irc = irc

    @wrap
    def about(self, irc, *args):
        """<about>
        Return information about the plugin.
        """
        irc.reply(format('%s - Google Custom Search Engine plugin'
            ' for the Limnoria IRC bot %u', 
            ircutils.bold(self.__class__.__name__),
            ircutils.bold(self.home)))

    def _test_feed(self, response):
        """Testing purposes, feed a DResponse object from ./local/test.py"""
        self._test_response = response

Class = GoogleCSE

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

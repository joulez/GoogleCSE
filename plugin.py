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
import re
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

from .local.GoogleAPI import searchEngine

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
        self.engine = None
        self._current = None #cache current results

    def _error(self, error):
        self.irc.error(error, Raise=True)

    def getAPIKey(self):
        apikey = self.registryValue('apikey')
        if not apikey:
            self.irc.error('Please add an API key to the default configuration.',
                Raise=True)
        return apikey

    def setOpts(self, channel, opts=None):
        if not isChannel(channel):
            channel = None
        self.opts['engine'] = self.registryValue('defaultEngine', channel)
        self.opts['number'] = self.registryValue('maxPageResults', channel)
        self.opts['maxDisplayResults'] = self.registryValue('maxDisplayResults',
                channel)
        self.opts['snippet'] = self.registryValue('includeSnippet', channel)
        self.opts['safe'] = self.registryValue('safeLevel', channel)
        self.opts['maxPages'] = self.registryValue('maxPages', channel)
        self.opts['engineAPI'] = self.registryValue('engineAPI', channel)
        if opts:
            for option, arg in opts:
                self.opts[option] = arg

    def formatOutput(self, channel, page, nav):
        l = []
        ctr = 0
        max = self.registryValue('maxDisplayResults')
        def rebold(s):
            return s.replace('<b>', '\x02').replace('</b>', '\x02')

        def setFormat(title, link):
            v= format('%s: %u', ircutils.bold(item.title), item.link)
            if self.opts['snippet']:
                v += format(' %s',(item.snippet.replace('\n','')))
                if self.opts['engineAPI'] == 'legacy':
                    v = rebold(v)
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
            self.engine.response = self._test_response
            self.engine._test_feed = True
        return self.engine.next()

    def evalQuery(self, query):
        return re.sub('["\']', '', query.strip())

    @wrap([getopts({'engine': 'somethingWithoutSpaces', 'number': 'Int',
        'snippet': ''}), 'text'])
    def search(self, irc, msg, args, opts, query):
        """<query>
        Standard basic search. Uses the channel configured engine by default.
        See plugins.googlecse.defaultEngine
        """
        self.irc = irc
        if not self.evalQuery(query):
            return irc.error()
        self.setOpts(msg.args[0], opts)
        if self.opts['engineAPI'] == 'cse':
            apikey = self.getAPIKey()
            if not self.opts.get('engine'):
                self._error('A search engine is required use --engine or'
                        ' configure a default engine for the channel')
            self.engine = searchEngine(self.opts['engineAPI'],
                query, self.opts, api_key=apikey, 
                engine_id=self.opts['engine'])
            self.log.info(format('\"%s\" Search Engine API created with'
                ' custom engine ID \"%s\"', self.opts['engineAPI'],
                self.opts['engine']))
        else:
            self.engine = searchEngine(self.opts['engineAPI'],
                    query, self.opts)
            self.log.info(format('\"%s\" Search Engine API initialized',
                    self.opts['engineAPI']))
        page = self._next()
        print(page.count)
        if page.count == 0:
            return irc.reply('No results found.')
        self._current = self.formatOutput(msg.args[0], page, 'next')
        return self.printResults(irc, self._current)

    google = search

    @wrap
    def current(self, irc, msg, args):
        """Returns previously cached results."""
        if self._current:
            return self.printResults(irc, self._current)
        else:
            return irc.error('No active search.')

    @wrap
    def next(self, irc, msg, args):
        """Return next list of items."""
        if self.engine:
            page = self.engine.currentPage
            fList = self.formatOutput(msg.args[0], page, 'next')
            if fList:
                return self.printResults(irc, fList)
            return irc.error('No next item.')
        else:
            return irc.error('No active search.')

    @wrap
    def previous(self, irc, msg, args):
        """Return previous list of items."""
        if self.engine:
            page = self.engine.currentPage
            fList = self.formatOutput(msg.args[0], page, 'previous')
            if fList:
                return self.printResults(irc, fList)
            return irc.error('No previous item.')
        else:
            return irc.error('No active search.')

    @wrap
    def nextpage(self, irc, msg, args):
        """Cue the next page."""
        try:
            if self.engine:
                page = self.engine.next()
            else:
                return
        except:
            return irc.error('No next pages.')
        return irc.reply(format('Current page startIndex: %i',page.startIndex))

    @wrap
    def previouspage(self, irc, msg, args):
        """Cue the previous page."""
        try:
            if self.engine:
                page = self.engine.previous()
            else:
                return
        except:
            return irc.error('No previous pages.')
        return irc.reply(format('Current page startIndex: %i',page.startIndex))

    def printResults(self, irc, L):
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

    class cache(callbacks.Commands):
        @wrap
        def list(self, irc, msg, args):
            """List search cache."""

        @wrap
        def add(self, irc, msg, args):
            """Add current search result to the cache if not
            already added."""

        @wrap(['positiveInt'])
        def remove(self, irc, msg, args, id):
            """<id>
            Remove cache with <id>.
            """
    @wrap
    def about(self, irc, msg, *args):
        """<about>
        Return information about the plugin.
        """
        self.irc = irc
        self.setOpts(msg.args[0])
        irc.reply(format('%s - Google Custom Search Engine plugin '
            '(Engine API: %s) for the Limnoria IRC bot %u',
            ircutils.bold(self.__class__.__name__),
            ircutils.bold(self.opts['engineAPI']),
            ircutils.bold(self.home)))

    def _test_feed(self, response):
        """Testing purposes, feed a DResponse object from ./local/test.py"""
        self._test_response = response

Class = GoogleCSE

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

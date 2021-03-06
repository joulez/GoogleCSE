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

import supybot.conf as conf
import supybot.registry as registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('GoogleCSE')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('GoogleCSE', True)

class SafeLevels(registry.OnlySomeStrings):
    validStrings = ('high', 'medium', 'off')

class EngineAPI(registry.OnlySomeStrings):
    validStrings = ('cse', 'legacy')

GoogleCSE = conf.registerPlugin('GoogleCSE')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(GoogleCSE, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))
conf.registerGlobalValue(GoogleCSE, 'apikey',
    registry.String('', _("""API key provided by google for API access"""),
        private=True))
conf.registerGlobalValue(GoogleCSE, 'engines',
    registry.CommaSeparatedListOfStrings('', _("""List of available Custom
        Search Engines.""")))
conf.registerChannelValue(GoogleCSE, 'defaultEngine',
    registry.String('', _("""Default Custom Search Engine for channel."""),
        private=True))
conf.registerChannelValue(GoogleCSE, 'maxPageResults',
    registry.Integer(10, _("""Maximum number of page results to fetch.""")))
conf.registerChannelValue(GoogleCSE, 'maxPages',
    registry.Integer(1, _("""Maximum number of page results to fetch.""")))
conf.registerChannelValue(GoogleCSE, 'maxDisplayResults',
    registry.Integer(5, _("""Maximum number of page results to display.""")))
conf.registerChannelValue(GoogleCSE, 'includeSnippet',
    registry.Boolean(False, _("""Display search result snippet in the output.""")))
conf.registerChannelValue(GoogleCSE, 'safeLevel',
    SafeLevels('medium', _("""Search results safe level. Default: medium.""")))
conf.registerChannelValue(GoogleCSE, 'engineAPI',
    EngineAPI('cse', _("""Select google engine mode. \"legacy\" sets the
    old google API \"cse\" sets the latest CSE API. Default: cse.""")))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

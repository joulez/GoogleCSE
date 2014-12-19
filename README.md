
GoogleCSE Plugin
----------------
The GoogleCSE plugin for the Limnoria IRC bot enables searching via their CSEv1 API.
Please note this has only been tested with Limnoria.

You are required to have a Google developers API key and at least one Custom Search Engine instance.

`@config plugins.googleCSE.api <yourAPI>`
`@config plugins.googleCSE.defaultEngine <customEngine>`

`@googlecse search <query>`

More google search options will be added. Currently `--snippet` is added but not tested.

TODO
----
Additional Commands:
`cache` - All search results will be cached to a permanent store and accessible 
with this command. (sqlite3). a `--no-cache` option will be added the the `search` command.
`cache remove` : Remove cached item.
`cache list` : List cached items (this could get big).

Polling cache search terms via `__call__` and a `plugins.googleCSE.cacheRefresh` configuration setting.

DISCLAIMER
----------
This plugin is currently in alpha state.

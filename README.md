
GoogleCSE Plugin
----------------
The GoogleCSE plugin for the Limnoria IRC bot enables searching via their CSEv1 API.
Please note this has only been tested with Limnoria.

Using CSE mode
--------------
You are required to have a Google developers API key when using a Custom Search Engine instance.

`@config plugins.googleCSE.engineapi cse`

`@config plugins.googleCSE.apikey <yourAPI>`

`@config plugins.googleCSE.defaultEngine <customEngine>`

`@googlecse search <query>`

Using Legacy Mode
-----------------
Until google decides to shutdown it's previously announced deprecation of the legacy api - Legacy api mode is supported via the `legacy` api.

`@config plugins.googleCSE.engineAPI legacy`

Neither `googleCSE.apikey` or `googleCSE.defaultEngine` are required.

Navigation
----------
Results are temporarily cached (until the next invocation).
The plugin currently supports `@next`, `@previous`, `@nextpage` and `@previouspage` commands. This is configurable via

`@config plugins.googleCSE.maxDisplayResults` - Maximum results to display at a time (`@next` and `@previous` load more results)

`@config plugins.googleCSE.maxPageResults` - Maximum results for any given page.

`@config plugins.googleCSE.maxPages` - Maximum pages (default is 1 - who goes pass the first page?)

TODO
----
####Additional Commands:

`cache` - All search results will be cached to a permanent store and accessible 
with this command. (sqlite3). A `--no-cache` option will be added the the `search` command.

`cache remove` : Remove cached item.

`cache list` : List cached items (this could get big).

Polling cache search terms via `__call__` and a `plugins.googleCSE.cacheRefresh` configuration setting.

DISCLAIMER
----------
This plugin is currently in alpha state.

DIRECTIVE_TYPES = [
    {'internalName': 'DIR_HTTP_ACCESS',
     'friendlyName': 'Allows http clients (browsers) to access the http port. this is the primary access control list.',
     'configName': 'http_access'},
    {'internalName': 'DIR_HTTP_REPLY_ACCESS',
        'friendlyName': 'Allows http clients (browsers) to receive the reply to their request. this further restricts permissions given by http_access, and is primarily intended to be used together with rep_mime_type acl for blocking different content types.',
        'configName': 'http_reply_access'},
    {'internalName': 'DIR_ICP_ACCESS',
        'friendlyName': 'Allows neighbor caches to query your cache with icp.',
        'configName': 'icp_access'},
    {'internalName': 'DIR_MISS_ACCESS',
        'friendlyName': 'Allows certain clients to forward cache misses through your cache. this further restricts permissions given by http_access, and is primarily intended to be used for enforcing sibling relations by denying siblings from forwarding cache misses through your cache.',
        'configName': 'miss_access'},
    {'internalName': 'DIR_CACHE',
        'friendlyName': 'Defines responses that should not be cached.',
        'configName': 'cache'},
    {'internalName': 'DIR_URL_REWRITE_ACCESS',
        'friendlyName': 'Controls which requests are sent through the redirector pool.',
        'configName': 'url_rewrite_access'},
    {'internalName': 'DIR_IDENT_LOOKUP_ACCESS',
        'friendlyName': 'Controls which requests need an ident lookup.',
        'configName': 'ident_lookup_access'},
    {'internalName': 'DIR_ALWAYS_DIRECT',
        'friendlyName': 'Controls which requests should always be forwarded directly to origin servers.',
        'configName': 'always_direct'},
    {'internalName': 'DIR_NEVER_DIRECT',
        'friendlyName': 'Controls which requests should never be forwarded directly to origin servers.',
        'configName': 'never_direct'},
    {'internalName': 'DIR_SNMP_ACCESS',
        'friendlyName': 'Controls snmp client access to the cache.',
        'configName': 'snmp_access'},
    {'internalName': 'DIR_BROKEN_POSTS',
        'friendlyName': 'Defines requests for which squid appends an extra crlf after post message bodies as required by some broken origin servers.',
        'configName': 'broken_posts'},
    {'internalName': 'DIR_CACHE_PEER_ACCESS',
        'friendlyName': 'Controls which requests can be forwarded to a given neighbor (cache_peer).',
        'configName': 'cache_peer_access'},
    {'internalName': 'DIR_HTCP_ACCESS',
        'friendlyName': 'Controls which remote machines are able to make htcp requests.',
        'configName': 'htcp_access'},
    {'internalName': 'DIR_HTCP_CLR_ACCESS',
        'friendlyName': 'Controls which remote machines are able to make htcp clr requests.',
        'configName': 'htcp_clr_access'},
    {'internalName': 'DIR_REQUEST_HEADER_ACCESS',
        'friendlyName': 'Controls which request headers are removed when violating http protocol.',
        'configName': 'request_header_access'},
    {'internalName': 'DIR_REPLY_HEADER_ACCESS',
        'friendlyName': 'Controls which reply headers are removed from delivery to the client when violating http protocol.',
        'configName': 'reply_header_access'},
    {'internalName': 'DIR_DELAY_ACCESS',
        'friendlyName': 'Controls which requests are handled by what delay pool',
        'configName': 'delay_access'},
    {'internalName': 'DIR_ICAP_ACCESS',
        'friendlyName': '(replaced by adaptation_access in squid-3.1) what requests may be sent to a particular icap server.',
        'configName': 'icap_access'},
    {'internalName': 'DIR_ADAPTATION_ACCESS',
        'friendlyName': 'What requests may be sent to a particular icap or ecap filter service.',
        'configName': 'adaptation_access'},
    {'internalName': 'DIR_LOG_ACCESS',
        'friendlyName': 'Controls which requests are logged. this is global and overrides specific file access lists appended to access_log directives.',
        'configName': 'log_access'}
]

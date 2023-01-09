class Bodies:
    searchA = '{"sort": "date", "format_": "all", "tags": "ambient", "depth": 2, "spotify": 0}'
    searchB = '{"sort": "pop", "format_": "all", "tags": "rock, fuzz", "depth": 1, "spotify": 1}'
    credentials = '{"client_id": "1becf788e8914edd9ff5b1c4ba9ef264", "client_secret": "2d461b0d15774be2b269978164190cd8"}'

class Links:
    sessionA = 0


class Actions:
    always = [('GET', '', 200)]

    first = [('GET', 'files', 204), ('GET', 'feed', 204), ('GET', 'spotify', 204)]

    casual = [('GET', 'files', 200), ('GET', 'feed', 200)]

    searchA = [('POST', 'search', 200, Bodies.searchA), ('GET', 'files', 200), ('GET', 'feed', 200)]
    searchB = [('POST', 'search', 200, Bodies.searchB), ('GET', 'files', 200), ('GET', 'feed', 200)]

    files = [
        # list all 0
        ('GET', 'files', 200, None),
        # load file 1
        ('GET', 'files/{}'.format(Links.sessionA), 200),
        # save file 2
        ('PUT', 'files/{}'.format(Links.sessionA), 200),
        # delete file 3
        ('DELETE', 'files/{}'.format(Links.sessionA), 200)
    ]

    spotify = [
        ('GET', 'spotify', 200),
        ('POST', 'spotify', 200, Bodies.credentials),
        ('DELETE', 'spotify', 200, Bodies.credentials)
    ]


class Scenario:
    schema = [
        Actions.always,
        Actions.first,
        Actions.searchA,
        Actions.spotify,
        Actions.searchB,
        Actions.casual
    ]

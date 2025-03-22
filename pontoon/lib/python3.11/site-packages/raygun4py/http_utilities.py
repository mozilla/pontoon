

def build_wsgi_compliant_request(request):
    if not request:
        return

    rg_request = None
    # start with WSGI environ variables, then overlay the specific, expected
    # httpRequest keys for RG API compat
    # https://www.python.org/dev/peps/pep-3333/#environ-variables

    http_host = request.get('hostName') \
                or request.get('HTTP_HOST') \
                or "{}:{}".format(request.get('SERVER_NAME'), request.get('SERVER_PORT'))

    if http_host is not None:
        http_host = http_host.replace(' ', '')

    try:
        http_form = getattr(request, 'form', None) or request.get('form')

        # fallback to wsgi.input
        if http_form is None and 'wsgi.input' in request:
            # we can assume WSGI keys inside this block
            content_length = int(request.get('CONTENT_LENGTH', 0))
            if content_length:
                http_form = request['wsgi.input'].read(content_length)

        rg_request = {
            'httpMethod': (request.get('httpMethod') or request.get('REQUEST_METHOD')),
            'url': (request.get('url') or request.get('PATH_INFO')),
            'hostName': http_host,
            'iPAddress': (request.get('ipAddress') or request.get('iPAddress') or request.get('REMOTE_ADDR')),
            'queryString': (request.get('queryString') or request.get('QUERY_STRING')),
            'headers': {}, # see below
            'form': http_form,
            'rawData': request.get('rawData')
        }
    except Exception:
        pass

    # Header processing
    _headers = request.get('headers')
    if _headers is None:
        # manually try to build up headers given known WSGI keys
        _headers = {
            'Content-Type': request.get('CONTENT_TYPE'),
            'Content-Length': request.get('CONTENT_LENGTH'),
        }

        for key, value in request.items():
            if key.startswith('HTTP_'):
                # 'HTTP_REFERER' => 'Referer'
                new_key = http_environ_var_to_header_key(key)
                _headers[new_key] = value

    rg_request['headers'] = _headers

    return rg_request


def http_environ_var_to_header_key(key):
    "turns HTTP_REFERER like keys into Referer"
    parts = key.split('_')
    if parts[0] == "HTTP":
        parts.pop(0)

    return '-'.join([x.title() for x in parts])
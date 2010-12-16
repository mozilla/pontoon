from django import http


def require_post(f):
    def wrapper(request, *args, **kw):
        if request.method == 'POST':
            return f(request, *args, **kw)
        else:
            return http.HttpResponseNotAllowed(['POST'])
    return wrapper

# functions for exposing web endpoints
from twisted.web.server import Request
from twisted.web.resource import Resource
from twisted.web.static import File
from jinja2 import Environment, FileSystemLoader
from .config import encode
import json

__all__ = ['expose_static', 'expose_web', 'root', "Request", "Args"]

from .injection import Inject, get_method


def HTTP_CODE(code, message='', request=None):
    if request:
        request.setResponseCode(code)
    return encode(f'{message}')


# we server static files under "/view"

root = File("view")


class StaticFile(File):
    def __init__(self, trigger_func, *a, **kw):
        self.trigger_func = trigger_func
        super().__init__(*a, **kw)

    def render(self, request, *a, **kw):
        args = Args(request.args)
        f = get_method(self.trigger_func, [request, args])

        res = super().render(request)
        f(*a, **kw)
        return res


class Args(dict, Inject):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._convert()

    @classmethod
    def __convert(cls, data):
        if isinstance(data, bytes):
            return data.decode('ascii')
        if isinstance(data, dict):
            return dict(map(cls.__convert, data.items()))
        if isinstance(data, (tuple, list)):
            return type(data)(map(cls.__convert, data))

        return data

    def _convert(self):
        new = self.__convert(self)
        self.clear()
        self.update(new)


class Template(Resource):
    def __init__(self, func, template):
        super().__init__()

        if '.' not in template:
            template = template + '.html'

        self.template = template
        self.function = func

    def render(self, request):
        args = Args(request.args)
        func = get_method(self.function, [request, args])

        ctx = func()
        ctx["__globals"] = json.dumps(ctx)
        env = Environment(loader=FileSystemLoader('view'))

        template = env.get_template(self.template)

        output_from_parsed_template = template.render(**ctx)
        return encode(output_from_parsed_template)


def expose_static(alias=None, template=True):
    def decorator(func):
        def wrapper():
            name = func.__name__

            filename = name if template in (True, False, None) else template

            if '.' not in filename:
                filename += '.html'

            if alias and not callable(alias):
                where = alias
            else:
                where = name

            if template:
                contents = Template(func, filename)
            else:
                contents = StaticFile(func, f'view/{filename}')

            root.putChild(where.encode(), contents)

        return wrapper()

    if callable(alias):
        return decorator(alias)  # return 'wrapper'
    else:
        return decorator  # ... or 'decorator'


def _safe_execute(func, request):
    try:
        args = Args(request.args)
        func = get_method(func, dependencies=[request, args])

        return encode(func())
    except Exception as e:
        return HTTP_CODE(400, f'Something went wrong: {e}', request)


def _add_page(root, name, function_post=None, function_get=None):
    class Page(Resource):
        def render_POST(self, request):
            if not function_post:
                return HTTP_CODE(405, "Method 'POST' not allowed.", request)
            return _safe_execute(function_post, request)

        def render_GET(self, request):
            if not function_get:
                return HTTP_CODE(405, "Method 'GET' not allowed.", request)
            return _safe_execute(function_get, request)

    p = Page()

    # allow trailing slash:
    p.putChild(b"", p)

    root.putChild(name.encode(), p)


def expose_web(method=None, alias=None):
    def wrapper(f):
        def inner_wrapper(*a, **kw):
            f(*a, **kw)

        request_method = method.lower() if method and isinstance(method, str) else 'get'

        kwargs = {}

        if request_method == 'post':
            kwargs['function_post'] = f
        elif request_method == 'get':
            kwargs['function_get'] = f
        else:
            raise NotImplementedError(f'Method {request_method} not implemented.')

        _add_page(root, f.__name__, **kwargs)

        if f.__name__ == "index":
            # index is special
            _add_page(root, "", **kwargs)

        if alias is not None:
            if not isinstance(alias, (tuple, list)):
                aliases = [alias]
            else:
                aliases = alias

            for a in aliases:
                _add_page(root, a, **kwargs)

        return inner_wrapper

    if callable(method):
        return wrapper(method)
    else:
        return wrapper

from functools import partial

from .ws import expose_ws
from .web import expose_web
from .web import expose_static

__all__ = ["websocket", "web", "static", "template"]

websocket = expose_ws
web = expose_web
template = expose_static

static = partial(template, template=False)

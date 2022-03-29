import sys

from autobahn.twisted.websocket import WebSocketServerFactory  # WebSocketServerProtocol
from twisted.internet import reactor, ssl
from twisted.python import log
from twisted.web.server import Site
from autobahn.twisted.resource import WebSocketResource

from .config import config
from .logging import console
from .ws import Server
from .web import root
from ._autoreload import autoreload


def _create_listener(port, site_root, ssl_factory):
    if ssl_factory:
        return reactor.listenSSL(int(port), Site(site_root), ssl_factory)
    else:
        return reactor.listenTCP(int(port), Site(site_root))


def _serve(arguments):
    if not arguments:
        port = '8080'
    else:
        port = arguments[0]
    log.startLogging(sys.stdout)
    if config.get('ssl'):
        factory = WebSocketServerFactory(u"wss://127.0.0.1:{}".format(port))
        ssl_factory = ssl.DefaultOpenSSLContextFactory('keys/privkey.pem',
                                                       'keys/cert.pem')
    else:
        factory = WebSocketServerFactory("ws://127.0.0.1:{}".format(port))
        ssl_factory = None

    factory.protocol = Server

    # run our WebSocket server under "/ws" (note that Twisted uses bytes for URIs)
    root.putChild(b"ws", WebSocketResource(factory))
    # start listening
    _create_listener(port, root, ssl_factory)
    reactor.run()


def serve(args, dev=None):
    if dev:
        import time
        try:
            autoreload(_serve, args)
        except Exception as e:
            console.error(e)
            time.sleep(3)
            serve(args, dev)
    else:
        _serve(args)

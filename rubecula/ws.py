# functions for exposing websocket endpoints

from autobahn.twisted.websocket import WebSocketServerProtocol

from . import injection
from .config import encode
import json
from dataclasses import dataclass

__all__ = ['expose_ws', 'peers', 'Server', "Client", "js", 'functions']

from .injection import Inject

peers, functions = {}, {}


def expose_ws(command=None):
    def wrapper(f):

        if command and not callable(command):
            cmd = command
        else:
            cmd = f.__name__

        def inner_wrapper(*a, **kw):
            f(*a, **kw)

        functions[cmd] = f
        return inner_wrapper

    if callable(command):
        return wrapper(command)
    else:
        return wrapper


class Server(WebSocketServerProtocol, Inject):

    def __init__(self):
        self.client = Client(self)
        super().__init__()

    @property
    def peers(self):
        return peers.items()

    @staticmethod
    def default_func(*_):
        raise NotImplementedError('please query another method ({})'.format(list(functions)))

    @staticmethod
    def payload_to_dict(pl):
        return json.loads(pl.decode())

    def send_client(self, message):
        self.sendMessage(encode(message))

    def _handle(self, payload):
        payload = self.payload_to_dict(payload)
        function = functions.get(payload.get('function', None), self.default_func)

        function = injection.get_method(function, dependencies=[self, self.client])

        result = function(payload.get('data', {}))

        if payload.get('return'):
            # add 'return' token to response:
            if isinstance(result, dict):
                result['return'] = payload['return']
            else:
                result = {
                    'return': payload['return'],
                    'data': result,
                }

        return encode(result)

    def onConnect(self, request):
        # add peer to peer pool
        peers[request.peer] = self

    def onMessage(self, payload, is_binary):
        try:
            self.send_client(self._handle(payload))
        except Exception as e:
            self.send_client('An error occured: {}'.format(str(repr(e))))

    def onClose(self, was_clean, code, reason):
        if peers.get(self.peer):
            # cleanup
            del peers[self.peer]

    @property
    def js(self):
        return JavaScript(server=self)


@dataclass
class JavascriptCall:
    func: str
    server: Server = None

    def __call__(self, data, **kwargs):
        data = {
            'function': self.func,
            'data': data,
            **kwargs
        }

        if self.server:
            return self.server.send_client(data)
        else:
            return data


@dataclass
class JavaScript:
    server: Server = None

    def __getattr__(self, key):
        return JavascriptCall(key, self.server)


@dataclass
class Client(JavaScript, Inject):
    # dummy for ease of use
    server: Server = None


js = JavaScript()

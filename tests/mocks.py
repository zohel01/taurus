""" test """
import logging
from logging import Handler

import requests

from bzt.engine import Engine, FileLister, HavingInstallableTools
from bzt.engine import Provisioning, ScenarioExecutor, Reporter
from bzt.utils import to_json

try:
    from exceptions import KeyboardInterrupt
except ImportError:
    # noinspection PyUnresolvedReferences
    from builtins import KeyboardInterrupt


class EngineEmul(Engine):
    def __init__(self):
        super(EngineEmul, self).__init__(logging.getLogger(''))
        pass


class ModuleMock(ScenarioExecutor, Provisioning, Reporter, FileLister, HavingInstallableTools):
    """ mock """

    def __init__(self):
        super(ModuleMock, self).__init__()
        pass


class RecordingHandler(Handler):
    def __init__(self):
        super(RecordingHandler, self).__init__()

    def emit(self, record):
        pass

    def write_log(self, buff, str_template, args):
        pass


class BZMock(object):
    def __init__(self, obj=None):
        """
        :type obj: bzt.bza.BZAObject
        """
        super(BZMock, self).__init__()
        locs = [{'id': 'aws', 'sandbox': False, 'title': 'AWS'},
                {'id': 'us-east-1', 'sandbox': False, 'title': 'East'},
                {'id': 'us-west', 'sandbox': False, 'title': 'Dallas (Rackspace)'},
                {'id': 'harbor-sandbox', 'sandbox': True, 'title': 'Sandbox'},
                {'id': 'non-harbor-sandbox', 'sandbox': True, 'title': 'Sandbox Neverexisting'}, ]
        self.mock_get = {
            'https://a.blazemeter.com/api/v4/web/version': {},
            'https://a.blazemeter.com/api/v4/user': {'defaultProject': {'id': None}},
            'https://a.blazemeter.com/api/v4/accounts': {"result": [{'id': 1}]},
            'https://a.blazemeter.com/api/v4/workspaces?accountId=1&enabled=true&limit=100': {
                "result": [{'id': 1, 'enabled': True}]},
            'https://a.blazemeter.com/api/v4/multi-tests?workspaceId=1&name=Taurus+Cloud+Test': {"result": []},
            'https://a.blazemeter.com/api/v4/tests?workspaceId=1&name=Taurus+Cloud+Test': {"result": []},
            'https://a.blazemeter.com/api/v4/projects?workspaceId=1&limit=99999': {"result": []},
            'https://a.blazemeter.com/api/v4/web/elfinder/1?cmd=open&target=s1_Lw': {"files": []},
            'https://a.blazemeter.com/api/v4/web/elfinder/1?target=s1_Lw&cmd=open': {"files": []},
            'https://a.blazemeter.com/api/v4/workspaces/1': {"result": {"locations": locs}},
        }

        self.mock_post = {}
        self.mock_patch = {}
        self.requests = []

        if obj is not None:
            self.apply(obj)

    def apply(self, obj):
        obj.http_request = self._request_mock

    def _request_mock(self, method, url, **kwargs):
        """
        :param method:
        :param url:
        :param kwargs:
        :rtype: requests.Response
        """
        # TODO: make it simplier, mocking and replacing requests.request of BZAObject
        if method == 'GET':
            resp = self.mock_get[url]
        elif method == 'POST':
            resp = self.mock_post[url]
        elif method == 'PATCH':
            resp = self.mock_patch[url]
        else:
            raise ValueError()

        response = requests.Response()

        if isinstance(resp, list):
            resp = resp.pop(0)

        data = kwargs['data']
        logging.debug("Emulated %s %s %s: %s", method, url, data, resp)
        self.requests.append({"method": method, "url": url, "data": data})
        if isinstance(resp, BaseException):
            raise resp
        response._content = to_json(resp)
        response.status_code = 200
        return response

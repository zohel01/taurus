""" test """
import logging
import os
import random
import sys
import tempfile
from logging import Handler

import requests

from bzt.engine import Engine, Configuration, FileLister, HavingInstallableTools
from bzt.engine import Provisioning, ScenarioExecutor, Reporter
from bzt.modules.aggregator import ResultsReader
from bzt.utils import load_class, to_json
from tests import random_sample

try:
    from exceptions import KeyboardInterrupt
except ImportError:
    # noinspection PyUnresolvedReferences
    from builtins import KeyboardInterrupt


class EngineEmul(Engine):
    def __init__(self):
        super(EngineEmul, self).__init__(logging.getLogger(''))
        self.config.get('settings')['artifacts-dir'] = os.path.dirname(__file__) + "/../build/test/%Y-%m-%d_%H-%M-%S.%f"
        self.config.get('settings')['check-updates'] = False
        self.create_artifacts_dir()
        self.config.merge({"provisioning": "local"})
        self.config.merge({"modules": {"mock": ModuleMock.__module__ + "." + ModuleMock.__name__}})
        self.finalize_exc = None
        self.was_finalize = False

    def dump_config(self):
        """ test """
        fname = tempfile.mkstemp()[1]
        self.config.dump(fname, Configuration.JSON)
        with open(fname) as fh:
            logging.debug("JSON:\n%s", fh.read())


class ModuleMock(ScenarioExecutor, Provisioning, Reporter, FileLister, HavingInstallableTools):
    """ mock """

    def __init__(self):
        super(ModuleMock, self).__init__()
        self.postproc_exc = None
        self.check_exc = None
        self.prepare_exc = None
        self.startup_exc = None
        self.shutdown_exc = None

        self.check_iterations = sys.maxsize

        self.was_shutdown = False
        self.was_startup = False
        self.was_prepare = False
        self.was_check = False
        self.was_postproc = False

        self.is_has_results = False


    def get_exc(self, param):
        """
        :type param: str
        :return:
        """
        name = self.settings.get(param, "")
        if name:
            cls = load_class(name)
            return cls()
        return None

    def resource_files(self):
        """


        :return:
        """
        self.execution.get('files', []).append(__file__)
        return [__file__]

    def has_results(self):
        return self.is_has_results

    def install_required_tools(self):
        self.log.debug("All is good")


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
            'https://a.blazemeter.com/api/v4/workspaces?accountId=1&enabled=true&limit=100': {"result": [{'id': 1, 'enabled': True}]},
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

import json

from bzt.engine import ManualShutdown
from bzt.modules.aggregator import ConsolidatingAggregator
from bzt.modules.blazemeter import CloudProvisioning
from tests import BZTestCase, __dir__
from tests.mocks import EngineEmul, ModuleMock
from tests.modules.test_blazemeter import BZMock


class TestCloudProvisioning(BZTestCase):
    @staticmethod
    def __get_user_info():
        with open(__dir__() + "/../json/blazemeter-api-user.json") as fhd:
            return json.loads(fhd.read())

    def setUp(self):
        engine = EngineEmul()
        engine.aggregator = ConsolidatingAggregator()
        self.obj = CloudProvisioning()
        self.obj.settings.merge({'delete-test-files': False})
        self.obj.engine = engine
        self.obj.browser_open = False
        self.mock = BZMock(self.obj.user)
        self.mock.mock_post.update({})

    def configure(self, engine_cfg=None, get=None, post=None, patch=None, add_config=True, add_settings=True):
        if engine_cfg is None:
            engine_cfg = {}
        self.obj.engine.config.merge(engine_cfg)

        if add_settings:
            self.obj.settings["token"] = "FakeToken"
            self.obj.settings["browser-open"] = False
            self.obj.settings['default-location'] = "us-east-1"

        if add_config:
            self.obj.engine.config.merge({
                "modules": {"mock": ModuleMock.__module__ + "." + ModuleMock.__name__},
                "provisioning": "mock"})

            self.obj.parameters = self.obj.engine.config.get('execution')

        if isinstance(self.obj.parameters, list):
            self.obj.parameters = self.obj.parameters[0]

        self.mock.mock_get.update(get if get else {})
        self.mock.mock_post.update(post if post else {})
        self.mock.mock_patch.update(patch if patch else {})
        self.mock.mock_patch.update({'https://a.blazemeter.com/api/v4/tests/1': {"result": {}}})

    def test_dump_locations_new_style(self):
        self.configure()
        self.obj.settings["dump-locations"] = True
        self.obj.settings["use-deprecated-api"] = False
        self.assertRaises(ManualShutdown, self.obj.prepare)
        self.obj.post_process()

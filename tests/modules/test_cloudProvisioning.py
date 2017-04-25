from bzt.engine import ManualShutdown
from bzt.modules.blazemeter import CloudProvisioning
from tests import BZTestCase
from tests.mocks import EngineEmul
from tests.modules.test_blazemeter import BZMock


class TestCloudProvisioning(BZTestCase):
    def setUp(self):
        engine = EngineEmul()
        self.obj = CloudProvisioning()
        self.obj.engine = engine
        self.mock = BZMock(self.obj.user)
        self.mock.mock_post.update({})

    def configure(self, engine_cfg=None, get=None, post=None, patch=None, add_config=True, add_settings=True):
        if add_settings:
            self.obj.settings["token"] = "FakeToken"
            self.obj.settings["browser-open"] = False
            self.obj.settings['default-location'] = "us-east-1"

        self.mock.mock_patch.update({'https://a.blazemeter.com/api/v4/tests/1': {"result": {}}})

    def test_dump_locations_new_style(self):
        self.configure()
        self.obj.settings["dump-locations"] = True
        self.obj.settings["use-deprecated-api"] = False
        try:
            self.obj.prepare()
        except BaseException as exc:
            self.assertTrue(isinstance(exc, ManualShutdown), exc)
            pass

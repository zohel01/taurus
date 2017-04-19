from bzt import TaurusNetworkError
from tests import BZTestCase

from bzt.bza import BZAObject, User
from bzt.engine import ScenarioExecutor
from bzt.modules.aggregator import ConsolidatingAggregator
from bzt.modules.blazemeter import CloudProvisioning
from tests.mocks import EngineEmul, ModuleMock, BZMock


class TestBZAObject(BZTestCase):
    def test_ping(self):
        obj = User()
        obj.ping()

class TestCloudProvisioningOld(BZTestCase):
    def test_case1(self):
        mock = BZMock()

        mock.mock_get.update({})

        mock.mock_post = {}

        mock.mock_patch = {}

        prov = CloudProvisioning()
        prov.browser_open = None
        prov.public_report = True
        prov.user.token = "test"
        prov.engine = EngineEmul()
        prov.engine.aggregator = ConsolidatingAggregator()
        # prov.engine.config.merge({"modules": {"blazemeter": {"browser-open": False}}})
        prov.engine.config[ScenarioExecutor.EXEC] = [{
            "executor": "mock",
            "locations": {
                "aws": 1
            },
            "files": ModuleMock().get_resource_files()
        }]
        mock.apply(prov.user)

        prov.prepare()
        prov.startup()
        prov.check()
        prov._last_check_time = 0
        prov.check()
        prov.shutdown()
        prov.post_process()

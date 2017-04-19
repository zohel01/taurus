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

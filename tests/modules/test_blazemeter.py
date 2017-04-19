from tests import BZTestCase

from bzt.bza import User
from tests.mocks import BZMock


class TestBZAObject(BZTestCase):
    def test_ping(self):
        obj = User()
        obj.ping()

from tests import BZTestCase


class LDJSONReaderEmul(object):
    def __init__(self):
        self.data = []

    def read(self, last_pass=False):
        for line in self.data:
            yield line


class TestReportReader(BZTestCase):
    def test_func_reader(self):
        pass

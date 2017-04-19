import logging
import os
import sys

from bzt.modules.selenium import SeleniumExecutor
from tests import BZTestCase, local_paths_config, __dir__
from tests.mocks import EngineEmul


class SeleniumTestCase(BZTestCase):
    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        engine_obj = EngineEmul()
        paths = [__dir__() + "/../../bzt/resources/base-config.yml", local_paths_config()]
        engine_obj.configure(paths)  # FIXME: avoid using whole engine in particular module test!
        self.obj = SeleniumExecutor()
        self.obj.settings = engine_obj.config.get("modules").get("selenium")
        self.obj.settings.merge({"virtual-display": {"width": 1024, "height": 768}})
        engine_obj.create_artifacts_dir(paths)
        self.obj.engine = engine_obj

    def configure(self, config):
        self.obj.engine.config.merge(config)
        self.obj.execution = self.obj.engine.config.get('execution')
        if isinstance(self.obj.execution, list):
            self.obj.execution = self.obj.execution[0]

    def tearDown(self):
        exc, _, _ = sys.exc_info()
        if exc:
            try:
                stdout_path = os.path.join(self.obj.engine.artifacts_dir, "selenium.out")
                if os.path.exists(stdout_path):
                    stdout = open(stdout_path).read()
                    logging.info('Selenium stdout: """\n%s\n"""', stdout)
            except BaseException:
                pass
            try:
                stdout_path = os.path.join(self.obj.engine.artifacts_dir, "selenium.err")
                if os.path.exists(stdout_path):
                    stderr = open(stdout_path).read()
                    logging.info('Selenium stderr: """\n%s\n"""', stderr)
            except BaseException:
                pass
        if isinstance(self.obj, SeleniumExecutor):
            self.obj.free_virtual_display()


class LDJSONReaderEmul(object):
    def __init__(self):
        self.data = []

    def read(self, last_pass=False):
        for line in self.data:
            yield line


class TestReportReader(BZTestCase):
    def test_func_reader(self):
        pass

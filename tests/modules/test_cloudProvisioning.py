import json
import os
import shutil
import tempfile
import time

import yaml

from bzt import TaurusConfigError, TaurusException
from bzt.bza import Master, Test, MultiTest
from bzt.engine import ScenarioExecutor, ManualShutdown, Service
from bzt.modules.aggregator import ConsolidatingAggregator, DataPoint, KPISet
from bzt.modules.blazemeter import CloudProvisioning, ResultsFromBZA, ServiceStubCaptureHAR
from bzt.modules.blazemeter import CloudTaurusTest, CloudCollectionTest
from bzt.utils import get_full_path
from tests import BZTestCase, __dir__
from tests.mocks import EngineEmul, ModuleMock, RecordingHandler
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
        self.mock.mock_post.update({
            'https://a.blazemeter.com/api/v4/projects': {"result": {"id": 1}},
            'https://a.blazemeter.com/api/v4/tests': {"result": {"id": 1}},
            'https://a.blazemeter.com/api/v4/tests/1/files': {"result": {"id": 1}},
            'https://a.blazemeter.com/api/v4/tests/1/start': {"result": {"id": 1}},
            'https://a.blazemeter.com/api/v4/masters/1/stop': {"result": True},
        })

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

    def test_check_interval(self):
        self.configure(
            engine_cfg={
                ScenarioExecutor.EXEC: {"executor": "mock", }},
            get={
                'https://a.blazemeter.com/api/v4/masters/1/status': [
                    {"result": {"id": id(self.obj)}},
                    {"result": {"id": id(self.obj), 'progress': 100}},
                ],
                'https://a.blazemeter.com/api/v4/masters/1/sessions': {"result": []},
                'https://a.blazemeter.com/api/v4/data/labels?master_id=1': {"result": [
                    {"id": "ALL", "name": "ALL"},
                    {"id": "e843ff89a5737891a10251cbb0db08e5", "name": "http://blazedemo.com/"}
                ]},
                'https://a.blazemeter.com/api/v4/data/kpis?interval=1&from=0&master_ids%5B%5D=1&kpis%5B%5D=t&kpis%5B%5D=lt&kpis%5B%5D=by&kpis%5B%5D=n&kpis%5B%5D=ec&kpis%5B%5D=ts&kpis%5B%5D=na&labels%5B%5D=ALL&labels%5B%5D=e843ff89a5737891a10251cbb0db08e5': {
                    "api_version": 2,
                    "error": None,
                    "result": [
                        {
                            "labelId": "ALL",
                            "labelName": "ALL",
                            "label": "ALL",
                            "kpis": [
                                {
                                    "n": 15,
                                    "na": 2,
                                    "ec": 0,
                                    "ts": 1442497724,
                                    "t_avg": 558,
                                    "lt_avg": 25.7,
                                    "by_avg": 0,
                                    "n_avg": 15,
                                    "ec_avg": 0
                                }, {
                                    "n": 7,
                                    "na": 4,
                                    "ec": 0,
                                    "ts": 1442497725,
                                    "t_avg": 88.1,
                                    "lt_avg": 11.9,
                                    "by_avg": 0,
                                    "n_avg": 7,
                                    "ec_avg": 0
                                }]
                        }, {
                            "labelId": "e843ff89a5737891a10251cbb0db08e5",
                            "labelName": "http://blazedemo.com/",
                            "label": "http://blazedemo.com/",
                            "kpis": [
                                {
                                    "n": 15,
                                    "na": 2,
                                    "ec": 0,
                                    "ts": 1442497724,
                                    "t_avg": 558,
                                    "lt_avg": 25.7,
                                    "by_avg": 0,
                                    "n_avg": 15,
                                    "ec_avg": 0
                                }, {
                                    "n": 7,
                                    "na": 4,
                                    "ec": 0,
                                    "ts": 1442497725,
                                    "t_avg": 88.1,
                                    "lt_avg": 11.9,
                                    "by_avg": 0,
                                    "n_avg": 7,
                                    "ec_avg": 0
                                }]}]},
                'https://a.blazemeter.com/api/v4/masters/1/reports/aggregatereport/data': {
                    "api_version": 2,
                    "error": None,
                    "result": [
                        {
                            "labelId": "ALL",
                            "labelName": "ALL",
                            "samples": 152,
                            "avgResponseTime": 786,
                            "90line": 836,
                            "95line": 912,
                            "99line": 1050,
                            "minResponseTime": 531,
                            "maxResponseTime": 1148,
                            "avgLatency": 81,
                            "geoMeanResponseTime": None,
                            "stDev": 108,
                            "duration": 119,
                            "avgBytes": 0,
                            "avgThroughput": 1.2773109243697,
                            "medianResponseTime": 0,
                            "errorsCount": 0,
                            "errorsRate": 0,
                            "hasLabelPassedThresholds": None
                        }, {
                            "labelId": "e843ff89a5737891a10251cbb0db08e5",
                            "labelName": "http://blazedemo.com/",
                            "samples": 152,
                            "avgResponseTime": 786,
                            "90line": 836,
                            "95line": 912,
                            "99line": 1050,
                            "minResponseTime": 531,
                            "maxResponseTime": 1148,
                            "avgLatency": 81,
                            "geoMeanResponseTime": None,
                            "stDev": 108,
                            "duration": 119,
                            "avgBytes": 0,
                            "avgThroughput": 1.2773109243697,
                            "medianResponseTime": 0,
                            "errorsCount": 0,
                            "errorsRate": 0,
                            "hasLabelPassedThresholds": None
                        }]}
            }
        )

        self.obj.settings["check-interval"] = "1s"

        self.obj.prepare()
        self.obj.startup()
        self.obj.check()  # this one should work
        self.obj.engine.aggregator.check()
        self.obj.check()  # this one should be skipped
        self.obj.engine.aggregator.check()
        time.sleep(1.5)
        self.obj.check()  # this one should work
        self.obj.engine.aggregator.check()
        self.obj.check()  # this one should skip
        self.obj.results_reader.min_ts = 0  # to make it request same URL
        self.obj.engine.aggregator.check()

        self.assertEqual(22, len(self.mock.requests))

    def test_dump_locations(self):
        self.configure()
        log_recorder = RecordingHandler()
        self.obj.log.addHandler(log_recorder)

        self.obj.settings["dump-locations"] = True
        self.obj.settings["use-deprecated-api"] = True
        self.assertRaises(ManualShutdown, self.obj.prepare)

        warnings = log_recorder.warn_buff.getvalue()
        self.assertIn("Dumping available locations instead of running the test", warnings)
        info = log_recorder.info_buff.getvalue()
        self.assertIn("Location: us-west\tDallas (Rackspace)", info)
        self.assertIn("Location: us-east-1\tEast", info)
        self.assertNotIn("Location: harbor-sandbox\tSandbox", info)
        self.obj.post_process()

    def test_dump_locations_new_style(self):
        log_recorder = RecordingHandler()
        self.obj.log.addHandler(log_recorder)
        self.configure()
        self.obj.settings["dump-locations"] = True
        self.obj.settings["use-deprecated-api"] = False
        self.assertRaises(ManualShutdown, self.obj.prepare)

        warnings = log_recorder.warn_buff.getvalue()
        self.assertIn("Dumping available locations instead of running the test", warnings)
        info = log_recorder.info_buff.getvalue()
        self.assertIn("Location: us-west\tDallas (Rackspace)", info)
        self.assertIn("Location: us-east-1\tEast", info)
        self.assertIn("Location: harbor-sandbox\tSandbox", info)

        self.obj.post_process()

    def test_settings_from_blazemeter_mod(self):
        self.configure(
            add_settings=False,
            engine_cfg={
                ScenarioExecutor.EXEC: {
                    "executor": "mock",
                    "concurrency": 5500,
                    "locations": {
                        "us-east-1": 1,
                        "us-west": 1}},
                "modules": {
                    "blazemeter": {
                        "class": ModuleMock.__module__ + "." + ModuleMock.__name__,
                        "token": "bmtoken",
                        "detach": True,
                        "browser-open": None,
                        "check-interval": 10.0}}},
        )  # upload files

        # these should override 'blazemeter' settings
        self.obj.settings["check-interval"] = 20.0
        self.obj.settings["browser-open"] = "both"

        self.obj.prepare()

        self.assertEqual(self.obj.detach, True)
        self.assertEqual(self.obj.browser_open, "both")
        self.assertEqual(self.obj.user.token, "bmtoken")
        self.assertEqual(self.obj.check_interval, 20.0)
        self.assertEqual(11, len(self.mock.requests))

    def test_public_report(self):
        self.configure(
            engine_cfg={
                ScenarioExecutor.EXEC: {
                    "executor": "mock",
                    "concurrency": 1,
                    "locations": {
                        "us-west": 2
                    }}},
            post={
                'https://a.blazemeter.com/api/v4/masters/1/public-token': {"result": {"publicToken": "publicToken"}}
            },
            get={
                'https://a.blazemeter.com/api/v4/masters/1/status': {"result": {"status": "CREATED"}},
                'https://a.blazemeter.com/api/v4/masters/1/sessions': {"result": {"sessions": []}},
                'https://a.blazemeter.com/api/v4/masters/1/full': {"result": {}},
            }
        )

        log_recorder = RecordingHandler()
        self.obj.log.addHandler(log_recorder)

        self.obj.settings['public-report'] = True
        self.obj.prepare()
        self.obj.startup()
        self.obj.check()
        self.obj.shutdown()
        self.obj.post_process()

        log_buff = log_recorder.info_buff.getvalue()
        log_line = "Public report link: https://a.blazemeter.com/app/?public-token=publicToken#/masters/1/summary"
        self.assertIn(log_line, log_buff)



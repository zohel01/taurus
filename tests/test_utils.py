""" unit test """
import sys
import logging

from psutil import Popen

from bzt.utils import log_std_streams, get_uniq_name
from tests.mocks import RecordingHandler
from tests import BZTestCase


class TestLogStreams(BZTestCase):
    def test_streams(self):
        pass

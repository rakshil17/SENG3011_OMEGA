import os
import sys
import pytest
from moto import mock_aws

from pprint import pprint
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../implementation')))
from ..implementation.RetrievalMicroservice import app

@pytest.mark.filterwarnings(r"ignore:datetime.datetime.utcnow\(\) is deprecated:DeprecationWarning")
class TestRegisterRoute:
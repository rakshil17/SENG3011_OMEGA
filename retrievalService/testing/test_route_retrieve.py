import os
import sys
import pytest
from moto import mock_aws

from pprint import pprint
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../implementation')))
from ..implementation.RetrievalMicroservice import app

@pytest.mark.filterwarnings(r"ignore:datetime.datetime.utcnow\(\) is deprecated:DeprecationWarning")
class TestRetrieveRoute:
    @mock_aws
    def test_retrieve(self, rootdir, client, s3_mock, test_table):
        fileName = os.path.join(rootdir, 'user1#apple_stock_data.csv')
        stockName = 'apple'
        username = 'user1'
        tableName = 'seng3011-test-dynamodb'

        with open(fileName) as f:
            fileContent = f.read()

        # pull for the first time - need to look at s3
        res = client.get(f"/v1/retrieve/{username}/{stockName}/")

        assert res.status_code == 200
        assert json.loads(res.data)['stock_name'] == stockName

        # pull again - no need to look at s3 this time
        res = client.get(f"/v1/retrieve/{username}/{stockName}/")
        assert res.status_code == 200
        assert json.loads(res.data)['stock_name'] == stockName


    @mock_aws
    def test_uncollected_stock(self, rootdir, client, s3_mock, test_table):
        fileName = os.path.join(rootdir, 'user1#apple_stock_data.csv')
        stockName = 'apple'
        username = 'user1'
        tableName = 'seng3011-test-dynamodb'

        with open(fileName) as f:
            fileContent = f.read()

        res = client.get(f"/v1/retrieve/{username}/fakestock/")
        pprint(res.data)
        assert res.status_code == 401
        assert json.loads(res.data)["StockNotFound"] is not None
    
    @mock_aws
    def test_invalid_test_table(self, rootdir, client, s3_mock, test_table):
        fileName = os.path.join(rootdir, 'user1#apple_stock_data.csv')
        stockName = 'apple'
        username = 'user1'
        tableName = 'seng3011-test-dynamodb'

        res = client.get(f"/v1/retrieve/fakeUser/{stockName}/")
        assert res.status_code == 500
        assert json.loads(res.data)["AWSError"] is not None



        


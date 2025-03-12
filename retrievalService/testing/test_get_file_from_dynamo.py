import pytest
from moto import mock_aws
import boto3

from ..implementation.RetrievalInterface import RetrievalInterface

@pytest.mark.filterwarnings(r"ignore:datetime.datetime.utcnow\(\) is deprecated:DeprecationWarning")
class TestGetFileFromDynamo:
    @mock_aws
    def test_get_file(self, test_table):
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'
        username = 'user1'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)
        
        found, retrievedFile, index = retrievalInterface.getFileFromDynamo(fileName, username, tableName)

        assert retrievedFile.get('content') == fileContent
        assert retrievedFile.get('filename') == fileName

    @mock_aws
    def test_get_



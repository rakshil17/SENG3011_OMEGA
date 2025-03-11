# https://pypi.org/project/moto/ 
# a mock for s3 to let me check that I am using boto3 correctly
import pytest
from moto import mock_aws
import boto3
from botocore.exceptions import ClientError

from ..implementation.RetrievalInterface import RetrievalInterface

# moto uses depreacted datetime.datetime.utcnow which causes a Deprecation Warning
# Therefore, I am choosing to hide this warning
@pytest.mark.filterwarnings(r"ignore:datetime.datetime.utcnow\(\) is deprecated:DeprecationWarning")
class TestPushToDynamo:
    # successfully push a file
    @mock_aws
    def test_push_file(self, test_table):
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'
        username = 'user1'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)

        retrievedFiles = test_table.get_item(Key={'username': username}).get('Item').get('retrievedFiles')
        assert len(retrievedFiles) == 1
        assert retrievedFiles[0].get('filename') == fileName
        assert retrievedFiles[0].get('content') == fileContent

    @mock_aws
    def test_table_not_exist(self, test_table):
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'
        username = 'user1'

        retrievalInterface = RetrievalInterface()
        # with pytest.raises(botocore.errorfactory.ResourceNotFoundException):
        with pytest.raises(ClientError) as errorInfo:
            retrievalInterface.pushToDynamo(fileName, fileContent, username, 'fakeTableName')
        assert errorInfo.value.response["Error"]["Code"] == "ResourceNotFoundException"

    def test_user_does_not_exist(self, test_table):
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        # with pytest.raises(botocore.errorfactory.ResourceNotFoundException):
        with pytest.raises(Exception) as errorInfo:
            retrievalInterface.pushToDynamo(fileName, fileContent, 'fake-user', tableName)







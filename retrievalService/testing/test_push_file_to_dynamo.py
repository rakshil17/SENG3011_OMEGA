# https://pypi.org/project/moto/
# a mock for s3 to let me check that I am using boto3 correctly
import pytest
from moto import mock_aws
from botocore.exceptions import ClientError

from ..implementation.RetrievalInterface import RetrievalInterface


# moto uses depreacted datetime.datetime.utcnow which causes a Deprecation Warning
# Therefore, I am choosing to hide this warning
@pytest.mark.filterwarnings(r"ignore:datetime.datetime.utcnow\(\) is deprecated:DeprecationWarning")
class TestPushToDynamo:
    @mock_aws
    def test_push_file(self, test_table):
        fileName = 'test-file.txt'
        fileContent = '''2024-12-3#3\n2024-12-4#4\n2024-12-5#8\n2024-12-6#3\n2024-12-7#4\n2024-12-8#8\n2024-12-9#3\n2024-12-10#4\n2024-12-11#8\n2024-12-12#3\n2024-12-13#4\n2024-12-14#8\n'''
        username = 'user1'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)

        retrievedFiles = test_table.get_item(
            TableName=tableName,
            Key={'username': {'S': username}}
        ).get('Item').get('retrievedFiles').get('L')

        assert len(retrievedFiles) == 1

        assert retrievedFiles[0].get('M').get('filename').get('S') == fileName


    @mock_aws
    def test_table_not_exist(self, test_table):
        fileName = 'test-file.txt'
        fileContent = '''2024-12-3#3\n2024-12-4#4\n2024-12-5#8\n2024-12-6#3\n2024-12-7#4\n2024-12-8#8\n2024-12-9#3\n2024-12-10#4\n2024-12-11#8\n2024-12-12#3\n2024-12-13#4\n2024-12-14#8\n'''
        username = 'user1'

        retrievalInterface = RetrievalInterface()
        with pytest.raises(ClientError) as errorInfo:
            retrievalInterface.pushToDynamo(fileName, fileContent, username, 'fakeTableName')
        assert errorInfo.value.response["Error"]["Code"] == "ResourceNotFoundException"

    @mock_aws
    def test_user_does_not_exist(self, test_table):
        fileName = 'test-file.txt'
        fileContent = '''2024-12-3#3\n2024-12-4#4\n2024-12-5#8\n2024-12-6#3\n2024-12-7#4\n2024-12-8#8\n2024-12-9#3\n2024-12-10#4\n2024-12-11#8\n2024-12-12#3\n2024-12-13#4\n2024-12-14#8\n'''
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        # with pytest.raises(botocore.errorfactory.ResourceNotFoundException):
        with pytest.raises(Exception):
            retrievalInterface.pushToDynamo(fileName, fileContent, 'fake-user', tableName)

    @mock_aws
    def test_user_double_pushes(self, test_table):
        fileName = 'test-file.txt'
        fileContent = '''2024-12-3#3\n2024-12-4#4\n2024-12-5#8\n2024-12-6#3\n2024-12-7#4\n2024-12-8#8\n2024-12-9#3\n2024-12-10#4\n2024-12-11#8\n2024-12-12#3\n2024-12-13#4\n2024-12-14#8\n'''
        tableName = 'test-table'
        username = 'user1'

        retrievalInterface = RetrievalInterface()

        response = retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)
        assert response is True

        with pytest.raises(Exception):
            retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)

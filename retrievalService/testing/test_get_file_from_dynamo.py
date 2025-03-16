import pytest
from moto import mock_aws

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

        assert retrievedFile == fileContent

    @mock_aws
    def test_get_file_from_wrong_user(self, test_table_two_users):
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'
        username = 'user1'
        username2 = 'user2'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)

        found, retrievedFile, index = retrievalInterface.getFileFromDynamo(fileName, username2, tableName)
        assert not found

    @mock_aws
    def test_get_file_wrong_file_name(self, test_table):
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'
        username = 'user1'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)

        found, retrievedFile, index = retrievalInterface.getFileFromDynamo('wrongFileName', username, tableName)
        assert not found

    @mock_aws
    def test_get_file_wrong_username(self, test_table):
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'
        username = 'user1'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)

        with pytest.raises(Exception):
            retrievalInterface.getFileFromDynamo(fileName, 'wrongUsername', tableName)

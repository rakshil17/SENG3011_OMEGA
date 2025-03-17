import pytest
from moto import mock_aws

from ..implementation.RetrievalInterface import RetrievalInterface


@pytest.mark.filterwarnings(r"ignore:datetime.datetime.utcnow\(\) is deprecated:DeprecationWarning")
class TestGetFileFromDynamo:
    @mock_aws
    def test_get_file(self, test_table):
        fileName = 'test-file.txt'
        fileContent = '''2024-12-3#3\n2024-12-4#4\n2024-12-5#8\n2024-12-6#3\n2024-12-7#4\n2024-12-8#8\n2024-12-9#3\n2024-12-10#4\n2024-12-11#8\n2024-12-12#3\n2024-12-13#4\n2024-12-14#8\n'''
        username = 'user1'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)

        found, retrievedFile, index = retrievalInterface.getFileFromDynamo(fileName, username, tableName)

        print(len(retrievedFile))
        for i, line in enumerate(fileContent.split('\n')):
            if i >= len(retrievedFile):
                break

            date, closeVal = line.split('#')
            assert retrievedFile[i].get('closeVal') == closeVal
            assert retrievedFile[i].get('date') == date


    @mock_aws
    def test_get_file_from_wrong_user(self, test_table_two_users):
        fileName = 'test-file.txt'
        fileContent = '''2024-12-3#3\n2024-12-4#4\n2024-12-5#8\n2024-12-6#3\n2024-12-7#4\n2024-12-8#8\n2024-12-9#3\n2024-12-10#4\n2024-12-11#8\n2024-12-12#3\n2024-12-13#4\n2024-12-14#8\n'''
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
        fileContent = '''2024-12-3#3\n2024-12-4#4\n2024-12-5#8\n2024-12-6#3\n2024-12-7#4\n2024-12-8#8\n2024-12-9#3\n2024-12-10#4\n2024-12-11#8\n2024-12-12#3\n2024-12-13#4\n2024-12-14#8\n'''
        username = 'user1'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)

        found, retrievedFile, index = retrievalInterface.getFileFromDynamo('wrongFileName', username, tableName)
        assert not found

    @mock_aws
    def test_get_file_wrong_username(self, test_table):
        fileName = 'test-file.txt'
        fileContent = '''2024-12-3#3\n2024-12-4#4\n2024-12-5#8\n2024-12-6#3\n2024-12-7#4\n2024-12-8#8\n2024-12-9#3\n2024-12-10#4\n2024-12-11#8\n2024-12-12#3\n2024-12-13#4\n2024-12-14#8\n'''
        username = 'user1'
        tableName = 'test-table'

        retrievalInterface = RetrievalInterface()
        retrievalInterface.pushToDynamo(fileName, fileContent, username, tableName)

        with pytest.raises(Exception):
            retrievalInterface.getFileFromDynamo(fileName, 'wrongUsername', tableName)

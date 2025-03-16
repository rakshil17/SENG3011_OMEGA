import pytest
import boto3
from moto import mock_aws


@pytest.fixture(scope="function")
def dynamodb_mock():
    """Sets up a mock DynamoDB table before each test using mock_aws."""
    with mock_aws():
        dynamodb = boto3.client('dynamodb', region_name='ap-southeast-2')
        yield dynamodb


@pytest.fixture(scope="function")
def test_table(dynamodb_mock):
    """Creates a test DynamoDB table before each test."""

    username = 'user1'

    with mock_aws():
        tableName = 'test-table'

        dynamodb_mock.create_table(
            TableName=tableName,
            KeySchema=[
                {'AttributeName': 'username', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'username', 'AttributeType': 'S'},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        item = {
            'username': {'S': username},
            'analysis': {'L': []},
            'retrievedFiles': {'L': []}
        }

        dynamodb_mock.put_item(
            TableName=tableName,
            Item=item
        )

        yield dynamodb_mock

        dynamodb_mock.delete_table(TableName=tableName)


# database with two users
@pytest.fixture(scope="function")
def test_table_two_users(dynamodb_mock):
    """Creates a test DynamoDB table before each test."""

    username = 'user1'
    username2 = 'user2'

    with mock_aws():
        tableName = 'test-table'

        dynamodb_mock.create_table(
            TableName=tableName,
            KeySchema=[
                {'AttributeName': 'username', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'username', 'AttributeType': 'S'},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        item = {
            'username': {'S': username},
            'analysis': {'L': []},
            'retrievedFiles': {'L': []}
        }

        item2 = {
            'username': {'S': username2},
            'analysis': {'L': []},
            'retrievedFiles': {'L': []}
        }

        dynamodb_mock.put_item(
            TableName=tableName,
            Item=item
        )

        dynamodb_mock.put_item(
            TableName=tableName,
            Item=item2
        )

        yield dynamodb_mock
        dynamodb_mock.delete_table(TableName=tableName)

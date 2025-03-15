import pytest
import boto3
from moto import mock_aws


@pytest.fixture(scope="function")
def dynamodb_mock():
    """Sets up a mock DynamoDB table before each test using mock_aws."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        yield dynamodb


@pytest.fixture(scope="function")
def test_table(dynamodb_mock):
    """Creates a test DynamoDB table before each test."""

    username = 'user1'

    with mock_aws():
        dynamodb = boto3.resource('dynamodb')
        tableName = 'test-table'

        table = dynamodb.create_table(
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
            'username': username,
            'analysis': [],
            'retrievedFiles': []
        }

        table.put_item(Item=item)

        yield table
        # clean up
        table.delete()


# database with two users
@pytest.fixture(scope="function")
def test_table_two_users(dynamodb_mock):
    """Creates a test DynamoDB table before each test."""

    username = 'user1'
    username2 = 'user2'

    with mock_aws():
        dynamodb = boto3.resource('dynamodb')
        tableName = 'test-table'

        table = dynamodb.create_table(
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
            'username': username,
            'analysis': [],
            'retrievedFiles': []
        }

        item2 = {
            'username': username2,
            'analysis': [],
            'retrievedFiles': []
        }

        table.put_item(Item=item)
        table.put_item(Item=item2)

        yield table
        # clean up
        table.delete()

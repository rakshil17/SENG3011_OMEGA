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

    fileName = 'test-file.txt'
    fileContent = 'some nice file content'
    username = 'user1'

    with mock_aws():
        dynamodb = boto3.resource('dynamodb')
        table_name = 'test-table'

        table = dynamodb.create_table(
            TableName=table_name,
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

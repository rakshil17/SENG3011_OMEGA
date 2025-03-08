# https://pypi.org/project/moto/ 
# a mock for s3 to let me check that I am using boto3 correctly

import pytest
from retrieveApp import BotoPullFile
from moto import mock_aws
import boto3

# moto uses depreacted datetime.datetime.utcnow which causes a Deprecation Warning
# Therefore, I am choosing to hide this warning
@pytest.mark.filterwarnings(r"ignore:datetime.datetime.utcnow\(\) is deprecated:DeprecationWarning")
class TestS3Operations:
    @mock_aws
    def test_pull_file():
        bucket_name = 'test-bucket'
        fileName = 'test-file.txt'
        file_content = 'Hello, Moto!'

        # Create a mock S3 bucket and upload a test file.
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
        'LocationConstraint': 'ap-southeast-2'})
        s3.put_object(Bucket=bucket_name, Key=fileName, Body=file_content.encode('utf-8'))

        # Call the function to download and read the file.
        filePuller = BotoPullFile()
        downloaded_content = filePuller.pull(bucket_name, fileName)

        # Assert that the downloaded content matches the original content.
        assert downloaded_content == file_content




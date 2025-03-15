# https://pypi.org/project/moto/
# a mock for s3 to let me check that I am using boto3 correctly
import pytest
from moto import mock_aws
import boto3
from ..implementation.RetrievalInterface import RetrievalInterface


# moto uses depreacted datetime.datetime.utcnow which causes a Deprecation Warning
# Therefore, I am choosing to hide this warning
@pytest.mark.filterwarnings(r"ignore:datetime.datetime.utcnow\(\) is deprecated:DeprecationWarning")
class TestPullFromS3:
    @mock_aws
    # successfully pull a file
    def test_pull_file(self):
        bucket_name = 'test-bucket'
        fileName = 'test-file.txt'
        file_content = 'Hello, Moto!'

        # Create a mock S3 bucket and upload a test file.
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-2'
        })
        s3.put_object(Bucket=bucket_name, Key=fileName, Body=file_content.encode('utf-8'))

        # Call the function to download and read the file.
        retrievalInterface = RetrievalInterface()
        downloaded_content = retrievalInterface.pull(bucket_name, fileName)

        # Assert that the downloaded content matches the original content.
        assert downloaded_content == file_content

    @mock_aws
    # try to pull a file that does not exist
    def test_pull_nonexistent_file(self):
        bucket_name = 'test-bucket'

        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-2'})
        s3.put_object(Bucket=bucket_name, Key='real-file', Body='file_content'.encode('utf-8'))

        retrievalInterface = RetrievalInterface()
        with pytest.raises(s3.exceptions.NoSuchKey):
            retrievalInterface.pull("test-bucket", "non-existent-file")

    @mock_aws
    def test_pull_nonexistent_bucket(self):
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket='real-bucket', CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-2'})
        retrievalInterface = RetrievalInterface()

        with pytest.raises(s3.exceptions.NoSuchBucket):
            retrievalInterface.pull("test-bucket", "non-existent-file")

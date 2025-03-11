# https://pypi.org/project/moto/ 
# a mock for s3 to let me check that I am using boto3 correctly
import pytest
from moto import mock_aws
import boto3

from ..implementation.RetrievalInterface import RetrievalInterface

# moto uses depreacted datetime.datetime.utcnow which causes a Deprecation Warning
# Therefore, I am choosing to hide this warning
@pytest.mark.filterwarnings(r"ignore:datetime.datetime.utcnow\(\) is deprecated:DeprecationWarning")
class TestDeleteFromS3:

    # successfully delete a file
    @mock_aws
    def test_delete_file(self):
        bucketName = 'test-bucket'
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'

        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucketName, CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-2'
        })

        s3.put_object(Bucket=bucketName, Key=fileName, Body=fileContent.encode('utf-8'))

        # Call the function to download and read the file.
        retrievalInterface = RetrievalInterface()
        result = retrievalInterface.deleteOne(bucketName, fileName)
        assert result == True

        with pytest.raises(s3.exceptions.NoSuchKey):
            retrievalInterface.pull(bucketName, fileName)



    @mock_aws
    def test_delete_non_existent_file(self):
        bucketName = 'test-bucket'
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'

        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucketName, CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-2'
        })

        s3.put_object(Bucket=bucketName, Key=fileName, Body=fileContent.encode('utf-8'))

        retrievalInterface = RetrievalInterface()
        result = retrievalInterface.deleteOne(bucketName, fileName)

        # even though the file never existed, boto3 does not throw an error
        assert result == True       

    @mock_aws
    def test_delete_non_existent_bucket(self):
        bucketName = 'test-bucket'
        fileName = 'test-file.txt'
        fileContent = 'some nice file content'

        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucketName, CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-2'
        })

        s3.put_object(Bucket=bucketName, Key=fileName, Body=fileContent.encode('utf-8'))
        retrievalInterface = RetrievalInterface()
        with pytest.raises(s3.exceptions.NoSuchBucket):
            retrievalInterface.deleteOne('non-existent-bucket', fileName)

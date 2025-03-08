import boto3
# won't be found in the repository because it is part of the gitignore file
# from secrets import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_S3_BUCKET_NAME, AWS_REGION
import sys


class RetrievalInterface:
    def pull(self, bucketName: str, fileNameOnS3: str) -> str:
        s3_client = boto3.client(service_name = 's3')

        try:
            response = s3_client.get_object(Bucket=bucketName, Key=fileNameOnS3)
            object_content = response['Body'].read().decode('utf-8')
            return object_content


        except s3_client.exceptions.NoSuchKey as e:
            sys.stderr.write(f"(RetrievalInterface.pull) No Such Key {fileNameOnS3}: {e}\n")
            raise
        except s3_client.exceptions.NoSuchBucket as e:
            sys.stderr.write(f"(RetrievalInterface.pull) No Such Bucket {bucketName}: {e}\n")
            raise
        except Exception as e:
            sys.stderr.write(f"(RetrievalInterface.pull) General Exception: {e}\n")
            raise

    def deleteOne(self, bucketName: str, fileNameOnS3: str) -> bool:
        s3_client = boto3.client("s3")
        try:
            response = s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        except Exception as e:
            raise

if __name__ == '__main__':
    interface = BotoPushAndPull()
    LOCAL_FILE = 'test_file.txt'
    NAME_FOR_S3 = 'test_file.txt'
    bucket_name = 'seng3011-omega-25t1-testing-bucket'

    message = interface.pull(bucket_name, NAME_FOR_S3)
    print(message)

import boto3
# won't be found in the repository because it is part of the gitignore file
# from secrets import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_S3_BUCKET_NAME, AWS_REGION
from secrets import  AWS_S3_BUCKET_NAME
import sys


class BotoPullFile:
    def pull(self, bucketName: str, fileNameOnS3: str) -> str:
        s3_client = boto3.client(service_name = 's3')

        try:
            response = s3_client.get_object(Bucket=bucketName, Key=fileNameOnS3)
            object_content = response['Body'].read().decode('utf-8')
            return object_content

        except Exception as e:
            sys.stderr.write(f"{e} (on line 27)\n")


if __name__ == '__main__':
    interface = BotoPushAndPull()
    LOCAL_FILE = 'test_file.txt'
    NAME_FOR_S3 = 'test_file.txt'
    bucket_name = 'seng3011-omega-25t1-testing-bucket'

    message = interface.pull(bucket_name, NAME_FOR_S3)
    print(message)

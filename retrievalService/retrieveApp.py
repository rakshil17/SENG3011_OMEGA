import boto3
# won't be found in the repository because it is part of the gitignore file
from secrets import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_S3_BUCKET_NAME, AWS_REGION



LOCAL_FILE = 'test_file.txt'
NAME_FOR_S3 = 'test_file.txt'

def pushFile(local_file: str, name_for_s3: str)->None:

    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    try:
        s3_client.upload_file(local_file, AWS_S3_BUCKET_NAME, name_for_s3)
    except Exception as e:
        print(e)


def pullFile(name_for_s3: str)->None:
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    response = s3_client.get_object(Bucket=AWS_S3_BUCKET_NAME, Key=name_for_s3)
    object_content = response['Body'].read().decode('utf-8')

    print(object_content)

if __name__ == '__main__':
    # pushFile(LOCAL_FILE, NAME_FOR_S3)             # uncomment depending on what you want to do
    pullFile(NAME_FOR_S3)
    # print("Hello world")
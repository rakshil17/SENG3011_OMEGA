import boto3
# won't be found in the repository because it is part of the gitignore file
# from secrets import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_S3_BUCKET_NAME, AWS_REGION
import sys

# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/programming-with-python.html for dynamoDB


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
    
            

    # Pushes a file and its content to dynamoDB
    # Does NOT check if the file already exists in the user's allocated memory
    def pushToDynamo(self, fileName: str, fileContent: str, username: str, tableName: str):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tableName)

        new_object = {
            'content': fileContent,
            'fileName': fileName
        }
        try:
            response = table.update_item(
                Key={
                    "username": username
                },
                UpdateExpression=f"SET {"retrievedFiles"} = list_append(if_not_exists({"retrievedFiles"}, :empty_list), :new_object)",
                ExpressionAttributeValues={
                    ':new_object': [new_object],  # Wrap the new object in a list for list_append
                    ':empty_list': []
                },
                ReturnValues="UPDATED_NEW"
            )

            print(response)
        except Exception as e:
            sys.stderr.write(f"(RetrievalInterface.pushToDynamo) General Exception {e}\n")


    def deleteOne(self, bucketName: str, fileNameOnS3: str) -> bool:
        s3_client = boto3.client("s3")
        try:
            s3_client.delete_object(Bucket=bucketName, Key=fileNameOnS3)
            return True
        except Exception as e:
            raise

if __name__ == '__main__':
    interface = RetrievalInterface()

    TABLE_NAME = "seng3011-test-dynamodb"

    interface.pushToDynamo("boto_file", "boto_file_content", "user1", TABLE_NAME)

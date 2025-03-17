from flask import Flask, request
from RetrievalInterface import RetrievalInterface
import sys

app =  Flask(__name__)

AWS_S3_BUCKET_NAME = "seng3011-omega-25t1-testing-bucket"
DYNAMO_DB_NAME = "seng3011-test-dynamodb"

@app.route('/v1/register/', methods=['POST'])
def register():
    username = request.get_json()['username']
    retrievalInterface = RetrievalInterface()

    try:
        retrievalInterface.register(username, DYNAMO_DB_NAME)
        return f"User {username} registered successfully"
    except Exception as e:
        sys.stderr.write(f"(RetrievalMicroservice.retrieve) Exception: {e}\n")
        return f"{e}"

@app.route('/v1/retrieve/<username>/<filename>/', methods=['GET'])
def retrieve(username, filename: str):
    retrievalInterface = RetrievalInterface()
    filenameS3 = f"{username}_{filename}"     # need to think about Rakshil's file formatting here
    try:
        found, content, index = retrievalInterface.getFileFromDynamo(filename, username, DYNAMO_DB_NAME)

        if found:
            return {
                'StockName': filename.removesuffix('.txt'),
                'StockData': content
            }
        else:
            content = retrievalInterface.pull(AWS_S3_BUCKET_NAME, f"{filenameS3}")
            # need to format Rakshil's S3 content format into DynamoDB content
            retrievalInterface.pushToDynamo(filename, content, username, DYNAMO_DB_NAME)
            found, content, index = retrievalInterface.getFileFromDynamo(filename, username, DYNAMO_DB_NAME)
            return {
                'StockName': filename.removesuffix('.txt'),     # will change depending on what Rakshil did
                'StockData': content
            }

    except Exception as e:
        sys.stderr.write(f"(RetrievalMicroservice.retrieve) Exception: {e}\n")
        return f"{e}"


@app.route('/v1/delete/', methods=['DELETE'])
def delete():
    filename = request.get_json()['filename']
    username = request.get_json()['username']

    retrievalInterface = RetrievalInterface()
    try:
        # delete from dynamodb
        retrievalInterface.deleteFromDynamo(filename, username, DYNAMO_DB_NAME)
        return f"Deleted {filename}"
    except Exception as e:
        sys.stderr.write(f"(RetrievalMicroservice.delete) Exception: {e}")

@app.route('/v1/list/<username>/', methods=['GET'])
def getAll(username):
    retrievalInterface = RetrievalInterface()
    try:
        return retrievalInterface.listUserFiles(username, DYNAMO_DB_NAME)

    except Exception as e:
        sys.stderr.write(f"(RetrievalMicroservice.delete) Exception: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

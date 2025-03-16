# ROUTES TO COMPLETE:
# /retrieve
# /list_files
# /delete
# /update           # more clarifaction would be good

from flask import Flask, request
from RetrievalInterface import RetrievalInterface
import sys
app = Flask(__name__)

AWS_S3_BUCKET_NAME = "seng3011-omega-25t1-testing-bucket"
DYNAMO_DB_NAME = "seng3011-test-dynamodb"


@app.route('/v1/retrieve/<username>/<filename>/', methods=['GET'])
def retrieve(username, filename: str):
    retrievalInterface = RetrievalInterface()
    try:
        # try to retrieve the file immediately in the dynamoDB
        # if there
        # if not, get from S3, push to dynamo

        # return content
        found, content, index = retrievalInterface.getFileFromDynamo(filename, username, DYNAMO_DB_NAME)
        print(f"found = {found}")
        if found:
            print("Good job nate")
            return content
        else:
            content = retrievalInterface.pull(AWS_S3_BUCKET_NAME, f"{username}_{filename}")
            retrievalInterface.pushToDynamo(filename, content, username, DYNAMO_DB_NAME)
            return content

    except Exception as e:
        sys.stderr.write(f"(RetrievalMicroservice.retrieve) Exception: {e}\n")
        return f"{e}"


@app.route('/v1/delete', methods=['DELETE'])
def delete():
    filename = request.get_json()['filename']
    filename = request.get_json()['username']

    retrievalInterface = RetrievalInterface()
    try:
        # delete from dynamodb
        retrievalInterface.deleteOne(AWS_S3_BUCKET_NAME, filename)
        return f"Deleted {filename}"
    except Exception as e:
        sys.stderr.write(f"(RetrievalMicroservice.delete) Exception: {e}")

# @app.route('/v1/list/<username>', methods=['GET'])
# def getAll():


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

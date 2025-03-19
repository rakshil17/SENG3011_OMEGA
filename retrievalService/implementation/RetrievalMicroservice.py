from flask import Flask, request
from RetrievalInterface import RetrievalInterface
import sys
from datetime import datetime
from pytz import timezone

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
        return f"(RetrievalMicroservice.retrieve) Exception: {e}\n"

@app.route('/v1/retrieve/<username>/<stockname>/', methods=['GET'])
def retrieve(username, stockname: str):
    retrievalInterface = RetrievalInterface()
    filenameS3 = f"{username}#{stockname}_stock_data.csv"     # need to think about Rakshil's file formatting here
    try:
        found, content, index = retrievalInterface.getFileFromDynamo(stockname, username, DYNAMO_DB_NAME)

        if found:
            return {
                'data_source': "yahoo_finance",
                'dataset_type': 'Daily stock data',
                'dataset_id': 'http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2-amazonaws.com',
                'time_object': {
                    'timestamp': f'{str(datetime.now(timezone('Australia/Sydney'))).split('+')[0]}',
                    'timezone': 'GMT+11' 
                },
                'stock_name': stockname,
                'events': content
            }
        else:
            content = retrievalInterface.pull(AWS_S3_BUCKET_NAME, f"{filenameS3}")
            # need to format Rakshil's S3 content format into DynamoDB content
            retrievalInterface.pushToDynamo(stockname, content, username, DYNAMO_DB_NAME)
            found, content, index = retrievalInterface.getFileFromDynamo(stockname, username, DYNAMO_DB_NAME)

            return {
                'data_source': "yahoo_finance",
                'dataset_type': 'Daily stock data',
                'dataset_id': 'http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2-amazonaws.com',
                'time_object': {
                    'timestamp': f'{str(datetime.now(timezone('Australia/Sydney'))).split('+')[0]}',
                    'timezone': 'GMT+11' 
                },
                'stock_name': stockname,
                'events': content
            }

    except Exception as e:
        return f"(RetrievalMicroservice.retrieve) Exception: {e}\n"


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
        return f"(RetrievalMicroservice.delete) Exception: {e}"

@app.route('/v1/list/<username>/', methods=['GET'])
def getAll(username):
    retrievalInterface = RetrievalInterface()
    try:
        return retrievalInterface.listUserFiles(username, DYNAMO_DB_NAME)

    except Exception as e:
        return f"(RetrievalMicroservice.delete) Exception: {e}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

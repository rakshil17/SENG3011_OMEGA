from flask import Flask, request
from botocore.exceptions import ClientError
from RetrievalInterface import RetrievalInterface

# import sys
from datetime import datetime
from pytz import timezone

import json

from exceptions.UserNotFound import UserNotFound
from exceptions.UserAlreadyExists import UserAlreadyExists

# from exceptions.UserHasFile import UserHasFile

app = Flask(__name__)

AWS_S3_BUCKET_NAME = "seng3011-omega-25t1-testing-bucket"
DYNAMO_DB_NAME = "seng3011-test-dynamodb"


@app.route("/v1/register/", methods=["POST"])
def register():
    username = request.get_json()["username"]
    retrievalInterface = RetrievalInterface()

    try:
        retrievalInterface.register(username, DYNAMO_DB_NAME)
        return json.dumps({"Success": f"User {username} registered successfully"}), 200
    except UserAlreadyExists:
        return json.dumps({"UserTakenError": "Username taken"}), 401
    except ClientError:
        return (
            json.dumps({"InternalError": "Something has gone wrong on our end. Please report"}),
            500,
        )


@app.route("/v1/retrieve/<username>/<stockname>/", methods=["GET"])
def retrieve(username, stockname: str):
    retrievalInterface = RetrievalInterface()
    filenameS3 = f"{username}#{stockname}_stock_data.csv"  # need to think about Rakshil's file formatting here
    try:
        found, content, index = retrievalInterface.getFileFromDynamo(stockname, username, DYNAMO_DB_NAME)

        if found:
            return (
                json.dumps(
                    {
                        "data_source": "yahoo_finance",
                        "dataset_type": "Daily stock data",
                        "dataset_id": "http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2-amazonaws.com",
                        "time_object": {
                            "timestamp": f"{str(datetime.now(timezone('Australia/Sydney'))).split('+')[0]}",
                            "timezone": "GMT+11",
                        },
                        "stock_name": stockname,
                        "events": content,
                    }
                ),
                200,
            )
        else:
            content = retrievalInterface.pull(AWS_S3_BUCKET_NAME, f"{filenameS3}")
            # need to format Rakshil's S3 content format into DynamoDB content
            retrievalInterface.pushToDynamo(stockname, content, username, DYNAMO_DB_NAME)
            found, content, index = retrievalInterface.getFileFromDynamo(stockname, username, DYNAMO_DB_NAME)

            return (
                json.dumps(
                    {
                        "data_source": "yahoo_finance",
                        "dataset_type": "Daily stock data",
                        "dataset_id": "http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2-amazonaws.com",
                        "time_object": {
                            "timestamp": f"{str(datetime.now(timezone('Australia/Sydney'))).split('+')[0]}",
                            "timezone": "GMT+11",
                        },
                        "stock_name": stockname,
                        "events": content,
                    }
                ),
                200,
            )
    except ClientError as e:

        if e.response["Error"]["Code"] == "NoSuchKey":
            return (
                json.dumps(
                    {
                        "StockNotFound": f"It appears that you have do not have access to stock {stockname}."
                        "Ensure you have collected the stock before attempting retrieval"
                    }
                ),
                401,
            )
        else:
            return json.dumps({"InternalError": "Something unexpected went wrong; please report"}), 500
    except UserNotFound:
        return json.dumps({"UserNotFound": "Username not found; ensure you have reigstered"}), 401
    except Exception:
        return json.dumps({"InternalError": "Something unexpected went wrong; please report"}), 500


@app.route("/v1/delete/", methods=["DELETE"])
def delete():
    filename = request.get_json()["filename"]
    username = request.get_json()["username"]

    retrievalInterface = RetrievalInterface()
    try:
        # delete from dynamodb
        retrievalInterface.deleteFromDynamo(filename, username, DYNAMO_DB_NAME)
        return json.dumps({"Success": f"Deleted {filename}"})
    except FileNotFoundError:
        return json.dumps({"FileNotFound": f"No File for stock {filename} exists for deletion"}), 400
    except UserNotFound:
        return json.dumps({"UserNotFound": f"No user with username {username} exists, ensure you have registered"}), 401
    except Exception:
        return json.dumps({"InternalError": "Something has gone wrong on our end, please report"}), 500


@app.route("/v1/list/<username>/", methods=["GET"])
def getAll(username):
    retrievalInterface = RetrievalInterface()
    try:
        return json.dumps({"Success": retrievalInterface.listUserFiles(username, DYNAMO_DB_NAME)})
    except UserNotFound:
        return json.dumps({"UserNotFound": "User does not appear to exist, ensure you have registered"}), 401
    except Exception:
        return json.dumps({"InternalError": "Something has gone wrong on our end, please report"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

# ROUTES TO COMPLETE:
# /retrieve
# /list_files
# /delete
# /update           # more clarifaction would be good

from flask import Flask, request
from RetrievalInterface import RetrievalInterface
import secrets
import sys
app = Flask(__name__)

AWS_S3_BUCKET_NAME = "seng3011-omega-25t1-testing-bucket"
# filename = "test_file.txt"

@app.route('/v1/retrieve', methods=['GET'])
def retrieve():
    filename = request.get_json()['filename']
    retrievalInterface = RetrievalInterface()
    try:
        return retrievalInterface.pull(AWS_S3_BUCKET_NAME, filename)
    except Exception as e:
        sys.stderr.write(f"(RetrievalMicroservice.retrieve) Exception: {e}")

        

@app.route('/v1/delete', methods=['DELETE'])
def delete():
    filename = request.get_json()['filename']
    retrievalInterface =  RetrievalInterface()
    try:
        retrievalInterface.deleteOne(AWS_S3_BUCKET_NAME, filename)
        return f"Deleted {filename}"
    except Exception as e:
        sys.stderr.write(f"(RetrievalMicroservice.delete) Exception: {e}")



if __name__ == "__main__":
    app.run(host ='0.0.0.0', port=5001, debug = True) 
# ROUTES TO COMPLETE:
# /retrieve
# /list_files
# /delete
# /update

from flask import Flask, request
from RetrievalInterface import RetrievalInterface
from secrets import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_S3_BUCKET_NAME, AWS_REGION

app = Flask(__name__)

@app.route('/v1/retrieve', methods=['GET'])
def retrieve():
    filename = request.form.get('filename')
    puller = RetrievalInterface()
    return puller.pull(AWS_S3_BUCKET_NAME, filename)

@app.route('/v1/delete', methods=['DELETE'])
def delete():
    filename = request.form.get('filename')
    deleter =  



if __name__ == "__main__":
    app.run(host ='0.0.0.0', port=5001, debug = True) 
from flask import Flask, jsonify, request
import yfinance as yf
import pandas as pd
import requests
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)


CLIENT_ROLE_ARN = "arn:aws:iam::339712883212:role/sharing-s3-bucket"
CLIENT_BUCKET_NAME = "seng3011-omega-25t1-testing-bucket"
def write_to_client_s3(filename):
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn=CLIENT_ROLE_ARN,
        RoleSessionName="AssumeRoleSession1"
    )
    credentials = assumed_role_object['Credentials']
    s3 = boto3.client(
        's3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    try:
        s3.upload_file(filename, 'seng3011-omega-25t1-testing-bucket' , filename)
        var = s3.get_object(Bucket='seng3011-omega-25t1-testing-bucket', Key=filename)
        object_content = var['Body'].read().decode('utf-8')
        print(object_content)
        return True
    except Exception as e:
        print(f"Error writing to S3: {e}")
        return False
    
    
def search_ticker(company_name):
    """
    Searches for a stock ticker based on a company name using Yahoo Finance's search API.
    """
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if "quotes" in data and len(data["quotes"]) > 0:
                for quote in data["quotes"]:
                    if "symbol" in quote and "isYahooFinance" in quote and quote["isYahooFinance"]:
                        return quote["symbol"] 
        
        return None

    except Exception as e:
        return None
    
def get_stock_data(stock_ticker, company, name, period="1mo"):
    try:
        stock = yf.Ticker(stock_ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return None, None

        hist = hist[["Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]]
        hist.reset_index(inplace=True)
        hist["Date"] = hist["Date"].dt.strftime("%Y-%m-%d")

        file_path = f"{name}#{company}_stock_data.csv"
        hist.to_csv(file_path, index=False)
        
        write_to_client_s3(file_path)

        return file_path, hist.to_dict(orient="records")
    except Exception as e:
        print(f"ERROR in get_stock_data: {e}")
        return None, None

@app.route("/")
def home():
    return "Welcome to the Stock Data API! Use /stockInfo?company=COMPANY_NAME to fetch stock details."

@app.route("/stockInfo")
def stock_info():
    try:
        company_name = request.args.get("company")
        name = request.args.get("name")

        if not company_name:
            return jsonify({"error": "Please provide a company name."}), 400

        company_name = company_name.strip().lower()
        if name:
            name = name.strip().lower()

        stock_ticker = search_ticker(company_name)

        if not stock_ticker:
            return jsonify({"error": f"Could not find a stock ticker for '{company_name}'."}), 404

        file_path, stock_data = get_stock_data(stock_ticker,company_name, name)

        if stock_data is None:
            return jsonify({"error": f"Stock data for '{stock_ticker}' not found or invalid."}), 404

        return jsonify({
            "message": "Stock data retrieved successfully",
            "ticker": stock_ticker,
            "file": file_path,
            "data": stock_data
        })
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/check_stock")
def check_stock():
    company_name = request.args.get("company")
    name = request.args.get("name")

    if not company_name or not name:
        return jsonify({"error": "Please provide both 'company' and 'name'."}), 400

    company_name = company_name.strip().lower()
    name = name.strip().lower()

    # Construct file path (same as in `get_stock_data`)
    file_path = f"{name}#{company_name}_stock_data.csv"

    # Assume Role for S3 access
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn=CLIENT_ROLE_ARN,
        RoleSessionName="AssumeRoleSession1"
    )
    credentials = assumed_role_object['Credentials']
    s3 = boto3.client(
        's3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    try:
        # Check if file exists in S3 bucket
        s3.head_object(Bucket='seng3011-omega-25t1-testing-bucket', Key= f"{name}#{company_name}_stock_data.csv")
        return jsonify({
            "exists": True,
            "message": f"Stock data for {name} for '{company_name}' exists in S3.",
            "file": file_path
        })
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return jsonify({
                "exists": False,
                "message": f"No stock data found for '{company_name}' in S3.",
                "file": file_path
            })
        else:
            return jsonify({"error": f"Error checking S3: {e}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)


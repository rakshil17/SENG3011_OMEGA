from flask import Flask, jsonify, request
import yfinance as yf
import pandas as pd
import requests
import boto3

app = Flask(__name__)

#hwy

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
        headers = {"User-Agent": "Mozilla/5.0"}  # Yahoo Finance sometimes requires a user-agent
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

def get_stock_data(stock_ticker, name, period="1mo"):
    """
    Fetches historical stock data using a valid ticker symbol.
    """
    try:
        stock = yf.Ticker(stock_ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return None, None  

        hist = hist[["Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]]
        hist.reset_index(inplace=True)

        file_path = f"{name}#{stock_ticker}_stock_data.csv"
        hist.to_csv(file_path, index=False)
        
        write_to_client_s3(file_path)

        return file_path, hist.to_dict(orient="records")

    except Exception as e:
        return None, str(e)

@app.route("/")
def home():
    return "Welcome to the Stock Data API! Use /stockInfo?company=COMPANY_NAME to fetch stock details."

@app.route("/stockInfo")
def stock_info():
    company_name = request.args.get("company")
    name = request.args.get("name")

    if not company_name:
        return jsonify({"error": "Please provide a company name."}), 400

    company_name = company_name.strip()

    stock_ticker = search_ticker(company_name)

    if not stock_ticker:
        return jsonify({"error": f"Could not find a stock ticker for '{company_name}'."}), 404

    file_path, stock_data = get_stock_data(stock_ticker, name)

    if stock_data is None:
        return jsonify({"error": f"Stock data for '{stock_ticker}' not found or invalid."}), 404

    return jsonify({
        "message": "Stock data retrieved successfully",
        "ticker": stock_ticker,
        "file": file_path,
        "data": stock_data
    })

if __name__ == "__main__":
    app.run(debug=True)


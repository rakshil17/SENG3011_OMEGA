import pytest
import json
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from dataCol import app, write_to_client_s3, search_ticker, get_stock_data  # Import the functions
import pandas as pd

@pytest.fixture
def client():
    """Creates a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# --------------- TEST SUITE FOR /check_stock ---------------
@pytest.mark.usefixtures("client")
class TestCheckStock:
    """Tests for the /check_stock endpoint."""

    def test_check_stock_exists(self, client, mocker):
        """Test if check_stock correctly detects an existing file in S3."""
        mock_s3 = mocker.patch("boto3.client")  # Mock S3 client
        mock_s3.return_value.head_object.return_value = {}  # Simulate file exists

        response = client.get("/check_stock?company=apple&name=john")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["exists"] is True
        assert "Stock data for" in data["message"]
        assert "exists in S3" in data["message"]

    def test_check_stock_not_exists(self, client, mocker):
        """Test if check_stock correctly handles missing files in S3."""
        mock_s3 = mocker.patch("boto3.client")  
        error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
        mock_s3.return_value.head_object.side_effect = ClientError(error_response, "HeadObject")

        response = client.get("/check_stock?company=apple&name=john")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["exists"] is False
        assert "No stock data found" in data["message"]

    def test_check_stock_invalid_permissions(self, client, mocker):
        """Test if check_stock correctly handles permission errors."""
        mock_s3 = mocker.patch("boto3.client")  
        error_response = {"Error": {"Code": "403", "Message": "Forbidden"}}
        mock_s3.return_value.head_object.side_effect = ClientError(error_response, "HeadObject")

        response = client.get("/check_stock?company=apple&name=john")
        data = json.loads(response.data)

        assert response.status_code == 500
        assert "Error checking S3" in data["error"]


# --------------- TEST SUITE FOR /stockInfo ---------------
@pytest.mark.usefixtures("client")
class TestStockInfo:
    """Tests for the /stockInfo endpoint."""

    def test_stock_info_success(self, client, mocker):
        """Test if stockInfo returns correct stock data."""
        mocker.patch("dataCol.search_ticker", return_value="AAPL")  
        mocker.patch("dataCol.get_stock_data", return_value=("apple_stock_data.csv", [{"Date": "2024-03-01", "Close": 150.5}]))  

        response = client.get("/stockInfo?company=apple&name=john")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["message"] == "Stock data retrieved successfully"
        assert data["ticker"] == "AAPL"

    def test_stock_info_error_handling(self, client, mocker):
        """Test stockInfo handles unexpected API failures."""
        mocker.patch("dataCol.search_ticker", side_effect=Exception("API error"))

        response = client.get("/stockInfo?company=apple&name=john")
        data = json.loads(response.data)

        assert response.status_code == 500
        assert "Unexpected error" in data["error"]


# --------------- TESTS FOR MISSING FUNCTIONS ---------------
@pytest.mark.usefixtures("client")
class TestWriteToClientS3:
    """Tests for `write_to_client_s3()` function."""

    @patch("boto3.client")
    def test_write_to_s3_success(self, mock_boto):
        """Test writing a file to S3 successfully."""
        mock_s3 = mock_boto.return_value
        mock_s3.upload_file.return_value = None  # Simulate successful upload
        mock_s3.get_object.return_value = {"Body": MagicMock(read=lambda: b"file content")}

        result = write_to_client_s3("test.csv")
        assert result is True

    @patch("boto3.client")
    def test_write_to_s3_failure(self, mock_boto):
        """Test handling failure when writing to S3."""
        mock_s3 = mock_boto.return_value
        mock_s3.upload_file.side_effect = Exception("S3 error")

        result = write_to_client_s3("test.csv")
        assert result is False


@pytest.mark.usefixtures("client")
class TestSearchTicker:
    """Tests for `search_ticker()` function."""

    @patch("dataCol.requests.get")
    def test_search_ticker_found(self, mock_get):
        """Test search_ticker when it finds a ticker."""
        mock_get.return_value.status_code = 200  # Simulate successful API call
        mock_get.return_value.json.return_value = {
            "quotes": [{"symbol": "AAPL", "isYahooFinance": True}]
        }
        result = search_ticker("apple")
        assert result == "AAPL"

    @patch("dataCol.requests.get")
    def test_search_ticker_not_found(self, mock_get):
        """Test search_ticker when no ticker is found."""
        mock_get.return_value.json.return_value = {"quotes": []}
        result = search_ticker("unknown")
        assert result is None


@pytest.mark.usefixtures("client")
class TestGetStockData:
    """Tests for `get_stock_data()` function."""

    @patch("dataCol.yf.Ticker")
    @patch("dataCol.write_to_client_s3", return_value=True)
    def test_get_stock_data_success(self, mock_write_s3, mock_ticker):
        """Test get_stock_data returns correct data."""
        mock_stock = mock_ticker.return_value
        mock_stock.history.return_value = pd.DataFrame(
            {
                "Open": [150.0], "High": [155.0], "Low": [148.0], "Close": [152.0],
                "Volume": [10000], "Dividends": [0.0], "Stock Splits": [0.0]
            },
            index=pd.to_datetime(["2024-03-01"])
        ).rename_axis("Date")

        file_path, data = get_stock_data("AAPL", "apple", "john")

        print("DEBUG: file_path =", file_path)
        print("DEBUG: data =", data)

        assert file_path is not None, "Expected file_path, but got None"
        assert file_path == "john#apple_stock_data.csv"
        assert len(data) == 1
        assert data[0]["Date"] == "2024-03-01"


    @patch("dataCol.yf.Ticker")
    def test_get_stock_data_empty(self, mock_ticker):
        """Test get_stock_data when no stock data is available."""
        mock_stock = mock_ticker.return_value
        mock_stock.history.return_value = pd.DataFrame() 

        file_path, data = get_stock_data("AAPL", "apple", "john")
        assert file_path is None
        assert data is None


# --------------- TEST FOR HOME ROUTE ---------------
def test_home_route(client):
    """Test the home page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Stock Data API" in response.data.decode()


# --------------- RUN TEST COVERAGE ---------------
# Run: pytest --cov=dataCol --cov-report=term-missing

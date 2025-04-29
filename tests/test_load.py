import pytest
from unittest import mock
from utils.load import DataLoader, DataLoaderException
import pandas as pd

# Dokumentasi singkat tentang pengujian
# File ini berisi unit tests untuk DataLoader class, khususnya fungsi load_data yang bertanggung jawab
# untuk menyimpan data ke berbagai tujuan penyimpanan seperti CSV, Google Sheets, dan PostgreSQL.

@pytest.fixture
def mock_dataframe():
    # Fixture untuk menyediakan dataframe mock
    data = {
        'timestamp': ['2025-04-28', '2025-04-27'],
        'value': [100, 150]
    }
    return pd.DataFrame(data)

@pytest.fixture
def data_loader():
    # Fixture untuk menyediakan instance DataLoader
    return DataLoader(credentials_path="fake_path.json")

def test_save_to_csv_success(mock_dataframe, data_loader):
    # Menguji fungsi save_to_csv berhasil menyimpan data ke file CSV
    with mock.patch("pandas.DataFrame.to_csv") as mock_to_csv:
        mock_to_csv.return_value = None  # Mock agar tidak menulis ke file
        result = data_loader.save_to_csv(mock_dataframe, "test.csv")
        assert result is True

def test_save_to_csv_failure(mock_dataframe, data_loader):
    # Menguji fungsi save_to_csv menangani error dengan benar
    with mock.patch("pandas.DataFrame.to_csv") as mock_to_csv:
        mock_to_csv.side_effect = Exception("Gagal menulis file")
        with pytest.raises(DataLoaderException):
            data_loader.save_to_csv(mock_dataframe, "test.csv")

def test_save_to_gsheets_success(mock_dataframe, data_loader):
    with mock.patch("googleapiclient.discovery.build") as mock_build:
        mock_sheets_service = mock.MagicMock()
        mock_sheets = mock.MagicMock()
        mock_values = mock.MagicMock()
        mock_execute = {"spreadsheetId": "fake_spreadsheet_id"}

        # Setup method chaining mocks
        mock_values.update.return_value.execute.return_value = mock_execute
        mock_sheets.values.return_value = mock_values
        mock_sheets_service.spreadsheets.return_value = mock_sheets
        mock_build.return_value = mock_sheets_service

        # Mock credentials with with_scopes chainable
        with mock.patch("google.oauth2.service_account.Credentials.from_service_account_file") as mock_credentials:
            # Step 1: Setup base credential instance
            mock_credentials_instance = mock.MagicMock()
            mock_credentials_instance.with_scopes.return_value = mock_credentials_instance

            # Step 2: Setup authorize() -> object with .credentials.universe_domain
            mock_authorized_http = mock.MagicMock()
            mock_authorized_http.credentials.universe_domain = "googleapis.com"

            # Step 3: Simulate .authorize() to return the object above
            mock_credentials_instance.authorize.return_value = mock_authorized_http
            mock_credentials.return_value = mock_credentials_instance

def test_save_to_gsheets_failure(mock_dataframe, data_loader):
    # Menguji fungsi save_to_gsheets menangani error dengan benar
    with mock.patch("googleapiclient.discovery.build") as mock_build:
        mock_build.side_effect = Exception("Gagal koneksi ke Google Sheets")
        result = data_loader.save_to_gsheets(mock_dataframe, "fake_spreadsheet_id")
        assert result is None

def test_save_to_postgresql_success(mock_dataframe, data_loader):
    # Menguji fungsi save_to_postgresql berhasil menyimpan data ke PostgreSQL
    with mock.patch("sqlalchemy.create_engine") as mock_create_engine:
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Mock connect dan to_sql
        mock_connection = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_dataframe.to_sql = mock.MagicMock(return_value=None)

        result = data_loader.save_to_postgresql(
            mock_dataframe,
            table_name="test_table",
            host="localhost",
            database="test_db",
            user="test_user",
            password="test_password"
        )
        assert result is True

def test_save_to_postgresql_failure(mock_dataframe, data_loader):
    # Menguji fungsi save_to_postgresql menangani error dengan benar
    with mock.patch("sqlalchemy.create_engine") as mock_create_engine:
        mock_create_engine.side_effect = Exception("Koneksi gagal")
        result = data_loader.save_to_postgresql(
            mock_dataframe,
            table_name="test_table",
            host="localhost",
            database="test_db",
            user="test_user",
            password="test_password"
        )
        assert result is False

def test_load_data_success(mock_dataframe, data_loader):
    # Menguji fungsi load_data yang menggabungkan penyimpanan ke CSV, Google Sheets, dan PostgreSQL
    with mock.patch.object(data_loader, "save_to_csv") as mock_save_to_csv, \
         mock.patch.object(data_loader, "save_to_gsheets") as mock_save_to_gsheets, \
         mock.patch.object(data_loader, "save_to_postgresql") as mock_save_to_postgresql:
        
        # Setup mock return values
        mock_save_to_csv.return_value = True
        mock_save_to_gsheets.return_value = "https://docs.google.com/spreadsheets/d/fake_spreadsheet_id"
        mock_save_to_postgresql.return_value = True
        
        pg_config = {
            'table_name': 'test_table',
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password',
            'port': '5432'
        }
        
        result = data_loader.load_data(mock_dataframe, "test.csv", "fake_spreadsheet_id", pg_config)
        
        # Verifikasi hasil
        assert result['csv_status'] is True
        assert result['sheets_url'] == "https://docs.google.com/spreadsheets/d/fake_spreadsheet_id"
        assert result['postgresql_status'] is True

def test_load_data_failure(mock_dataframe, data_loader):
    # Menguji kegagalan pada load_data ketika salah satu fungsi gagal
    with mock.patch.object(data_loader, "save_to_csv") as mock_save_to_csv, \
         mock.patch.object(data_loader, "save_to_gsheets") as mock_save_to_gsheets, \
         mock.patch.object(data_loader, "save_to_postgresql") as mock_save_to_postgresql:
        
        # Setup mock return values dengan satu fungsi gagal
        mock_save_to_csv.return_value = False
        mock_save_to_gsheets.return_value = None
        mock_save_to_postgresql.return_value = False
        
        pg_config = {
            'table_name': 'test_table',
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password',
            'port': '5432'
        }
        
        result = data_loader.load_data(mock_dataframe, "test.csv", "fake_spreadsheet_id", pg_config)
        
        # Verifikasi hasil
        assert result['csv_status'] is False
        assert result['sheets_url'] is None
        assert result['postgresql_status'] is False
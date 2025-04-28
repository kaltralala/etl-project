import pandas as pd
import logging
from typing import Optional, Dict
from sqlalchemy import create_engine
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoaderException(Exception):
    """Custom exception untuk error pada proses loading data"""
    pass

class DataLoader:
    """Class untuk menyimpan data ke berbagai tujuan penyimpanan"""
    
    def __init__(self, credentials_path: str):
        """
        Inisialisasi DataLoader
        
        Args:
            credentials_path: Path ke file credentials Google Sheets
        """
        self.credentials_path = credentials_path
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

    def save_to_csv(self, df: pd.DataFrame, output_path: str) -> bool:
        """Menyimpan data ke CSV file"""
        try:
            df.to_csv(output_path, index=False)
            logger.info(f"Data berhasil disimpan ke {output_path}")
            return True
        except Exception as e:
            error_msg = f"Gagal menyimpan ke CSV: {str(e)}"
            logger.error(error_msg)
            raise DataLoaderException(error_msg)

    def save_to_gsheets(self, df: pd.DataFrame, spreadsheet_id: str) -> Optional[str]:
        """
        Menyimpan data ke Google Sheets yang sudah ada
        """
        try:
            # Buat salinan DataFrame untuk menghindari perubahan pada data asli
            df_sheets = df.copy()
            
            # Konversi kolom timestamp menjadi format string
            if 'timestamp' in df_sheets.columns:
                df_sheets['timestamp'] = df_sheets['timestamp'].astype(str)
            
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Buat service untuk Sheets API
            sheets_service = build('sheets', 'v4', credentials=credentials)
            
            # Siapkan data untuk update
            values = [df_sheets.columns.values.tolist()] + df_sheets.values.tolist()
            body = {
                'values': values
            }
            
            # Update cells di spreadsheet
            sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='A1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            logger.info(f"Data berhasil disimpan ke Google Sheets: {sheet_url}")
            return sheet_url
            
        except Exception as e:
            logger.error(f"Gagal menyimpan ke Google Sheets: {str(e)}")
            return None

    def save_to_postgresql(self, 
                         df: pd.DataFrame, 
                         table_name: str,
                         host: str,
                         database: str,
                         user: str,
                         password: str,
                         port: str = "5432") -> bool:
        """Menyimpan data ke PostgreSQL database menggunakan SQLAlchemy"""
        try:
            conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            engine = create_engine(conn_string)
            
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists='replace',
                index=False
            )
            
            logger.info(f"Data berhasil disimpan ke PostgreSQL table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Gagal menyimpan ke PostgreSQL: {str(e)}")
            return False

    def load_data(self, 
                 df: pd.DataFrame,
                 csv_path: str,
                 spreadsheet_id: str,
                 pg_config: Dict) -> Dict:
        """Menyimpan data ke semua tujuan penyimpanan"""
        results = {
            'csv_status': False,
            'sheets_url': None,
            'postgresql_status': False
        }
        
        results['csv_status'] = self.save_to_csv(df, csv_path)
        results['sheets_url'] = self.save_to_gsheets(df, spreadsheet_id)
        results['postgresql_status'] = self.save_to_postgresql(
            df,
            table_name=pg_config.get('table_name'),
            host=pg_config.get('host'),
            database=pg_config.get('database'),
            user=pg_config.get('user'),
            password=pg_config.get('password'),
            port=pg_config.get('port', '5432')
        )
        
        return results
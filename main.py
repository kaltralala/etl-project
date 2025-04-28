from utils.extract import ProductExtractor
from utils.transform import DataTransformer
from utils.load import DataLoader
import logging
import os
import pandas as pd

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Fungsi utama untuk menjalankan proses ETL"""
    try:
        # EXTRACT
        logger.info("Memulai proses ekstraksi data...")
        base_url = "https://fashion-studio.dicoding.dev"
        extractor = ProductExtractor(base_url)
        
        df_raw = extractor.extract_all_pages()
        raw_path = "raw_fashion_data.csv"
        df_raw.to_csv(raw_path, index=False)
        logger.info(f"Berhasil mengekstrak {len(df_raw)} produk ke {raw_path}")
        
        # TRANSFORM
        logger.info("Memulai proses transformasi data...")
        transformer = DataTransformer()
        df_clean = transformer.transform_data(df_raw)
        
        clean_path = "clean_fashion_data.csv"
        df_clean.to_csv(clean_path, index=False)
        logger.info(f"Berhasil menyimpan {len(df_clean)} data bersih ke {clean_path}")
        
        # LOAD
        logger.info("Memulai proses penyimpanan data...")
        
        # Konfigurasi PostgreSQL
        pg_config = {
            'host': 'localhost',
            'database': 'fashion_db',
            'user': 'developer',
            'password': 'supersecretpassword',
            'table_name': 'fashion_products',
            'port': '5432'
        }
        
        # Masukkan ID spreadsheet
        SPREADSHEET_ID = "17OXUOijS_TmLZkpL6ogCFVzTk_OBznHdtrwPbcCIzdM"

        # Inisialisasi DataLoader dengan credentials yang sudah ada
        credentials_path = os.path.join(os.path.dirname(__file__), 'google-sheets-api.json')
        loader = DataLoader(credentials_path=credentials_path)
        
        # Proses loading data
        results = loader.load_data(
            df=df_clean,
            csv_path=clean_path,
            spreadsheet_id=SPREADSHEET_ID,  # Gunakan spreadsheet ID yang sudah ada
            pg_config=pg_config
        )
        
        # Log hasil penyimpanan
        if results['csv_status']:
            logger.info(f"Data berhasil disimpan ke CSV: {clean_path}")
        
        if results['sheets_url']:
            logger.info(f"Data berhasil disimpan ke Google Sheets: {results['sheets_url']}")
        
        if results['postgresql_status']:
            logger.info("Data berhasil disimpan ke PostgreSQL")

    except Exception as e:
        logger.error(f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    main()
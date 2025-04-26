from utils.extract import ProductExtractor, ProductExtractorException
from utils.transform import DataTransformer
import logging
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
        
    except ProductExtractorException as e:
        logger.error(f"Gagal melakukan ekstraksi data: {str(e)}")
    except Exception as e:
        logger.error(f"Terjadi kesalahan tidak terduga: {str(e)}")

if __name__ == "__main__":
    main()
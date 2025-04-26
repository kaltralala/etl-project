from utils.extract import ProductExtractor, ProductExtractorException
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Fungsi utama untuk menjalankan proses ekstraksi data"""
    try:
        # URL website target
        base_url = "https://fashion-studio.dicoding.dev"
        
        # Inisialisasi ekstractor
        extractor = ProductExtractor(base_url)
        
        # Proses ekstraksi data
        df = extractor.extract_all_pages()
        
        # Simpan hasil ke CSV
        output_path = "raw_fashion_data.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Berhasil mengekstrak {len(df)} produk ke {output_path}")
        
    except ProductExtractorException as e:
        logger.error(f"Gagal melakukan ekstraksi data: {str(e)}")
    except Exception as e:
        logger.error(f"Terjadi kesalahan tidak terduga: {str(e)}")

if __name__ == "__main__":
    main()
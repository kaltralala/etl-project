import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from typing import Optional, List, Dict, Union
from requests.exceptions import RequestException
from datetime import datetime  # Tambahkan impor ini

# Konfigurasi logging untuk monitoring proses scraping
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductExtractorException(Exception):
    """Custom exception untuk ProductExtractor"""
    pass

class ProductExtractor:
    """Kelas untuk mengekstrak data produk fashion dari website."""
    
    def __init__(self, base_url: str):
        """
        Inisialisasi ProductExtractor.
        
        Args:
            base_url: URL dasar website yang akan di-scrape
            
        Raises:
            ValueError: Jika base_url kosong atau tidak valid
        """
        if not base_url:
            raise ValueError("Base URL tidak boleh kosong")
        
        try:
            self.base_url = base_url.rstrip('/')
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        except AttributeError as e:
            raise ValueError(f"Base URL tidak valid: {str(e)}")

    def get_page_url(self, page: int) -> str:
        """
        Membuat URL untuk setiap halaman.
        
        Args:
            page: Nomor halaman yang akan diakses
            
        Returns:
            URL lengkap untuk halaman tertentu
            
        Raises:
            ValueError: Jika nomor halaman kurang dari 1
        """
        if page < 1:
            raise ValueError("Nomor halaman harus lebih besar dari 0")
            
        try:
            if page == 1:
                return self.base_url
            return f"{self.base_url}/page{page}"
        except Exception as e:
            raise ProductExtractorException(f"Gagal membuat URL halaman: {str(e)}")

    def extract_price(self, element: BeautifulSoup) -> str:
        """
        Mengekstrak harga produk dari elemen HTML.
        
        Args:
            element: Element BeautifulSoup yang berisi informasi harga
            
        Returns:
            Harga produk dalam format string
            
        Raises:
            ProductExtractorException: Jika gagal mengekstrak harga
        """
        try:
            price_span = element.select_one('span.price')
            if price_span:
                return price_span.text.strip()
            
            price_p = element.select_one('p.price')
            if price_p:
                return price_p.text.strip()
            
            return "Price Unavailable"
        except Exception as e:
            raise ProductExtractorException(f"Gagal mengekstrak harga: {str(e)}")

    def extract_rating(self, element: BeautifulSoup) -> str:
        """
        Mengekstrak rating produk dari elemen HTML.
        
        Args:
            element: Element BeautifulSoup yang berisi informasi rating
            
        Returns:
            Rating produk dalam format string
            
        Raises:
            ProductExtractorException: Jika gagal mengekstrak rating
        """
        try:
            rating_elem = element.select_one('p:-soup-contains("Rating:")')
            if rating_elem:
                return rating_elem.text.replace('Rating:', '').strip()
            return "Not Rated"
        except Exception as e:
            raise ProductExtractorException(f"Gagal mengekstrak rating: {str(e)}")

    def extract_product_data(self, page: int) -> List[Dict[str, Union[str, float]]]:
        """
        Mengekstrak data produk dari satu halaman.
        
        Args:
            page: Nomor halaman yang akan di-scrape
            
        Returns:
            List berisi data produk dalam bentuk dictionary
            
        Raises:
            RequestException: Jika gagal mengakses halaman
            ProductExtractorException: Jika gagal mengekstrak data
        """
        try:
            url = self.get_page_url(page)
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = soup.select('div.collection-card')
            
            data = []
            for product in products:
                try:
                    details = product.select_one('div.product-details')
                    if not details:
                        continue

                    product_data = {
                        'title': details.select_one('h3.product-title').text.strip(),
                        'price': self.extract_price(details),
                        'rating': self.extract_rating(details),
                        'colors': next((p.text.strip() for p in details.select('p') if 'Colors' in p.text), 'No Color Info'),
                        'size': next((p.text.replace('Size:', '').strip() for p in details.select('p') if 'Size:' in p.text), 'No Size Info'),
                        'gender': next((p.text.replace('Gender:', '').strip() for p in details.select('p') if 'Gender:' in p.text), 'No Gender Info'),
                        'timestamp': datetime.now().isoformat()  # Tambahkan timestamp
                    }
                    data.append(product_data)
                except Exception as e:
                    logger.warning(f"Gagal mengekstrak produk pada halaman {page}: {str(e)}")
                    continue

            return data

        except RequestException as e:
            logger.error(f"Error saat mengakses halaman {page}: {str(e)}")
            return []
        except Exception as e:
            raise ProductExtractorException(f"Gagal mengekstrak data halaman {page}: {str(e)}")

    def extract_all_pages(self, start_page: int = 1, end_page: int = 50, 
                         max_products: int = 1000) -> pd.DataFrame:
        """
        Mengekstrak data dari semua halaman yang ditentukan.
        
        Args:
            start_page: Halaman awal untuk scraping
            end_page: Halaman akhir untuk scraping
            max_products: Jumlah maksimum produk yang akan diambil
            
        Returns:
            DataFrame pandas berisi semua data produk
            
        Raises:
            ValueError: Jika parameter tidak valid
            ProductExtractorException: Jika gagal mengekstrak data
        """
        try:
            if start_page < 1 or end_page < start_page or max_products < 1:
                raise ValueError("Parameter halaman atau jumlah produk tidak valid")

            all_products = []
            current_page = start_page

            while current_page <= end_page and len(all_products) < max_products:
                logger.info(f"Sedang mengekstrak halaman {current_page}")
                try:
                    products = self.extract_product_data(current_page)
                    
                    if not products:
                        break

                    all_products.extend(products)
                    if len(all_products) >= max_products:
                        all_products = all_products[:max_products]
                        break

                    current_page += 1
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error pada halaman {current_page}: {str(e)}")
                    current_page += 1

            if not all_products:
                raise ProductExtractorException("Tidak ada data yang berhasil diekstrak")

            return pd.DataFrame(all_products)

        except Exception as e:
            raise ProductExtractorException(f"Gagal mengekstrak semua halaman: {str(e)}")

def main():
    base_url = "https://fashion-studio.dicoding.dev"
    extractor = ProductExtractor(base_url)
    
    try:
        df = extractor.extract_all_pages()
        output_path = "raw_fashion_data.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Extracted {len(df)} products to {output_path}")
    except ProductExtractorException as e:
        logger.error(f"Gagal mengekstrak data: {str(e)}")

if __name__ == "__main__":
    main()
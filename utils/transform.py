import pandas as pd
import logging
from typing import Dict, List, Union
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self):
        self.dirty_patterns = {
            "title": ["Unknown Product"],  # Sesuaikan dengan nama kolom di CSV
            "rating": ["Invalid Rating / 5", "Not Rated"],
            "price": ["Price Unavailable", None]
        }
        self.exchange_rate = 16000

    def clean_price(self, price: str) -> float:
        """Membersihkan dan mengkonversi harga ke Rupiah menggunakan str.extract dan replace"""
        try:
            if pd.isna(price) or price == "Price Unavailable":
                return None
            # Menggunakan replace untuk membersihkan karakter $ dan koma
            clean_price = str(price).replace('$', '').replace(',', '')
            # Menggunakan str.extract untuk mengambil angka
            price_value = pd.Series(clean_price).str.extract(r'([\d.]+)').iloc[0, 0]
            return float(price_value) * self.exchange_rate
        except (ValueError, AttributeError):
            return None

    def clean_rating(self, rating: str) -> float:
        """Membersihkan rating menggunakan str.extract"""
        try:
            if pd.isna(rating) or rating in ["Invalid Rating / 5", "Not Rated"]:
                return None
            # Menggunakan str.extract untuk mengambil angka rating
            rating_value = pd.Series(rating).str.extract(r'([\d.]+)').iloc[0, 0]
            return float(rating_value)
        except (ValueError, AttributeError):
            return None

    def clean_colors(self, colors: str) -> int:
        """Membersihkan colors menggunakan str.extract"""
        try:
            if pd.isna(colors):
                return None
            # Menggunakan str.extract untuk mengambil angka
            color_value = pd.Series(colors).str.extract(r'(\d+)').iloc[0, 0]
            return int(color_value)
        except (ValueError, AttributeError):
            return None

    def clean_size_gender(self, value: str, column: str) -> str:
        """Membersihkan Size dan Gender menggunakan replace dan strip"""
        try:
            if pd.isna(value):
                return None
            # Menggunakan replace dan strip untuk membersihkan string
            return str(value).replace(f"{column}:", "").strip()
        except AttributeError:
            return None

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Melakukan transformasi data menggunakan semua metode yang disarankan"""
        try:
            logger.info("Memulai proses transformasi data...")
            # Buat copy DataFrame
            df_clean = df.copy()
            
            # Bersihkan data invalid menggunakan replace
            for column, patterns in self.dirty_patterns.items():
                df_clean[column] = df_clean[column].replace(patterns, None)
            
            # Transformasi setiap kolom
            logger.info("Mengubah format kolom...")
            df_clean['price'] = df_clean['price'].apply(self.clean_price)
            df_clean['rating'] = df_clean['rating'].apply(self.clean_rating)
            df_clean['colors'] = df_clean['colors'].apply(self.clean_colors)
            df_clean['size'] = df_clean['size'].apply(lambda x: self.clean_size_gender(x, 'Size'))
            df_clean['gender'] = df_clean['gender'].apply(lambda x: self.clean_size_gender(x, 'Gender'))
            
            # Hapus duplikat menggunakan drop_duplicates
            logger.info("Menghapus data duplikat...")
            df_clean = df_clean.drop_duplicates()
            
            # Hapus nilai null menggunakan dropna
            logger.info("Menghapus nilai null...")
            df_clean = df_clean.dropna()
            
            # Reset index
            df_clean = df_clean.reset_index(drop=True)
            
            logger.info(f"Transformasi selesai. {len(df_clean)} baris data valid tersisa.")
            return df_clean
            
        except Exception as e:
            logger.error(f"Error saat transformasi data: {str(e)}")
            raise
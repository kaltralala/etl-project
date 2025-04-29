# tests/test_transform.py

"""
Unit Testing untuk modul utils/transform.py

Tujuan:
- Memastikan fungsi transformasi data bekerja sesuai spesifikasi.
- Memverifikasi bahwa format output benar.
- Menangani kasus error dan edge case dengan baik.
- Mencapai coverage minimal 80–100%.
"""

import pytest
import pandas as pd
import pandas.testing as pdt
import math
from utils.transform import DataTransformer

# Membuat fixture untuk instance DataTransformer
@pytest.fixture
def transformer():
    return DataTransformer()

# Fixture untuk dummy dataframe sebelum transformasi
@pytest.fixture
def dummy_df():
    return pd.DataFrame({
        'title': ['T-shirt 2', 'Hoodie 3', 'Pants 4', 'Outerwear 5', 'Jacket 6'],
        'price': ['$102.15', '$496.88', '$467.31', '$321.59', '$153.37'],
        'rating': ['⭐ 3.9 / 5', '⭐ 4.8 / 5', '⭐ 3.3 / 5', '⭐ 3.5 / 5', '⭐ 3.3 / 5'],
        'colors': ['3 Colors', '3 Colors', '3 Colors', '3 Colors', '3 Colors'],
        'size': ['M', 'L', 'XL', 'XXL', 'S'],
        'gender': ['Women', 'Unisex', 'Men', 'Women', 'Unisex']
    })

# Fixture untuk expected dataframe setelah transformasi
@pytest.fixture
def expected_df():
    return pd.DataFrame({
        'title': ['t-shirt 2', 'hoodie 3', 'pants 4', 'outerwear 5', 'jacket 6'],
        'price': [1634400.0, 7950080.0, 7476960.0, 5145440.0, 2453920.0],
        'rating': [3.9, 4.8, 3.3, 3.5, 3.3],
        'colors': [3, 3, 3, 3, 3],
        'size': ['M', 'L', 'XL', 'XXL', 'S'],
        'gender': ['women', 'unisex', 'men', 'women', 'unisex']
    })

# Test fungsi clean_price
def test_clean_price_valid(transformer):
    input_price = '$1,200.50'
    expected = 1200.5 * 16000  # Karena ada exchange rate dikali 16000
    result = transformer.clean_price(input_price)
    assert result == expected, f"Expected {expected}, got {result}"

def test_clean_price_invalid(transformer):
    input_price = 'invalid_price'
    result = transformer.clean_price(input_price)
    assert pd.isna(result), f"Expected NaN for invalid price input"

# Test fungsi clean_rating
def test_clean_rating_valid(transformer):
    input_rating = '4.5 out of 5'
    expected = 4.5
    result = transformer.clean_rating(input_rating)
    assert result == expected, f"Expected {expected}, got {result}"

def test_clean_rating_invalid(transformer):
    input_rating = 'bad_rating'
    result = transformer.clean_rating(input_rating)
    assert pd.isna(result), f"Expected NaN for invalid rating input"

# Test fungsi clean_colors
def test_clean_colors_valid(transformer):
    assert transformer.clean_colors('8 colors') == 8

def test_clean_colors_invalid(transformer):
    assert transformer.clean_colors(None) is None
    assert transformer.clean_colors('') is None

# Test fungsi clean_size_gender
def test_clean_size_gender_valid(transformer):
    assert transformer.clean_size_gender('Size: Small', 'Size') == 'Small'
    assert transformer.clean_size_gender('Gender: Unisex', 'Gender') == 'Unisex'

def test_clean_size_gender_invalid(transformer):
    assert transformer.clean_size_gender(None, 'Size') is None

# Test utama untuk fungsi transform_data
def test_transform_data_success(transformer, dummy_df):
    transformed_df = transformer.transform_data(dummy_df)

    expected_df = pd.DataFrame({
        'title': ['t-shirt 2', 'hoodie 3', 'pants 4', 'outerwear 5', 'jacket 6'],
        'price': [1634400.0, 7950080.0, 7476960.0, 5145440.0, 2453920.0],
        'rating': [3.9, 4.8, 3.3, 3.5, 3.3],
        'colors': [3, 3, 3, 3, 3],
        'size': ['M', 'L', 'XL', 'XXL', 'S'],
        'gender': ['women', 'unisex', 'men', 'women', 'unisex']
    })

# Test jika input dataframe kosong
def test_transform_empty_dataframe(transformer):
    empty_df = pd.DataFrame(columns=['title', 'rating', 'price', 'colors', 'size', 'gender'])
    transformed_df = transformer.transform_data(empty_df)
    assert transformed_df.empty, "Expected transformed DataFrame to be empty"

# Test handling error saat ada kolom hilang
def test_transform_missing_columns(transformer):
    incomplete_df = pd.DataFrame({
        'title': ['Produk X'],
        'price': ['$30.00']
        # Kolom lain tidak ada
    })
    with pytest.raises(Exception):
        transformer.transform_data(incomplete_df)

# Test clean_price untuk kasus angka yang sangat besar
def test_clean_price_large_value(transformer):
    large_price = '$1,000,000.00'
    assert transformer.clean_price(large_price) == 16000000000.0

# Test edge case clean_rating string aneh
def test_clean_rating_strange_input(transformer):
    result = transformer.clean_rating("Unknown rating")
    assert pd.isna(result), f"Expected NaN, got {result}"

# Test edge case clean_colors string tidak biasa
def test_clean_colors_strange_input(transformer):
    strange_colors = 'several colors'
    assert transformer.clean_colors(strange_colors) is None

# Test edge case clean_size_gender string tanpa keyword
def test_clean_size_gender_no_keyword(transformer):
    input_value = 'Medium'
    assert transformer.clean_size_gender(input_value, 'Size') == 'Medium'

# Test edge
def test_clean_price_none(transformer):
    input_price = None
    result = transformer.clean_price(input_price)
    assert pd.isna(result)

# Test edge
def test_clean_rating_none(transformer):
    input_rating = None
    result = transformer.clean_rating(input_rating)
    assert pd.isna(result)
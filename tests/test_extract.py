"""
test_extract.py

Tujuan:
- Menguji fungsi-fungsi dalam ProductExtractor untuk memastikan:
    - Proses extract berjalan sesuai ekspektasi.
    - Struktur dan format data yang dikembalikan sudah benar.
    - Error handling bekerja dengan baik pada kondisi gagal koneksi, timeout, atau data tidak ditemukan.

Framework: pytest
Teknik: mocking koneksi eksternal menggunakan unittest.mock
Coverage target: 80-100%
"""

import pytest
from utils import extract
from unittest.mock import patch, MagicMock
from utils.extract import ProductExtractor, ProductExtractorException
import pandas as pd
from requests.exceptions import RequestException

# Fixture dasar untuk membuat instance ProductExtractor
@pytest.fixture
def extractor():
    return ProductExtractor(base_url="https://fashion-studio.dicoding.dev")

# Contoh HTML dummy untuk produk
PRODUCT_HTML = """
<div class="collection-card">
  <div class="product-details">
    <h3 class="product-title">T-Shirt Unisex</h3>
    <span class="price">$20</span>
    <p>Rating: 4.5</p>
    <p>Colors: Red, Blue</p>
    <p>Size: M</p>
    <p>Gender: Unisex</p>
  </div>
</div>
"""

@patch('utils.extract.ProductExtractor')
def test_main_success(mock_extractor_class):
    mock_extractor = MagicMock()
    mock_df = MagicMock()
    mock_df.to_csv.return_value = None
    mock_df.__len__.return_value = 5

    mock_extractor.extract_all_pages.return_value = mock_df
    mock_extractor_class.return_value = mock_extractor

    with patch('utils.extract.logger') as mock_logger:
        extract.main()
        mock_df.to_csv.assert_called_once_with("raw_fashion_data.csv", index=False)
        mock_logger.info.assert_called_with("Extracted 5 products to raw_fashion_data.csv")

@patch('utils.extract.ProductExtractor')
def test_main_exception(mock_extractor_class):
    mock_extractor = MagicMock()
    mock_extractor.extract_all_pages.side_effect = extract.ProductExtractorException("mock error")
    mock_extractor_class.return_value = mock_extractor

    with patch('utils.extract.logger') as mock_logger:
        extract.main()
        mock_logger.error.assert_called_with("Gagal mengekstrak data: mock error")

# Test URL generator
def test_get_page_url_valid(extractor):
    # Menguji URL halaman 1 dan halaman selain 1
    assert extractor.get_page_url(1) == "https://fashion-studio.dicoding.dev"
    assert extractor.get_page_url(2) == "https://fashion-studio.dicoding.dev/page2"

def test_get_page_url_invalid(extractor):
    # Menguji ValueError saat page kurang dari 1
    with pytest.raises(ValueError):
        extractor.get_page_url(0)

# Test extract_price function
def test_extract_price_success(extractor):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(PRODUCT_HTML, "html.parser")
    details = soup.select_one('div.product-details')
    price = extractor.extract_price(details)
    assert price == "$20"

def test_extract_price_unavailable(extractor):
    from bs4 import BeautifulSoup
    html_no_price = '<div class="product-details"></div>'
    soup = BeautifulSoup(html_no_price, "html.parser")
    details = soup.select_one('div.product-details')
    price = extractor.extract_price(details)
    assert price == "Price Unavailable"

def test_extract_price_exception(extractor):
    class BadElement:
        def select_one(self, _):
            raise Exception("mocked exception")
    with pytest.raises(ProductExtractorException):
        extractor.extract_price(BadElement())

# Test extract_rating function
def test_extract_rating_success(extractor):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(PRODUCT_HTML, "html.parser")
    details = soup.select_one('div.product-details')
    rating = extractor.extract_rating(details)
    assert rating == "4.5"

def test_extract_rating_not_found(extractor):
    from bs4 import BeautifulSoup
    html_no_rating = '<div class="product-details"></div>'
    soup = BeautifulSoup(html_no_rating, "html.parser")
    details = soup.select_one('div.product-details')
    rating = extractor.extract_rating(details)
    assert rating == "Not Rated"

def test_extract_rating_exception(extractor):
    class BadElement:
        def select_one(self, _):
            raise Exception("mocked exception")
    with pytest.raises(ProductExtractorException):
        extractor.extract_rating(BadElement())

# Test extract_product_data normal
@patch('utils.extract.requests.get')
def test_extract_product_data_success(mock_get, extractor):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = PRODUCT_HTML
    mock_get.return_value = mock_response

    products = extractor.extract_product_data(1)
    assert isinstance(products, list)
    assert len(products) == 1
    assert products[0]['title'] == "T-Shirt Unisex"
    assert products[0]['price'] == "$20"
    assert products[0]['rating'] == "4.5"
    assert products[0]['colors'] == "Colors: Red, Blue"
    assert products[0]['size'] == "M"
    assert products[0]['gender'] == "Unisex"

# Test extract_product_data handling RequestException
@patch('utils.extract.requests.get')
def test_extract_product_data_request_exception(mock_get, extractor):
    mock_get.side_effect = RequestException("Connection error")
    products = extractor.extract_product_data(1)
    assert products == []

@patch('utils.extract.requests.get')
def test_extract_product_data_internal_parse_error(mock_get, extractor):
    bad_html = """
    <div class="collection-card">
        <div class="product-details"> <!-- h3 is missing to cause .text access error -->
            <span class="price">$20</span>
        </div>
    </div>
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = bad_html
    mock_get.return_value = mock_response

    # Tidak error total, tapi hanya skip produk
    products = extractor.extract_product_data(1)
    assert products == []

@patch('utils.extract.requests.get')
def test_extract_product_data_general_exception(mock_get, extractor):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = PRODUCT_HTML
    mock_get.return_value = mock_response

    # Patch method yang dipakai agar langsung raise Exception
    with patch.object(extractor, 'get_page_url', side_effect=Exception("generic failure")):
        with pytest.raises(ProductExtractorException):
            extractor.extract_product_data(1)

# Test extract_all_pages normal
@patch('utils.extract.requests.get')
def test_extract_all_pages_success(mock_get, extractor):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = PRODUCT_HTML
    mock_get.return_value = mock_response

    df = extractor.extract_all_pages(start_page=1, end_page=2, max_products=2)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ['title', 'price', 'rating', 'colors', 'size', 'gender', 'timestamp']

# Test extract_all_pages with no products extracted
@patch('utils.extract.requests.get')
def test_extract_all_pages_no_products(mock_get, extractor):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = "<html></html>"  # No collection-card div
    mock_get.return_value = mock_response

    with pytest.raises(ProductExtractorException):
        extractor.extract_all_pages(start_page=1, end_page=2, max_products=2)

# Test extract_all_pages invalid parameters
def test_extract_all_pages_invalid_params(extractor):
    with pytest.raises(ProductExtractorException):
        extractor.extract_all_pages(start_page=5, end_page=4, max_products=0)

# Test custom exception raised if URL base salah
def test_invalid_base_url():
    with pytest.raises(ValueError):
        ProductExtractor(base_url=None)

# Edge Case: Handling AttributeError in URL building
def test_get_page_url_attribute_error():
    with pytest.raises(ValueError):
        ProductExtractor(base_url=None)
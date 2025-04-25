import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

def fetching_content(url):
    session = requests.Session()
    response = session.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Gagal request {url}: {e}")
        return None

def extract_product_data(card):
    title = card.find('h3', class_='product-title')
    price = card.find('span', class_='price')
    details = card.find_all('p', style=True)

    # Default values
    title_text = title.text.strip() if title else "N/A"
    price_text = price.text.strip() if price else "N/A"
    colors = size = gender = rating = "N/A"

    for detail in details:
        text = detail.text.lower()
        if "color" in text:
            colors = text.replace("colors", "").strip()
        elif "size" in text:
            size = text.replace("size:", "").strip()
        elif "gender" in text:
            gender = text.replace("gender:", "").strip().capitalize()
        elif "rating" in text:
            rating = text.replace("rating:", "").strip()

    return {
        "Title": title_text,
        "Price": price_text,
        "Colors": colors,
        "Size": size,
        "Gender": gender,
        "Rating": rating
    }

def scrape_products(base_url, max_page=50, delay=1):
    data = []

    for page in range(1, max_page + 1):
        url = base_url.format(page)
        print(f"[+] Scraping {url}")
        content = fetching_content(url)
        if not content:
            break

        soup = BeautifulSoup(content, "html.parser")
        cards = soup.find_all('div', class_='collection-card')

        if not cards:
            print(f"[!] Tidak ada produk di halaman {page}. Stop scraping.")
            break

        for card in cards:
            product = extract_product_data(card)
            data.append(product)

        time.sleep(delay)

    return data

def main():
    BASE_URL = "https://fashion-studio.dicoding.dev/page{}"
    produk = scrape_products(BASE_URL, max_page=50)
    df = pd.DataFrame(produk)
    df.to_csv("produk_fashion.csv", index=False)
    print("[✓] Data berhasil disimpan ke 'produk_fashion.csv'.")

if __name__ == "__main__":
    main()
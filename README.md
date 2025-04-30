# 🧵 ETL Pipeline untuk Data Produk Kompetitor - Fashion Studio

Proyek ini dibuat untuk mendukung kebutuhan analisis kompetitor pada perusahaan retail fashion. Fokus utama proyek ini adalah membangun pipeline **ETL (Extract, Transform, Load)** untuk mengambil data produk dari situs web [Fashion Studio](https://fashion-studio.dicoding.dev), membersihkannya, dan menyimpannya ke berbagai media (CSV, Google Sheets, dan PostgreSQL) agar siap digunakan oleh tim data science untuk keperluan analisis lanjutan.

---

## 🔧 Teknologi & Library yang Digunakan

- **Python 3.10**
- `requests` & `beautifulsoup4` – Web scraping HTML
- `pandas` – Transformasi data
- `sqlalchemy` & `psycopg2-binary` – Koneksi ke PostgreSQL
- `google-api-python-client` & `google-auth` – Integrasi Google Sheets API
- `pytest-cov` – Pengujian unit

---

## 🗂️ Struktur Proyek

```bash
etl-project/
├── tests/
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
├── utils/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── main.py
├── requirements.txt
├── submission.txt
├── clean_fashion_data.csv
├── raw_fashion_data.csv
├── google-sheets-api.json
└── README.md

---

## 🚀 Cara Menjalankan Proyek
1. Clone repositori dan pasang dependensi

git clone https://github.com/Kaltralala/etl-project.git
cd etl-project
pip install -r requirements.txt

2. Jalankan pipeline ETL

python main.py

## 📤 Output Pipeline

Pipeline ini menghasilkan output pada tiga media:

    raw_fashion_data.csv – Data mentah hasil web scraping

    clean_fashion_data.csv – Data bersih dan siap pakai

    Google Sheets – Data otomatis diunggah menggunakan API Google Sheets

    PostgreSQL – Data dimuat ke dalam tabel di database PostgreSQL

## ✅ Pengujian

Tersedia unit test untuk setiap tahap ETL. Jalankan dengan:

pytest --cov=utils tests/

## 👨‍💻 Kontributor

Haykal Maulana Rulian
GitHub: Kaltralala
LinkedIn

## 📄 Lisensi

Proyek ini dibuat untuk tujuan pembelajaran dan submission di Dicoding. Seluruh data dan nama bersifat fiktif.
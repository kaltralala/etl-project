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
```
---

## 🚀 Cara Menjalankan Proyek

### 1. Clone repositori dan pasang dependensi
```bash
git clone https://github.com/Kaltralala/etl-project.git
cd etl-project
pip install -r requirements.txt
```

### 2. Jalankan Pipeline ETL
Pipeline utama dijalankan melalui file `main.py` yang mengatur alur ETL secara terstruktur:
```bash
python main.py
```
---

## 📤 Output Pipeline

Setelah pipeline dijalankan, kamu akan mendapatkan output berikut:

- `raw_fashion_data.csv` – Data hasil ekstraksi mentah dari website
- `clean_fashion_data.csv` – Data yang telah dibersihkan dan siap dianalisis
- **Google Sheets** – Data diunggah ke spreadsheet Google melalui integrasi API
- **PostgreSQL** – Data dimuat ke dalam tabel di database PostgreSQL untuk keperluan lanjutan

---

## 🧑‍💻 Kontributor
- Nama: Haykal Maulana Rulian
- GitHub: [Kaltralala](https://github.com/Kaltralala)
- LinkedIn: [haykalmr](https://www.linkedin.com/in/haykalmr/)
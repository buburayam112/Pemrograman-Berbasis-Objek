# POS App - Point of Sale Application

Aplikasi Point of Sale (POS) dan manajemen inventaris berbasis desktop yang dibangun menggunakan Python, Tkinter, dan SQLite dengan arsitektur MVC.

## Fitur

- 🔐 **Role-Based Access Control** — Login untuk Admin dan Kasir
- 📦 **Manajemen Produk** — CRUD lengkap untuk data produk
- 📊 **Manajemen Stok** — Pengelolaan stok otomatis
- 🛒 **Kasir** — Proses transaksi penjualan
- 📈 **Laporan** — Laporan penjualan dan dashboard

## Struktur Project

```
pos_app/
├── main.py              # Entry point aplikasi
├── database.py          # Konfigurasi database SQLite
├── models/              # Model layer (MVC)
│   ├── base_model.py
│   ├── product_model.py
│   ├── stock_model.py
│   ├── transaction_model.py
│   └── user_model.py
├── views/               # View layer (MVC)
│   ├── base_view.py
│   ├── dashboard_view.py
│   ├── kasir_view.py
│   ├── login_view.py
│   ├── product_view.py
│   ├── report_view.py
│   └── stock_view.py
└── utils/               # Utility & validators
    └── validators.py
```

## Teknologi

- **Python 3** — Bahasa pemrograman
- **Tkinter** — GUI framework
- **SQLite** — Database

## Cara Menjalankan

```bash
python main.py
```

## Prinsip OOP

Aplikasi ini menerapkan prinsip OOP:
- **Encapsulation** — Data model terenkapsulasi
- **Inheritance** — Base class untuk model dan view
- **Polymorphism** — Override method pada subclass
- **DRY** — Kode reusable melalui base classes

# POS Kasir & Manajemen Stok Gudang

Aplikasi desktop Point of Sale (POS) untuk transaksi penjualan dan manajemen stok gudang, dibangun dengan Python, Tkinter, dan SQLite. Proyek ini dikembangkan sebagai tugas akhir mata kuliah Pemrograman Berorientasi Objek / Rekayasa Perangkat Lunak, dengan penerapan arsitektur MVC (Model-View-Controller) dan prinsip OOP secara ketat.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

---

## Daftar Isi

- [Tentang Proyek](#tentang-proyek)
- [Fitur Utama](#fitur-utama)
- [Tampilan Aplikasi](#tampilan-aplikasi)
- [Arsitektur dan Teknologi](#arsitektur-dan-teknologi)
- [Struktur Folder](#struktur-folder)
- [Skema Database](#skema-database)
- [Instalasi dan Menjalankan](#instalasi-dan-menjalankan)
- [Akun Default](#akun-default)
- [Penerapan Konsep OOP](#penerapan-konsep-oop)
- [Kontributor](#kontributor)

---

## Tentang Proyek

Aplikasi ini membantu proses operasional toko/gudang skala kecil-menengah, mencakup pencatatan transaksi penjualan (kasir), pengelolaan data produk, mutasi stok masuk/keluar, hingga pelaporan penjualan — seluruhnya dalam satu jendela aplikasi bergaya Single Page Application (SPA) desktop tanpa jendela pop-up yang berlebihan.

## Fitur Utama

- **Login dan Role Management** — akses berbeda untuk Admin dan Kasir.
- **Manajemen Produk** — CRUD penuh (tambah, lihat, ubah, hapus) data barang dan kategori.
- **Modul Kasir** — pencatatan transaksi penjualan, kalkulasi otomatis total dan kembalian, pengurangan stok otomatis saat transaksi disimpan.
- **Manajemen Stok Gudang** — pencatatan stok masuk (restock) dan stok keluar (retur/rusak), tersinkron real-time dengan data produk.
- **Laporan Penjualan** — rekap transaksi per periode, total omzet, dan peringatan produk dengan stok menipis.
- **Exception Handling** — seluruh operasi database dibungkus try-except-finally dengan notifikasi messagebox agar aplikasi tidak crash.

## Tampilan Aplikasi

| Login | Dashboard |
|---|---|
| (tambahkan screenshot di sini) | (tambahkan screenshot di sini) |

| Modul Kasir | Manajemen Produk |
|---|---|
| (tambahkan screenshot di sini) | (tambahkan screenshot di sini) |

| Manajemen Stok | Laporan Penjualan |
|---|---|
| (tambahkan screenshot di sini) | (tambahkan screenshot di sini) |

Simpan screenshot di folder `assets/screenshots/` lalu ganti placeholder di atas dengan `![nama](assets/screenshots/nama-file.png)`.

## Arsitektur dan Teknologi

| Komponen | Teknologi |
|---|---|
| Bahasa | Python 3.10+ |
| GUI | Tkinter dan ttk (Treeview, Combobox) |
| Database | SQLite 3 (`pos_database.db`) |
| Pola Arsitektur | MVC (Model - View - Controller) |
| Paradigma | OOP (Encapsulation, Inheritance, Polymorphism) + DRY |

## Struktur Folder

```
pos_app/
├── main.py                 # Controller utama & routing antar frame
├── database.py              # Koneksi SQLite & inisialisasi tabel
├── models/
│   ├── base_model.py
│   ├── product_model.py
│   ├── transaction_model.py
│   ├── stock_model.py
│   └── user_model.py
├── views/
│   ├── base_view.py
│   ├── login_view.py
│   ├── dashboard_view.py
│   ├── kasir_view.py
│   ├── product_view.py
│   ├── stock_view.py
│   └── report_view.py
├── utils/
│   └── validators.py
└── pos_database.db          # dibuat otomatis saat pertama dijalankan
```

## Skema Database

Aplikasi menggunakan 6 tabel utama: `users`, `categories`, `products`, `transactions`, `transaction_items`, dan `stock_log`. Detail lengkap struktur kolom dapat dilihat pada `database.py`.

## Instalasi dan Menjalankan

```bash
# 1. Clone repository
git clone https://github.com/username/pos-kasir-stok-gudang.git
cd pos-kasir-stok-gudang

# 2. (Opsional) Buat virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Jalankan aplikasi (tidak ada dependency eksternal, hanya modul bawaan Python)
python main.py
```

Pastikan Python 3.10+ sudah terpasang. Modul `tkinter` dan `sqlite3` sudah termasuk dalam instalasi Python standar.

## Akun Default

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Kasir | `kasir` | `kasir123` |

## Penerapan Konsep OOP

- **Encapsulation** — atribut koneksi database dan data internal model bersifat privat, hanya bisa diakses lewat method publik (`get_all()`, `add()`, `update()`, `delete()`).
- **Inheritance** — seluruh model (`ProductModel`, `TransactionModel`, `StockModel`, `UserModel`) mewarisi `BaseModel`; `Admin` dan `Kasir` mewarisi `User`; seluruh frame mewarisi `BaseFrame`.
- **Polymorphism** — method `validate()` di-override berbeda pada setiap model sesuai aturan bisnisnya; method `get_permissions()` mengembalikan hak akses berbeda antara `Admin` dan `Kasir`.
- **DRY** — seluruh query CRUD berulang ditangani lewat method generik di `BaseModel`, bukan ditulis ulang di setiap model.

## Kontributor

| Nama | NIM |
|---|---|
| Abiyyu Farras | 221230029 |
| Syafiq Indirwan | 241230065 |
| Iksan Nugraha | 241230057 |

## Lisensi

Proyek ini dibuat untuk keperluan akademik tugas akhir mata kuliah Pemrograman Berbasis Objek.

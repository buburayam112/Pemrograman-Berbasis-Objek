# POS Kasir & Manajemen Stok Gudang

Aplikasi desktop Point of Sale (POS) untuk transaksi penjualan dan manajemen stok gudang, dibangun dengan Python, Tkinter, dan SQLite. Proyek ini dikembangkan sebagai tugas akhir mata kuliah Pemrograman Berorientasi Objek / Rekayasa Perangkat Lunak, dengan penerapan arsitektur MVC (Model-View-Controller) dan prinsip OOP secara ketat.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

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
- [Lisensi](#lisensi)

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
| <img width="1370" height="910" alt="image" src="[https://github.com/user-attachments/assets/7867d108-ad51-4ddc-9853-fcfecf463674](https://uploads.onecompiler.io/44vrs5jr5/1784533749037/Screenshot%202026-07-20%20144301.png)" />
) | (<img width="1913" height="1026" alt="image" src="[https://github.com/user-attachments/assets/f5a53351-9b44-4823-954d-f382454294ed](https://uploads.onecompiler.io/44vrs5jr5/1784533756511/Screenshot%202026-07-20%20144404.png)" />
) |

| Modul Kasir | Manajemen Produk |
|---|---|
|[ (<img width="1907" height="1057" alt="image" src="[https://github.com/user-attachments/assets/8db9e03e-ebe4-40f0-a277-cc404626b899](https://uploads.onecompiler.io/44vrs5jr5/1784533767321/Screenshot%202026-07-20%20144453.png)" />
)](https://uploads.onecompiler.io/44vrs5jr5/1784533816060/Screenshot%202026-07-20%20145001.png) | (<img width="1882" height="1055" alt="image" src="[https://github.com/user-attachments/assets/654b06d5-a756-4567-8901-3b87357ab6f4](https://uploads.onecompiler.io/44vrs5jr5/1784533778110/Screenshot%202026-07-20%20144520.png)" />
) |

| Manajemen Stok | Laporan Penjualan |
|---|---|
| |[ (<img width="1907" height="1057" alt="image" src="[[https://github.com/user-attachments/assets/8db9e03e-ebe4-40f0-a277-cc404626b899](https://uploads.onecompiler.io/44vrs5jr5/1784533767321/Screenshot%202026-07-20%20144453.png)](https://uploads.onecompiler.io/44vrs5jr5/1784533614091/Screenshot%202026-07-20%20144548.png)" />
)] |[ (<img width="1907" height="1057" alt="image" src="https://uploads.onecompiler.io/44vrs5jr5/1784533816060/Screenshot%202026-07-20%20145001.png" />
)] |

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


Proyek ini dibuat untuk keperluan akademik tugas akhir mata kuliah Pemrograman Berbasis Objek.

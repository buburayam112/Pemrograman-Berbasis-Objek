"""
report_view.py — Halaman laporan penjualan.

Menampilkan laporan transaksi dengan filter tanggal,
total omzet, dan peringatan produk stok menipis.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from views.base_view import BaseFrame, COLORS, FONTS
from utils.validators import validate_date_format


class ReportFrame(BaseFrame):
    """
    Frame laporan penjualan.
    
    Fitur:
    - Filter tanggal (dari-sampai)
    - Treeview laporan transaksi
    - Total omzet
    - Tabel produk stok menipis (baris merah)
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="📈  Laporan Penjualan")
        self._build_ui()

    def _build_ui(self):
        """Bangun seluruh komponen UI laporan."""
        content = self._create_content_frame()
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # ── Panel Filter ──
        filter_card = self._create_card(content, title="Filter Laporan",
                                         row=0, column=0, sticky="ew")
        filter_card.grid_columnconfigure(5, weight=1)

        tk.Label(filter_card, text="Dari Tanggal:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=2, column=0, sticky="w", padx=(15, 5), pady=5)

        self._entry_from = tk.Entry(filter_card, font=FONTS["body"], width=12,
                                     relief="solid", bd=1)
        self._entry_from.grid(row=2, column=1, padx=(0, 10), pady=5)

        tk.Label(filter_card, text="Sampai:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=2, column=2, padx=(0, 5), pady=5)

        self._entry_to = tk.Entry(filter_card, font=FONTS["body"], width=12,
                                   relief="solid", bd=1)
        self._entry_to.grid(row=2, column=3, padx=(0, 10), pady=5)

        self._create_button(filter_card, "🔍  Tampilkan",
                            self._on_filter, "primary",
                            row=2, column=4, padx=5, pady=5)
        self._create_button(filter_card, "📅  Hari Ini",
                            self._filter_today, "secondary",
                            row=2, column=5, padx=5, pady=5)
        self._create_button(filter_card, "📅  7 Hari",
                            self._filter_week, "secondary",
                            row=2, column=6, padx=5, pady=5)
        self._create_button(filter_card, "📅  30 Hari",
                            self._filter_month, "secondary",
                            row=2, column=7, padx=(5, 15), pady=5)

        # Label total omzet
        omzet_frame = tk.Frame(filter_card, bg=COLORS["bg_card"])
        omzet_frame.grid(row=3, column=0, columnspan=8, sticky="ew",
                          padx=15, pady=(5, 15))

        tk.Label(omzet_frame, text="Total Omzet:", font=FONTS["subtitle"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=0, column=0, padx=(0, 10))

        self._lbl_omzet = tk.Label(
            omzet_frame, text="Rp 0",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["success"]
        )
        self._lbl_omzet.grid(row=0, column=1)

        tk.Label(omzet_frame, text="  |  Jumlah Transaksi:", font=FONTS["body"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=0, column=2, padx=(20, 5))

        self._lbl_count = tk.Label(
            omzet_frame, text="0",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["accent"]
        )
        self._lbl_count.grid(row=0, column=3)

        # ── Tabs: Transaksi & Stok Menipis ──
        notebook = ttk.Notebook(content)
        notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        # Tab 1: Laporan Transaksi
        tab_trx = tk.Frame(notebook, bg=COLORS["bg_card"])
        notebook.add(tab_trx, text="  📋 Laporan Transaksi  ")
        tab_trx.grid_columnconfigure(0, weight=1)
        tab_trx.grid_rowconfigure(0, weight=1)

        trx_columns = [
            ("no", "No. Transaksi"),
            ("tanggal", "Tanggal"),
            ("kasir", "Kasir"),
            ("total", "Total Belanja"),
            ("bayar", "Bayar"),
            ("kembalian", "Kembalian"),
        ]
        self._tree_trx = self._create_treeview(
            tab_trx, trx_columns,
            column_widths={"no": 140, "tanggal": 140, "kasir": 100,
                           "total": 120, "bayar": 120, "kembalian": 120},
            height=12
        )
        self._tree_trx.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Tab 2: Stok Menipis
        tab_stock = tk.Frame(notebook, bg=COLORS["bg_card"])
        notebook.add(tab_stock, text="  ⚠️ Stok Menipis  ")
        tab_stock.grid_columnconfigure(0, weight=1)
        tab_stock.grid_rowconfigure(0, weight=1)

        stock_columns = [
            ("kode", "Kode"),
            ("nama", "Nama Barang"),
            ("kategori", "Kategori"),
            ("stok", "Stok Saat Ini"),
            ("minimum", "Stok Minimum"),
            ("selisih", "Kekurangan"),
        ]
        self._tree_stock = self._create_treeview(
            tab_stock, stock_columns,
            column_widths={"kode": 90, "nama": 180, "kategori": 120,
                           "stok": 100, "minimum": 100, "selisih": 100},
            height=12
        )
        self._tree_stock.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Set default tanggal
        today = datetime.now()
        self._entry_from.insert(0, (today - timedelta(days=30)).strftime("%Y-%m-%d"))
        self._entry_to.insert(0, today.strftime("%Y-%m-%d"))

    def _on_filter(self):
        """Tampilkan laporan berdasarkan filter tanggal."""
        try:
            date_from = validate_date_format(self._entry_from.get())
            date_to = validate_date_format(self._entry_to.get())
        except ValueError as e:
            messagebox.showwarning("Format Tanggal", str(e))
            return

        self._load_transactions(date_from, date_to)

    def _filter_today(self):
        """Filter laporan hari ini."""
        today = datetime.now().strftime("%Y-%m-%d")
        self._entry_from.delete(0, tk.END)
        self._entry_to.delete(0, tk.END)
        self._entry_from.insert(0, today)
        self._entry_to.insert(0, today)
        self._load_transactions(today, today)

    def _filter_week(self):
        """Filter laporan 7 hari terakhir."""
        today = datetime.now()
        week_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        self._entry_from.delete(0, tk.END)
        self._entry_to.delete(0, tk.END)
        self._entry_from.insert(0, week_ago)
        self._entry_to.insert(0, today_str)
        self._load_transactions(week_ago, today_str)

    def _filter_month(self):
        """Filter laporan 30 hari terakhir."""
        today = datetime.now()
        month_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        self._entry_from.delete(0, tk.END)
        self._entry_to.delete(0, tk.END)
        self._entry_from.insert(0, month_ago)
        self._entry_to.insert(0, today_str)
        self._load_transactions(month_ago, today_str)

    def _load_transactions(self, date_from, date_to):
        """Muat data transaksi ke Treeview."""
        self._tree_trx.delete(*self._tree_trx.get_children())
        try:
            from models.transaction_model import TransactionModel
            trx_model = TransactionModel()
            transactions = trx_model.get_by_date_range(date_from, date_to)

            total_omzet = 0
            for i, t in enumerate(transactions):
                tags = ("alt_row",) if i % 2 == 1 else ()
                self._tree_trx.insert("", "end", values=(
                    t["no_transaksi"],
                    t["tanggal"],
                    t["kasir_name"] or "-",
                    self._format_currency(t["total_belanja"]),
                    self._format_currency(t["bayar"]),
                    self._format_currency(t["kembalian"])
                ), tags=tags)
                total_omzet += t["total_belanja"]

            self._lbl_omzet.config(text=self._format_currency(total_omzet))
            self._lbl_count.config(text=str(len(transactions)))

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat laporan: {e}")

    def _load_low_stock(self):
        """Muat produk stok menipis ke tab kedua."""
        self._tree_stock.delete(*self._tree_stock.get_children())
        try:
            from models.product_model import ProductModel
            product_model = ProductModel()
            low_stock = product_model.get_low_stock()

            for p in low_stock:
                selisih = p["stok_minimum"] - p["stok"]
                self._tree_stock.insert("", "end", values=(
                    p["kode_barang"],
                    p["nama_barang"],
                    p["nama_kategori"] or "-",
                    p["stok"],
                    p["stok_minimum"],
                    f"-{selisih}"
                ), tags=("low_stock",))

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data stok: {e}")

    def refresh_data(self):
        """Refresh data saat frame ditampilkan."""
        self._on_filter()
        self._load_low_stock()

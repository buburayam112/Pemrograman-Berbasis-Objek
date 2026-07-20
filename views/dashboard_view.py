"""
dashboard_view.py — Halaman dashboard ringkasan aplikasi POS.

Menampilkan statistik harian (total produk, transaksi, omzet)
dan peringatan produk dengan stok menipis.
"""

import tkinter as tk
from tkinter import ttk
from views.base_view import BaseFrame, COLORS, FONTS


class DashboardFrame(BaseFrame):
    """
    Frame dashboard utama.
    
    Menampilkan:
    - Kartu statistik (total produk, transaksi hari ini, omzet)
    - Tabel produk stok menipis (warning)
    - Tombol quick-access ke modul utama
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="📊  Dashboard")
        self._build_ui()

    def _build_ui(self):
        """Bangun seluruh komponen UI dashboard."""
        content = self._create_content_frame()
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(2, weight=1)

        # ── Baris 1: Kartu Statistik ──
        self._card_produk = self._create_stat_card(
            content, "📦 Total Produk", "0", COLORS["accent"], row=0, col=0
        )
        self._card_trx = self._create_stat_card(
            content, "🧾 Transaksi Hari Ini", "0", COLORS["success"], row=0, col=1
        )
        self._card_omzet = self._create_stat_card(
            content, "💰 Omzet Hari Ini", "Rp 0", COLORS["warning"], row=0, col=2
        )

        # ── Baris 2: Quick Access Buttons ──
        btn_frame = tk.Frame(content, bg=COLORS["bg_main"])
        btn_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(15, 10))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        btn_frame.grid_columnconfigure(3, weight=1)

        self._create_button(btn_frame, "🛒  Buka Kasir",
                            lambda: self._controller.show_frame("kasir"),
                            "primary", row=0, column=0, padx=5)
        self._create_button(btn_frame, "📦  Kelola Produk",
                            lambda: self._controller.show_frame("produk"),
                            "secondary", row=0, column=1, padx=5)
        self._create_button(btn_frame, "📋  Kelola Stok",
                            lambda: self._controller.show_frame("stok"),
                            "secondary", row=0, column=2, padx=5)
        self._create_button(btn_frame, "📈  Lihat Laporan",
                            lambda: self._controller.show_frame("laporan"),
                            "secondary", row=0, column=3, padx=5)

        # ── Baris 3: Tabel Stok Menipis ──
        warning_card = self._create_card(
            content, title="⚠️  Produk Stok Menipis",
            row=2, column=0, colspan=3, pady=(10, 5)
        )
        warning_card.grid_columnconfigure(0, weight=1)
        warning_card.grid_rowconfigure(2, weight=1)

        columns = [
            ("kode", "Kode"),
            ("nama", "Nama Barang"),
            ("kategori", "Kategori"),
            ("stok", "Stok"),
            ("minimum", "Minimum"),
        ]
        self._tree_low = self._create_treeview(
            warning_card, columns,
            column_widths={"kode": 100, "nama": 200, "kategori": 120,
                           "stok": 80, "minimum": 80},
            height=8
        )
        self._tree_low.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15),
                             columnspan=10)

        # ── Info User ──
        self._lbl_user = tk.Label(
            content, text="",
            font=FONTS["small"],
            bg=COLORS["bg_main"], fg=COLORS["text_muted"],
            anchor="w"
        )
        self._lbl_user.grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 0))

    def _create_stat_card(self, parent, title, value, color, row, col):
        """
        Buat kartu statistik individual.
        
        Returns:
            dict: {'title': Label, 'value': Label} untuk update dinamis
        """
        card = tk.Frame(parent, bg=COLORS["bg_card"],
                        relief="solid", bd=1,
                        highlightbackground=COLORS["border"],
                        highlightthickness=1)
        card.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        card.grid_columnconfigure(0, weight=1)

        # Color bar di atas
        bar = tk.Frame(card, bg=color, height=4)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)

        lbl_title = tk.Label(
            card, text=title,
            font=FONTS["body"],
            bg=COLORS["bg_card"], fg=COLORS["text_muted"]
        )
        lbl_title.grid(row=1, column=0, padx=15, pady=(12, 2))

        lbl_value = tk.Label(
            card, text=value,
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["bg_card"], fg=color
        )
        lbl_value.grid(row=2, column=0, padx=15, pady=(2, 15))

        return {"title": lbl_title, "value": lbl_value}

    def refresh_data(self):
        """Refresh semua data statistik dashboard."""
        try:
            # Total produk
            from models.product_model import ProductModel
            product_model = ProductModel()
            total_produk = product_model.count()
            self._card_produk["value"].config(text=str(total_produk))

            # Transaksi hari ini
            from models.transaction_model import TransactionModel
            trx_model = TransactionModel()
            summary = trx_model.get_today_summary()
            self._card_trx["value"].config(text=str(summary["total_trx"]))
            self._card_omzet["value"].config(
                text=self._format_currency(summary["total_omzet"])
            )

            # Produk stok menipis
            low_stock = product_model.get_low_stock()
            self._tree_low.delete(*self._tree_low.get_children())
            for item in low_stock:
                self._tree_low.insert("", "end", values=(
                    item["kode_barang"],
                    item["nama_barang"],
                    item["nama_kategori"] or "-",
                    item["stok"],
                    item["stok_minimum"]
                ), tags=("low_stock",))

            # Info user
            user = self._controller.current_user
            if user:
                self._lbl_user.config(
                    text=f"Login sebagai: {user.username} ({user.role.upper()})"
                )

        except Exception as e:
            print(f"Error refresh dashboard: {e}")

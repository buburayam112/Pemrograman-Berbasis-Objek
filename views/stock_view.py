"""
stock_view.py — Halaman manajemen stok gudang.

Menampilkan form stok masuk/keluar dan riwayat mutasi stok
dengan filter jenis (masuk/keluar/semua).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseFrame, COLORS, FONTS
from utils.validators import validate_positive_integer, validate_not_empty


class StockFrame(BaseFrame):
    """
    Frame manajemen stok gudang.
    
    Fitur:
    - Form stok masuk (restock) dan stok keluar (retur/rusak)
    - Treeview riwayat mutasi stok dengan filter
    - Sinkronisasi instan ke tabel products
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="📋  Manajemen Stok Gudang")
        self._build_ui()

    def _build_ui(self):
        """Bangun seluruh komponen UI stok."""
        content = self._create_content_frame()
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # ── Panel Form Mutasi Stok ──
        form_card = self._create_card(content, title="Form Mutasi Stok",
                                       row=0, column=0, sticky="ew")
        form_card.grid_columnconfigure(1, weight=1)
        form_card.grid_columnconfigure(3, weight=1)

        # Row 2: Pilih Produk
        tk.Label(form_card, text="Produk:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"],
                 anchor="w").grid(row=2, column=0, sticky="w", padx=(15, 5), pady=3)

        self._combo_produk = ttk.Combobox(
            form_card, font=FONTS["body"], width=35, state="readonly"
        )
        self._combo_produk.grid(row=2, column=1, sticky="ew", padx=(5, 15), 
                                 pady=3, columnspan=3)
        self._combo_produk.bind("<<ComboboxSelected>>", self._on_product_select)

        # Info stok saat ini
        self._lbl_stok_info = tk.Label(
            form_card, text="Stok saat ini: -",
            font=FONTS["body"], bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        )
        self._lbl_stok_info.grid(row=3, column=0, columnspan=4, 
                                  sticky="w", padx=15, pady=(0, 5))

        # Row 4: Jenis + Jumlah
        tk.Label(form_card, text="Jenis:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"],
                 anchor="w").grid(row=4, column=0, sticky="w", padx=(15, 5), pady=3)

        self._combo_jenis = ttk.Combobox(
            form_card, font=FONTS["body"], width=15, state="readonly",
            values=["masuk", "keluar"]
        )
        self._combo_jenis.grid(row=4, column=1, sticky="w", padx=(5, 15), pady=3)
        self._combo_jenis.set("masuk")

        _, self._entry_jumlah = self._create_label_entry(
            form_card, "Jumlah:", 4, 2, 10)

        # Row 5: Keterangan
        tk.Label(form_card, text="Keterangan:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"],
                 anchor="w").grid(row=5, column=0, sticky="w", padx=(15, 5), pady=3)

        self._entry_ket = tk.Entry(form_card, font=FONTS["body"], width=40,
                                    relief="solid", bd=1)
        self._entry_ket.grid(row=5, column=1, sticky="ew", padx=(5, 15),
                              pady=3, columnspan=3)

        # Row 6: Tombol
        btn_frame = tk.Frame(form_card, bg=COLORS["bg_card"])
        btn_frame.grid(row=6, column=0, columnspan=4, pady=(10, 15), padx=15,
                       sticky="w")

        self._create_button(btn_frame, "📥  Proses Stok Masuk",
                            lambda: self._process_stock("masuk"), "success",
                            row=0, column=0, padx=(0, 5))
        self._create_button(btn_frame, "📤  Proses Stok Keluar",
                            lambda: self._process_stock("keluar"), "warning",
                            row=0, column=1, padx=5)
        self._create_button(btn_frame, "🔄  Bersihkan",
                            self._clear_form, "secondary",
                            row=0, column=2, padx=5)

        # ── Panel Riwayat Mutasi ──
        log_card = self._create_card(content, title="Riwayat Mutasi Stok",
                                      row=1, column=0, pady=(10, 5))
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(3, weight=1)

        # Filter bar
        filter_frame = tk.Frame(log_card, bg=COLORS["bg_card"])
        filter_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10),
                          columnspan=10)

        tk.Label(filter_frame, text="Filter:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=0, column=0, padx=(0, 5))

        self._combo_filter = ttk.Combobox(
            filter_frame, font=FONTS["body"], width=12, state="readonly",
            values=["Semua", "Masuk", "Keluar"]
        )
        self._combo_filter.grid(row=0, column=1, padx=(0, 10))
        self._combo_filter.set("Semua")
        self._combo_filter.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Treeview
        columns = [
            ("tanggal", "Tanggal"),
            ("kode", "Kode"),
            ("nama", "Nama Barang"),
            ("jenis", "Jenis"),
            ("jumlah", "Jumlah"),
            ("keterangan", "Keterangan"),
        ]
        self._tree_log = self._create_treeview(
            log_card, columns,
            column_widths={"tanggal": 140, "kode": 80, "nama": 160,
                           "jenis": 70, "jumlah": 60, "keterangan": 200},
            height=10
        )
        self._tree_log.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 15),
                             columnspan=10)

        # Tag jenis
        self._tree_log.tag_configure("masuk", foreground=COLORS["success"])
        self._tree_log.tag_configure("keluar", foreground=COLORS["danger"])

    def _load_products(self):
        """Muat daftar produk ke Combobox."""
        try:
            from models.product_model import ProductModel
            product_model = ProductModel()
            products = product_model.get_all()
            self._products_map = {}
            display_list = []
            for p in products:
                key = f"{p['kode_barang']} — {p['nama_barang']}"
                self._products_map[key] = {
                    "id": p["id"], "stok": p["stok"],
                    "nama": p["nama_barang"]
                }
                display_list.append(key)
            self._combo_produk["values"] = display_list
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat produk: {e}")

    def _on_product_select(self, event=None):
        """Tampilkan info stok produk terpilih."""
        key = self._combo_produk.get()
        if key in self._products_map:
            stok = self._products_map[key]["stok"]
            self._lbl_stok_info.config(text=f"Stok saat ini: {stok} unit")

    def _load_log(self, jenis_filter=None):
        """Muat riwayat mutasi stok ke Treeview."""
        self._tree_log.delete(*self._tree_log.get_children())
        try:
            from models.stock_model import StockModel
            stock_model = StockModel()
            logs = stock_model.get_log(jenis_filter)

            for log in logs:
                tag = log["jenis"]
                self._tree_log.insert("", "end", values=(
                    log["tanggal"],
                    log["kode_barang"] or "-",
                    log["nama_barang"] or "-",
                    log["jenis"].upper(),
                    log["jumlah"],
                    log["keterangan"] or "-"
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat log stok: {e}")

    def _process_stock(self, jenis):
        """Proses mutasi stok masuk atau keluar."""
        key = self._combo_produk.get()
        if not key or key not in self._products_map:
            messagebox.showwarning("Peringatan", "Pilih produk terlebih dahulu!")
            return

        try:
            jumlah = validate_positive_integer(self._entry_jumlah.get(), "Jumlah")
            if jumlah <= 0:
                raise ValueError("Jumlah harus minimal 1")
        except ValueError as e:
            messagebox.showwarning("Validasi", str(e))
            return

        produk = self._products_map[key]
        keterangan = self._entry_ket.get().strip()

        # Konfirmasi
        jenis_label = "MASUK (restock)" if jenis == "masuk" else "KELUAR (retur/rusak)"
        if not messagebox.askyesno(
            "Konfirmasi",
            f"Proses stok {jenis_label}?\n\n"
            f"Produk: {produk['nama']}\n"
            f"Jumlah: {jumlah}\n"
            f"Keterangan: {keterangan or '-'}"
        ):
            return

        try:
            from models.stock_model import StockModel
            stock_model = StockModel()
            stock_model.add_stock(produk["id"], jenis, jumlah, keterangan)

            messagebox.showinfo("Sukses",
                                f"Stok {jenis} berhasil diproses!\n"
                                f"{produk['nama']}: {jenis} {jumlah} unit")
            self._clear_form()
            self._load_products()  # Refresh stok
            self._load_log()      # Refresh log

        except ValueError as e:
            messagebox.showwarning("Validasi", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_filter_change(self, event=None):
        """Handler perubahan filter jenis mutasi."""
        selected = self._combo_filter.get()
        if selected == "Masuk":
            self._load_log("masuk")
        elif selected == "Keluar":
            self._load_log("keluar")
        else:
            self._load_log()

    def _clear_form(self):
        """Bersihkan form mutasi stok."""
        self._combo_produk.set("")
        self._combo_jenis.set("masuk")
        self._entry_jumlah.delete(0, tk.END)
        self._entry_ket.delete(0, tk.END)
        self._lbl_stok_info.config(text="Stok saat ini: -")

    def refresh_data(self):
        """Refresh data saat frame ditampilkan."""
        self._load_products()
        self._load_log()

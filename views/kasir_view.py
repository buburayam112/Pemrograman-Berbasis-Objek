"""
kasir_view.py — Halaman transaksi kasir (modul inti POS).

Layout 2 kolom:
- Kiri: Pilih produk + input qty → tambah ke keranjang
- Kanan: Keranjang belanja + total + pembayaran
"""

import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseFrame, COLORS, FONTS
from utils.validators import validate_positive_integer, validate_positive_number


class KasirFrame(BaseFrame):
    """
    Frame transaksi kasir.
    
    Fitur:
    - Pilih produk dari Combobox atau search
    - Input qty → tambah ke keranjang (Treeview)
    - Hitung subtotal & total otomatis
    - Input bayar → hitung kembalian
    - Proses transaksi atomik (insert + kurangi stok + log)
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="🛒  Kasir — Transaksi Penjualan")
        self._cart = []  # List of dict: {produk_id, kode, nama, qty, harga, subtotal, stok}
        self._products_data = []  # Cache data produk
        self._build_ui()

    def _build_ui(self):
        """Bangun seluruh komponen UI kasir."""
        content = self._create_content_frame(padding=10)
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=3)
        content.grid_rowconfigure(0, weight=1)

        # ═══ KOLOM KIRI: Pilih Produk ═══
        left_card = self._create_card(content, title="Pilih Produk",
                                       row=0, column=0, sticky="nsew", padx=(0, 5))
        left_card.grid_columnconfigure(1, weight=1)
        left_card.grid_rowconfigure(6, weight=1)

        # Search produk
        tk.Label(left_card, text="🔍 Cari Produk:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=2, column=0, sticky="w", padx=(15, 5), pady=3)

        self._entry_search = tk.Entry(left_card, font=FONTS["body"], width=20,
                                       relief="solid", bd=1)
        self._entry_search.grid(row=2, column=1, sticky="ew", padx=(5, 15), pady=3)
        self._entry_search.bind("<KeyRelease>", self._on_search_product)

        # Tabel daftar produk
        prod_columns = [
            ("kode", "Kode"),
            ("nama", "Nama"),
            ("harga", "Harga Jual"),
            ("stok", "Stok"),
        ]
        self._tree_products = self._create_treeview(
            left_card, prod_columns,
            column_widths={"kode": 70, "nama": 140, "harga": 90, "stok": 50},
            height=10
        )
        self._tree_products.grid(row=3, column=0, columnspan=2, sticky="nsew",
                                  padx=15, pady=5)

        # Input qty
        qty_frame = tk.Frame(left_card, bg=COLORS["bg_card"])
        qty_frame.grid(row=4, column=0, columnspan=2, sticky="ew",
                       padx=15, pady=5)
        qty_frame.grid_columnconfigure(1, weight=1)

        tk.Label(qty_frame, text="Jumlah (Qty):", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=0, column=0, padx=(0, 10))

        self._entry_qty = tk.Entry(qty_frame, font=FONTS["body"], width=8,
                                    relief="solid", bd=1, justify="center")
        self._entry_qty.grid(row=0, column=1, sticky="w")
        self._entry_qty.insert(0, "1")

        # Tombol tambah ke keranjang
        self._create_button(left_card, "➕  Tambah ke Keranjang",
                            self._add_to_cart, "success",
                            row=5, column=0, padx=15, pady=(5, 15), sticky="ew")

        # Info produk terpilih
        self._lbl_selected = tk.Label(
            left_card, text="Pilih produk dari tabel di atas",
            font=FONTS["small"], bg=COLORS["bg_card"],
            fg=COLORS["text_muted"], wraplength=280
        )
        self._lbl_selected.grid(row=6, column=0, columnspan=2, 
                                 sticky="sw", padx=15, pady=(0, 10))

        # Bind pilih produk
        self._tree_products.bind("<<TreeviewSelect>>", self._on_product_select)

        # ═══ KOLOM KANAN: Keranjang Belanja ═══
        right_card = self._create_card(content, title="🧺  Keranjang Belanja",
                                        row=0, column=1, sticky="nsew", padx=(5, 0))
        right_card.grid_columnconfigure(0, weight=1)
        right_card.grid_rowconfigure(2, weight=1)

        # Treeview keranjang
        cart_columns = [
            ("no", "No"),
            ("kode", "Kode"),
            ("nama", "Nama Barang"),
            ("harga", "Harga"),
            ("qty", "Qty"),
            ("subtotal", "Subtotal"),
        ]
        self._tree_cart = self._create_treeview(
            right_card, cart_columns,
            column_widths={"no": 35, "kode": 70, "nama": 150,
                           "harga": 90, "qty": 45, "subtotal": 100},
            height=10
        )
        self._tree_cart.grid(row=2, column=0, sticky="nsew", padx=15, pady=5,
                              columnspan=10)

        # Tombol hapus item
        cart_btn_frame = tk.Frame(right_card, bg=COLORS["bg_card"])
        cart_btn_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=5,
                             columnspan=10)

        self._create_button(cart_btn_frame, "🗑️  Hapus Item",
                            self._remove_from_cart, "danger",
                            row=0, column=0, padx=(0, 5))
        self._create_button(cart_btn_frame, "🔄  Batal/Reset",
                            self._reset_cart, "secondary",
                            row=0, column=1, padx=5)

        # ── Panel Total & Pembayaran ──
        pay_frame = tk.Frame(right_card, bg=COLORS["bg_card"],
                              relief="groove", bd=1)
        pay_frame.grid(row=4, column=0, sticky="ew", padx=15, pady=(5, 15),
                        columnspan=10)
        pay_frame.grid_columnconfigure(1, weight=1)

        # Total belanja
        tk.Label(pay_frame, text="TOTAL BELANJA:",
                 font=("Segoe UI", 14, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        self._lbl_total = tk.Label(
            pay_frame, text="Rp 0",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["accent"]
        )
        self._lbl_total.grid(row=0, column=1, sticky="e", padx=15, pady=(15, 5))

        # Input bayar
        tk.Label(pay_frame, text="Bayar (Rp):",
                 font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=1, column=0, sticky="w", padx=15, pady=3)

        self._entry_bayar = tk.Entry(
            pay_frame, font=("Segoe UI", 14),
            width=15, relief="solid", bd=1, justify="right"
        )
        self._entry_bayar.grid(row=1, column=1, sticky="e", padx=15, pady=3)
        self._entry_bayar.bind("<KeyRelease>", self._calc_kembalian)

        # Kembalian
        tk.Label(pay_frame, text="Kembalian:",
                 font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=2, column=0, sticky="w", padx=15, pady=3)

        self._lbl_kembalian = tk.Label(
            pay_frame, text="Rp 0",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["success"]
        )
        self._lbl_kembalian.grid(row=2, column=1, sticky="e", padx=15, pady=3)

        # Tombol proses
        self._create_button(pay_frame, "✅  PROSES TRANSAKSI",
                            self._process_transaction, "success",
                            row=3, column=0, padx=15, pady=(10, 15),
                            sticky="ew")
        # Span 2 columns
        pay_frame.grid_columnconfigure(0, weight=1)

    def _load_products(self, data=None):
        """Muat daftar produk ke Treeview kiri."""
        self._tree_products.delete(*self._tree_products.get_children())
        try:
            if data is None:
                from models.product_model import ProductModel
                product_model = ProductModel()
                self._products_data = product_model.get_all()
                data = self._products_data

            for p in data:
                tags = ("low_stock",) if p["stok"] < p["stok_minimum"] else ()
                self._tree_products.insert("", "end", iid=str(p["id"]), values=(
                    p["kode_barang"],
                    p["nama_barang"],
                    self._format_currency(p["harga_jual"]),
                    p["stok"]
                ), tags=tags)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat produk: {e}")

    def _on_search_product(self, event=None):
        """Cari produk real-time."""
        keyword = self._entry_search.get().strip()
        if keyword:
            try:
                from models.product_model import ProductModel
                product_model = ProductModel()
                results = product_model.search(keyword)
                self._load_products(data=results)
            except Exception:
                pass
        else:
            self._load_products()

    def _on_product_select(self, event):
        """Tampilkan info produk yang dipilih."""
        selection = self._tree_products.selection()
        if selection:
            values = self._tree_products.item(selection[0])["values"]
            self._lbl_selected.config(
                text=f"✓ Terpilih: {values[0]} — {values[1]} | Harga: {values[2]} | Stok: {values[3]}"
            )

    def _add_to_cart(self):
        """Tambah produk ke keranjang belanja."""
        selection = self._tree_products.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih produk terlebih dahulu!")
            return

        try:
            qty = validate_positive_integer(self._entry_qty.get(), "Jumlah")
            if qty <= 0:
                raise ValueError("Jumlah harus minimal 1")
        except ValueError as e:
            messagebox.showwarning("Validasi", str(e))
            return

        produk_id = int(selection[0])

        # Ambil data produk terbaru dari DB
        try:
            from models.product_model import ProductModel
            product_model = ProductModel()
            p = product_model.get_by_id(produk_id)

            if not p:
                messagebox.showerror("Error", "Produk tidak ditemukan!")
                return

            # Hitung qty total (jika produk sudah ada di keranjang)
            existing_qty = 0
            for item in self._cart:
                if item["produk_id"] == produk_id:
                    existing_qty = item["qty"]
                    break

            total_qty = existing_qty + qty
            if total_qty > p["stok"]:
                messagebox.showwarning(
                    "Stok Tidak Cukup",
                    f"Stok {p['nama_barang']} hanya tersisa {p['stok']}.\n"
                    f"Di keranjang sudah ada {existing_qty} unit."
                )
                return

            # Cek apakah produk sudah di keranjang
            found = False
            for item in self._cart:
                if item["produk_id"] == produk_id:
                    item["qty"] = total_qty
                    item["subtotal"] = total_qty * item["harga"]
                    found = True
                    break

            if not found:
                self._cart.append({
                    "produk_id": produk_id,
                    "kode": p["kode_barang"],
                    "nama": p["nama_barang"],
                    "harga": p["harga_jual"],
                    "qty": qty,
                    "subtotal": qty * p["harga_jual"],
                    "stok_tersedia": p["stok"],
                    "harga_satuan": p["harga_jual"]
                })

            self._refresh_cart()
            self._entry_qty.delete(0, tk.END)
            self._entry_qty.insert(0, "1")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _remove_from_cart(self):
        """Hapus item terpilih dari keranjang."""
        selection = self._tree_cart.selection()
        if not selection:
            messagebox.showwarning("Peringatan", "Pilih item yang ingin dihapus!")
            return

        idx = int(selection[0])
        if 0 <= idx < len(self._cart):
            removed = self._cart.pop(idx)
            messagebox.showinfo("Info", f"{removed['nama']} dihapus dari keranjang.")
            self._refresh_cart()

    def _reset_cart(self):
        """Reset/kosongkan seluruh keranjang."""
        if self._cart:
            if messagebox.askyesno("Konfirmasi", "Batalkan semua item di keranjang?"):
                self._cart.clear()
                self._refresh_cart()
                self._entry_bayar.delete(0, tk.END)
                self._lbl_kembalian.config(text="Rp 0", fg=COLORS["success"])

    def _refresh_cart(self):
        """Refresh tampilan Treeview keranjang."""
        self._tree_cart.delete(*self._tree_cart.get_children())
        total = 0
        for i, item in enumerate(self._cart):
            self._tree_cart.insert("", "end", iid=str(i), values=(
                i + 1,
                item["kode"],
                item["nama"],
                self._format_currency(item["harga"]),
                item["qty"],
                self._format_currency(item["subtotal"])
            ))
            total += item["subtotal"]

        self._lbl_total.config(text=self._format_currency(total))
        self._calc_kembalian()

    def _calc_kembalian(self, event=None):
        """Hitung kembalian otomatis."""
        total = sum(item["subtotal"] for item in self._cart)
        try:
            bayar = float(self._entry_bayar.get() or 0)
            kembalian = bayar - total
            self._lbl_kembalian.config(
                text=self._format_currency(kembalian),
                fg=COLORS["success"] if kembalian >= 0 else COLORS["danger"]
            )
        except ValueError:
            self._lbl_kembalian.config(text="Rp 0", fg=COLORS["text_muted"])

    def _process_transaction(self):
        """Proses dan simpan transaksi."""
        if not self._cart:
            messagebox.showwarning("Peringatan", "Keranjang belanja masih kosong!")
            return

        total = sum(item["subtotal"] for item in self._cart)

        try:
            bayar = validate_positive_number(self._entry_bayar.get(), "Jumlah Bayar")
        except ValueError as e:
            messagebox.showwarning("Validasi", str(e))
            return

        if bayar < total:
            messagebox.showwarning(
                "Pembayaran Kurang",
                f"Total: {self._format_currency(total)}\n"
                f"Bayar: {self._format_currency(bayar)}\n"
                f"Kurang: {self._format_currency(total - bayar)}"
            )
            return

        # Konfirmasi
        kembalian = bayar - total
        msg = (
            f"Total Belanja: {self._format_currency(total)}\n"
            f"Bayar: {self._format_currency(bayar)}\n"
            f"Kembalian: {self._format_currency(kembalian)}\n\n"
            f"Proses transaksi?"
        )
        if not messagebox.askyesno("Konfirmasi Transaksi", msg):
            return

        try:
            from models.transaction_model import TransactionModel
            trx_model = TransactionModel()

            # Refresh stok terbaru sebelum proses
            from models.product_model import ProductModel
            product_model = ProductModel()
            for item in self._cart:
                p = product_model.get_by_id(item["produk_id"])
                item["stok_tersedia"] = p["stok"]

            kasir_id = self._controller.current_user.id
            result = trx_model.create_transaction(kasir_id, self._cart, bayar)

            # Struk ringkas
            struk = (
                f"═══════════════════════════\n"
                f"     STRUK TRANSAKSI\n"
                f"═══════════════════════════\n"
                f"No: {result['no_transaksi']}\n"
                f"Tanggal: {result['tanggal']}\n"
                f"Item: {result['jumlah_item']} jenis\n"
                f"───────────────────────────\n"
                f"Total: {self._format_currency(result['total'])}\n"
                f"Bayar: {self._format_currency(result['bayar'])}\n"
                f"Kembali: {self._format_currency(result['kembalian'])}\n"
                f"═══════════════════════════\n"
                f"    Terima kasih!\n"
            )
            messagebox.showinfo("Transaksi Berhasil", struk)

            # Reset
            self._cart.clear()
            self._refresh_cart()
            self._entry_bayar.delete(0, tk.END)
            self._lbl_kembalian.config(text="Rp 0", fg=COLORS["success"])
            self._load_products()  # Refresh stok di tabel

        except ValueError as e:
            messagebox.showwarning("Validasi", str(e))
        except Exception as e:
            messagebox.showerror("Error Transaksi", str(e))

    def refresh_data(self):
        """Refresh data saat frame ditampilkan."""
        self._load_products()

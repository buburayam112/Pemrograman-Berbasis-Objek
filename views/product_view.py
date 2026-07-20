"""
product_view.py — Halaman manajemen produk (CRUD penuh).

Menampilkan tabel produk dengan form tambah/edit di panel atas.
Tidak menggunakan popup window — semua di satu frame.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseFrame, COLORS, FONTS
from utils.validators import validate_not_empty, validate_positive_number, validate_positive_integer


class ProductFrame(BaseFrame):
    """
    Frame CRUD produk.
    
    Layout:
    - Panel atas: Form input produk (kode, nama, kategori, harga, stok)
    - Panel bawah: Treeview daftar produk + search bar
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="📦  Manajemen Produk")
        self._editing_id = None  # ID produk yang sedang di-edit
        self._build_ui()

    def _build_ui(self):
        """Bangun seluruh komponen UI."""
        content = self._create_content_frame()
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)

        # ── Panel Form ──
        form_card = self._create_card(content, title="Form Produk",
                                       row=0, column=0, sticky="ew")
        form_card.grid_columnconfigure(1, weight=1)
        form_card.grid_columnconfigure(3, weight=1)

        # Row 2: Kode Barang + Nama Barang
        _, self._entry_kode = self._create_label_entry(
            form_card, "Kode Barang:", 2, 0, 20)
        _, self._entry_nama = self._create_label_entry(
            form_card, "Nama Barang:", 2, 2, 30)

        # Row 3: Kategori + Harga Beli
        tk.Label(form_card, text="Kategori:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"],
                 anchor="w").grid(row=3, column=0, sticky="w", padx=(15, 5), pady=3)

        self._combo_kategori = ttk.Combobox(
            form_card, font=FONTS["body"], width=18, state="readonly"
        )
        self._combo_kategori.grid(row=3, column=1, sticky="ew", padx=(5, 15), pady=3)

        _, self._entry_harga_beli = self._create_label_entry(
            form_card, "Harga Beli:", 3, 2, 15)

        # Row 4: Harga Jual + Stok
        _, self._entry_harga_jual = self._create_label_entry(
            form_card, "Harga Jual:", 4, 0, 15)
        _, self._entry_stok = self._create_label_entry(
            form_card, "Stok:", 4, 2, 10)

        # Row 5: Stok Minimum
        _, self._entry_stok_min = self._create_label_entry(
            form_card, "Stok Minimum:", 5, 0, 10)

        # Row 6: Tombol Aksi
        btn_frame = tk.Frame(form_card, bg=COLORS["bg_card"])
        btn_frame.grid(row=6, column=0, columnspan=4, pady=(10, 15), padx=15,
                       sticky="w")

        self._btn_simpan = self._create_button(
            btn_frame, "💾  Simpan", self._on_save, "success",
            row=0, column=0, padx=(0, 5))
        self._btn_update = self._create_button(
            btn_frame, "✏️  Update", self._on_update, "primary",
            row=0, column=1, padx=5)
        self._btn_hapus = self._create_button(
            btn_frame, "🗑️  Hapus", self._on_delete, "danger",
            row=0, column=2, padx=5)
        self._btn_bersih = self._create_button(
            btn_frame, "🔄  Bersihkan", self._clear_form, "secondary",
            row=0, column=3, padx=5)

        # ── Panel Tabel ──
        table_card = self._create_card(content, title="Daftar Produk",
                                        row=1, column=0, pady=(10, 5))
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(3, weight=1)

        # Search bar
        search_frame = tk.Frame(table_card, bg=COLORS["bg_card"])
        search_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10),
                          columnspan=10)
        search_frame.grid_columnconfigure(1, weight=1)

        tk.Label(search_frame, text="🔍 Cari:", font=FONTS["body_bold"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]
                 ).grid(row=0, column=0, padx=(0, 5))

        self._entry_search = tk.Entry(search_frame, font=FONTS["body"],
                                       width=30, relief="solid", bd=1)
        self._entry_search.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self._entry_search.bind("<KeyRelease>", self._on_search)

        # Treeview
        columns = [
            ("kode", "Kode"),
            ("nama", "Nama Barang"),
            ("kategori", "Kategori"),
            ("harga_beli", "Harga Beli"),
            ("harga_jual", "Harga Jual"),
            ("stok", "Stok"),
            ("stok_min", "Min"),
        ]
        self._tree = self._create_treeview(
            table_card, columns,
            column_widths={"kode": 90, "nama": 180, "kategori": 100,
                           "harga_beli": 110, "harga_jual": 110,
                           "stok": 60, "stok_min": 60},
            height=12
        )
        self._tree.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 15),
                         columnspan=10)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # Label info jumlah
        self._lbl_info = tk.Label(table_card, text="Total: 0 produk",
                                   font=FONTS["small"], bg=COLORS["bg_card"],
                                   fg=COLORS["text_muted"])
        self._lbl_info.grid(row=4, column=0, sticky="w", padx=15, pady=(0, 10),
                             columnspan=10)

    def _load_categories(self):
        """Muat daftar kategori ke Combobox."""
        try:
            from models.product_model import CategoryModel
            cat_model = CategoryModel()
            categories = cat_model.get_all()
            self._categories = {row["nama_kategori"]: row["id"] for row in categories}
            self._combo_kategori["values"] = list(self._categories.keys())
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat kategori: {e}")

    def _load_products(self, data=None):
        """Muat data produk ke Treeview."""
        self._tree.delete(*self._tree.get_children())
        try:
            from models.product_model import ProductModel
            product_model = ProductModel()
            products = data if data is not None else product_model.get_all()

            for i, p in enumerate(products):
                tags = []
                if p["stok"] < p["stok_minimum"]:
                    tags.append("low_stock")
                elif i % 2 == 1:
                    tags.append("alt_row")

                self._tree.insert("", "end", iid=str(p["id"]), values=(
                    p["kode_barang"],
                    p["nama_barang"],
                    p["nama_kategori"] or "-",
                    self._format_currency(p["harga_beli"]),
                    self._format_currency(p["harga_jual"]),
                    p["stok"],
                    p["stok_minimum"]
                ), tags=tags)

            self._lbl_info.config(text=f"Total: {len(products)} produk")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat produk: {e}")

    def _on_select(self, event):
        """Handler ketika baris di Treeview dipilih — isi form untuk edit."""
        selection = self._tree.selection()
        if not selection:
            return

        item_id = selection[0]
        self._editing_id = int(item_id)

        try:
            from models.product_model import ProductModel
            product_model = ProductModel()
            p = product_model.get_by_id(self._editing_id)

            if p:
                self._clear_form(keep_id=True)
                self._entry_kode.insert(0, p["kode_barang"])
                self._entry_nama.insert(0, p["nama_barang"])

                # Set kategori di combobox
                if p["nama_kategori"]:
                    self._combo_kategori.set(p["nama_kategori"])

                self._entry_harga_beli.insert(0, str(int(p["harga_beli"])))
                self._entry_harga_jual.insert(0, str(int(p["harga_jual"])))
                self._entry_stok.insert(0, str(p["stok"]))
                self._entry_stok_min.insert(0, str(p["stok_minimum"]))
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data produk: {e}")

    def _on_save(self):
        """Handler tombol Simpan — tambah produk baru."""
        try:
            kode = validate_not_empty(self._entry_kode.get(), "Kode Barang")
            nama = validate_not_empty(self._entry_nama.get(), "Nama Barang")
            harga_beli = validate_positive_number(self._entry_harga_beli.get(), "Harga Beli")
            harga_jual = validate_positive_number(self._entry_harga_jual.get(), "Harga Jual")
            stok = validate_positive_integer(self._entry_stok.get(), "Stok")
            stok_min = validate_positive_integer(
                self._entry_stok_min.get() or "5", "Stok Minimum"
            )

            # Ambil kategori_id
            kat_nama = self._combo_kategori.get()
            kategori_id = self._categories.get(kat_nama)
            if not kategori_id:
                raise ValueError("Kategori harus dipilih")

            from models.product_model import ProductModel
            product_model = ProductModel()

            # Cek kode unik
            if not product_model.check_kode_unique(kode):
                raise ValueError(f"Kode barang '{kode}' sudah digunakan")

            product_model.add(kode, nama, kategori_id, harga_beli,
                              harga_jual, stok, stok_min)
            messagebox.showinfo("Sukses", f"Produk '{nama}' berhasil ditambahkan!")
            self._clear_form()
            self._load_products()

        except ValueError as e:
            messagebox.showwarning("Validasi", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_update(self):
        """Handler tombol Update — perbarui produk yang sedang di-edit."""
        if not self._editing_id:
            messagebox.showwarning("Peringatan", "Pilih produk yang ingin di-update!")
            return

        try:
            kode = validate_not_empty(self._entry_kode.get(), "Kode Barang")
            nama = validate_not_empty(self._entry_nama.get(), "Nama Barang")
            harga_beli = validate_positive_number(self._entry_harga_beli.get(), "Harga Beli")
            harga_jual = validate_positive_number(self._entry_harga_jual.get(), "Harga Jual")
            stok = validate_positive_integer(self._entry_stok.get(), "Stok")
            stok_min = validate_positive_integer(
                self._entry_stok_min.get() or "5", "Stok Minimum"
            )

            kat_nama = self._combo_kategori.get()
            kategori_id = self._categories.get(kat_nama)
            if not kategori_id:
                raise ValueError("Kategori harus dipilih")

            from models.product_model import ProductModel
            product_model = ProductModel()

            # Cek kode unik (exclude current id)
            if not product_model.check_kode_unique(kode, exclude_id=self._editing_id):
                raise ValueError(f"Kode barang '{kode}' sudah digunakan produk lain")

            product_model.update(self._editing_id, kode, nama, kategori_id,
                                 harga_beli, harga_jual, stok, stok_min)
            messagebox.showinfo("Sukses", f"Produk '{nama}' berhasil diperbarui!")
            self._clear_form()
            self._load_products()

        except ValueError as e:
            messagebox.showwarning("Validasi", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_delete(self):
        """Handler tombol Hapus — hapus produk dengan konfirmasi."""
        if not self._editing_id:
            messagebox.showwarning("Peringatan", "Pilih produk yang ingin dihapus!")
            return

        nama = self._entry_nama.get()
        if messagebox.askyesno("Konfirmasi Hapus",
                                f"Yakin ingin menghapus produk '{nama}'?"):
            try:
                from models.product_model import ProductModel
                product_model = ProductModel()
                product_model.delete(self._editing_id)
                messagebox.showinfo("Sukses", f"Produk '{nama}' berhasil dihapus!")
                self._clear_form()
                self._load_products()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _on_search(self, event=None):
        """Handler pencarian produk real-time."""
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

    def _clear_form(self, keep_id=False):
        """Bersihkan semua field form."""
        if not keep_id:
            self._editing_id = None

        for entry in [self._entry_kode, self._entry_nama,
                      self._entry_harga_beli, self._entry_harga_jual,
                      self._entry_stok, self._entry_stok_min]:
            entry.delete(0, tk.END)

        self._combo_kategori.set("")

    def refresh_data(self):
        """Refresh data saat frame ditampilkan."""
        self._load_categories()
        self._load_products()

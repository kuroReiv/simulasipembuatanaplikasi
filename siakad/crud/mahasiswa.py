# Mengimpor datetime untuk validasi format tanggal lahir
from datetime import datetime
# Mengimpor modul tkinter dasar untuk pembuatan komponen GUI
import tkinter as tk
# Mengimpor ttk (Combobox & Treeview) dan messagebox untuk dialog pop-up
from tkinter import ttk, messagebox
# Mengimpor mysql.connector untuk koneksi dan operasi database MySQL
import mysql.connector

# --- KONEKSI DATABASE ---
def connect_db():
    return mysql.connector.connect(
        host="localhost",      # Alamat host server MySQL
        user="root",           # Username MySQL
        password="",           # Password (kosongkan jika tidak ada)
        database="siakad"      # Nama database
    )

# --- DEFINISI KOLOM ---
# Setiap item: (nama kolom di database, label di form/tabel, lebar kolom tabel)
# Urutannya sama persis dengan struktur tabel mahasiswa
KOLOM = [
    ("nim",           "NIM",            90),
    ("nama_lengkap",  "Nama Lengkap",   160),
    ("jenis_kelamin", "Jenis Kelamin",  100),
    ("tanggal_lahir", "Tanggal Lahir",  100),
    ("tempat_lahir",  "Tempat Lahir",   100),
    ("alamat",        "Alamat",         200),
    ("no_telepon",    "No Telepon",     110),
    ("email",         "Email",          160),
    ("jurusan",       "Jurusan",        150),
    ("angkatan",      "Angkatan",       70),
    ("status",        "Status",         70),
]
NAMA_KOLOM = [k[0] for k in KOLOM]

# Pilihan untuk field yang berbentuk dropdown
PILIHAN_JK = ["Laki-laki", "Perempuan"]
PILIHAN_STATUS = ["Aktif", "Cuti", "Lulus", "Non-Aktif"]

# Dictionary penampung widget input: {nama_kolom: widget}
fields = {}

# --- FUNGSI BANTU ---
# Mengatur isi sebuah widget input (Entry atau Combobox)
def set_field(widget, value):
    if isinstance(widget, ttk.Combobox):
        widget.set(value)
    else:
        widget.delete(0, tk.END)
        widget.insert(0, value)

# Mengosongkan seluruh input form
def clear_fields(keep_selection=False):
    for widget in fields.values():
        set_field(widget, "")
    # Jika dipanggil dari tombol Clear, hilangkan juga pilihan baris di tabel
    if not keep_selection and tree.selection():
        tree.selection_remove(tree.selection())

# Mengambil nilai form, memvalidasi, lalu mengembalikan dict (atau None jika tidak valid)
def ambil_dan_validasi():
    data = {col: fields[col].get().strip() for col in NAMA_KOLOM}

    # NIM dan Nama wajib diisi
    if not data["nim"] or not data["nama_lengkap"]:
        messagebox.showwarning("Warning", "NIM dan Nama Lengkap wajib diisi!")
        return None

    # Tanggal lahir harus berformat YYYY-MM-DD (format DATE MySQL)
    if data["tanggal_lahir"]:
        try:
            datetime.strptime(data["tanggal_lahir"], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Warning", "Tanggal Lahir harus berformat YYYY-MM-DD (contoh: 2003-05-12)!")
            return None
    else:
        data["tanggal_lahir"] = None

    # Angkatan harus berupa angka
    if data["angkatan"]:
        if not data["angkatan"].isdigit():
            messagebox.showwarning("Warning", "Angkatan harus berupa angka (contoh: 2023)!")
            return None
    else:
        data["angkatan"] = None

    return data

# --- FUNGSI CRUD ---
# Menampilkan baris hasil query ke Treeview (nilai None ditampilkan kosong)
def isi_tabel(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", "end", values=["" if v is None else v for v in row])

# Memuat seluruh data mahasiswa
def load_data():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT {', '.join(NAMA_KOLOM)} FROM mahasiswa ORDER BY nim")
        isi_tabel(cursor.fetchall())
        db.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")

# Menambahkan data mahasiswa baru
def tambah_data():
    data = ambil_dan_validasi()
    if data is None:
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        placeholders = ", ".join(["%s"] * len(NAMA_KOLOM))
        sql = f"INSERT INTO mahasiswa ({', '.join(NAMA_KOLOM)}) VALUES ({placeholders})"
        cursor.execute(sql, [data[c] for c in NAMA_KOLOM])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
        clear_fields()
        load_data()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menambah data: {e}")

# Memperbarui data mahasiswa yang dipilih (NIM dipakai sebagai acuan WHERE)
def edit_data():
    if not tree.selection():
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin diubah!")
        return
    data = ambil_dan_validasi()
    if data is None:
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        kolom_update = [c for c in NAMA_KOLOM if c != "nim"]
        set_clause = ", ".join(f"{c}=%s" for c in kolom_update)
        sql = f"UPDATE mahasiswa SET {set_clause} WHERE nim=%s"
        cursor.execute(sql, [data[c] for c in kolom_update] + [data["nim"]])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
        clear_fields()
        load_data()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

# Menghapus data mahasiswa
def hapus_data():
    if not tree.selection():
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin dihapus!")
        return
    nim = fields["nim"].get()
    if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus mahasiswa NIM {nim}?"):
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM mahasiswa WHERE nim = %s", (nim,))
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
            clear_fields()
            load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus data: {e}")

# Mencari data berdasarkan NIM, nama, atau jurusan
def cari_data():
    keyword = entry_cari.get().strip()
    if not keyword:
        load_data()
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        sql = f"""SELECT {', '.join(NAMA_KOLOM)} FROM mahasiswa
                  WHERE nim LIKE %s OR nama_lengkap LIKE %s OR jurusan LIKE %s
                  ORDER BY nim"""
        like = f"%{keyword}%"
        cursor.execute(sql, (like, like, like))
        isi_tabel(cursor.fetchall())
        db.close()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal mencari data: {e}")

# Saat baris tabel dipilih, isi form dengan data baris tersebut
def select_item(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0], "values")
        clear_fields(keep_selection=True)
        for col, val in zip(NAMA_KOLOM, values):
            set_field(fields[col], val)

# --- GUI MAIN WINDOW ---
root = tk.Tk()
root.title("Aplikasi Data Mahasiswa - SIAKAD")
root.geometry("1100x620")

# Frame form input
frame_form = tk.LabelFrame(root, text=" Form Data Mahasiswa ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

# Membuat label + input untuk setiap kolom secara otomatis (grid 2 kolom)
for i, (col, label, _) in enumerate(KOLOM):
    baris, kolom = i // 2, (i % 2) * 2
    tk.Label(frame_form, text=label).grid(row=baris, column=kolom, sticky="w", padx=5, pady=3)
    if col == "jenis_kelamin":
        widget = ttk.Combobox(frame_form, values=PILIHAN_JK, state="readonly")
    elif col == "status":
        widget = ttk.Combobox(frame_form, values=PILIHAN_STATUS, state="readonly")
    else:
        widget = tk.Entry(frame_form)
    widget.grid(row=baris, column=kolom + 1, padx=5, pady=3, sticky="ew")
    fields[col] = widget

# Kolom input melebar mengikuti lebar frame
frame_form.grid_columnconfigure(1, weight=1)
frame_form.grid_columnconfigure(3, weight=1)

# Frame tombol aksi
frame_btn = tk.Frame(root)
frame_btn.pack(fill="x", padx=15, pady=5)

tk.Button(frame_btn, text="Tambah", bg="#4CAF50", fg="white", command=tambah_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Edit", bg="#2196F3", fg="white", command=edit_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Hapus", bg="#f44336", fg="white", command=hapus_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Clear", bg="#9E9E9E", fg="white", command=clear_fields, width=12).pack(side="left", padx=5)

# Kolom pencarian di sisi kanan
tk.Button(frame_btn, text="Cari", bg="#FF9800", fg="white", command=cari_data, width=8).pack(side="right", padx=5)
entry_cari = tk.Entry(frame_btn, width=25)
entry_cari.pack(side="right", padx=5)
entry_cari.bind("<Return>", lambda e: cari_data())
tk.Label(frame_btn, text="Cari NIM/Nama/Jurusan:").pack(side="right")

# Frame tabel
frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=15, pady=10)

tree = ttk.Treeview(frame_table, columns=NAMA_KOLOM, show="headings")
for col, label, lebar in KOLOM:
    tree.heading(col, text=label)
    tree.column(col, width=lebar, minwidth=60)

tree.bind("<<TreeviewSelect>>", select_item)

# Scrollbar vertikal dan horizontal (tabel punya 11 kolom sehingga cukup lebar)
scroll_y = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_table, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")
frame_table.grid_rowconfigure(0, weight=1)
frame_table.grid_columnconfigure(0, weight=1)

# Tampilkan data awal
load_data()

# Jalankan loop utama GUI
root.mainloop()
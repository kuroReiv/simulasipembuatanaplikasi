# Mengimpor datetime dan date untuk validasi serta tampilan tanggal
from datetime import datetime, date
# Mengimpor Decimal untuk menampilkan nilai uang dari database dengan format rapi
from decimal import Decimal
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

# Nama tabel pembayaran di database (ubah di sini jika nama tabelmu berbeda)
TABEL = "pembayaran_ukt"

# --- DEFINISI KOLOM ---
# Setiap item: (nama kolom di database, label di form/tabel, lebar kolom tabel)
KOLOM = [
    ("id_pembayaran",     "ID Pembayaran",     100),
    ("nim",               "NIM",               90),
    ("semester",          "Semester",          70),
    ("tahun_ajaran",      "Tahun Ajaran",      100),
    ("jumlah_bayar",      "Jumlah Bayar",      110),
    ("tanggal_bayar",     "Tanggal Bayar",     100),
    ("metode_pembayaran", "Metode Pembayaran", 130),
    ("status",            "Status",            100),
]
NAMA_KOLOM = [k[0] for k in KOLOM]
# Kolom yang diisi pengguna (id_pembayaran dibuat otomatis oleh database / AUTO_INCREMENT)
KOLOM_INPUT = [c for c in NAMA_KOLOM if c != "id_pembayaran"]

# Pilihan metode kosong untuk pembayaran yang belum dilakukan
PILIHAN_METODE = ["", "Transfer Bank", "Virtual Account", "Tunai"]
PILIHAN_STATUS = ["Lunas", "Belum Lunas"]

# Dictionary penampung widget input: {nama_kolom: widget}
fields = {}

# --- FUNGSI BANTU ---
# Mengubah nilai dari database menjadi teks tampilan
# (None -> kosong, Decimal -> 2 desimal, date -> YYYY-MM-DD)
def tampil(v):
    if v is None:
        return ""
    if isinstance(v, (Decimal, float)):
        return f"{v:.2f}"
    if isinstance(v, date):
        return v.isoformat()
    return v

# Mengatur isi sebuah widget input (Entry atau Combobox), termasuk Entry yang readonly
def set_field(widget, value):
    if isinstance(widget, ttk.Combobox):
        widget.set(value)
    else:
        status_awal = str(widget.cget("state"))
        widget.config(state="normal")
        widget.delete(0, tk.END)
        widget.insert(0, value)
        widget.config(state=status_awal)

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

    # NIM, Semester, Tahun Ajaran, Jumlah Bayar, dan Status wajib diisi
    for col, label in [("nim", "NIM"), ("semester", "Semester"), ("tahun_ajaran", "Tahun Ajaran"),
                       ("jumlah_bayar", "Jumlah Bayar"), ("status", "Status")]:
        if not data[col]:
            messagebox.showwarning("Warning", f"{label} wajib diisi!")
            return None

    # Semester harus angka 1-14
    if not data["semester"].isdigit() or not (1 <= int(data["semester"]) <= 14):
        messagebox.showwarning("Warning", "Semester harus berupa angka 1 - 14!")
        return None

    # Tahun ajaran berformat YYYY/YYYY dan tahun kedua = tahun pertama + 1
    bagian = data["tahun_ajaran"].split("/")
    if (len(bagian) != 2 or not all(b.isdigit() and len(b) == 4 for b in bagian)
            or int(bagian[1]) != int(bagian[0]) + 1):
        messagebox.showwarning("Warning", "Tahun Ajaran harus berformat YYYY/YYYY (contoh: 2023/2024)!")
        return None

    # Jumlah bayar harus angka tidak negatif
    try:
        jumlah = float(data["jumlah_bayar"])
    except ValueError:
        messagebox.showwarning("Warning", "Jumlah Bayar harus berupa angka (contoh: 3500000)!")
        return None
    if jumlah < 0:
        messagebox.showwarning("Warning", "Jumlah Bayar tidak boleh negatif!")
        return None
    data["jumlah_bayar"] = f"{jumlah:.2f}"

    # Tanggal bayar boleh kosong (belum bayar), jika diisi harus format YYYY-MM-DD
    if data["tanggal_bayar"]:
        try:
            datetime.strptime(data["tanggal_bayar"], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Warning", "Tanggal Bayar harus berformat YYYY-MM-DD (contoh: 2023-08-15)!")
            return None
    else:
        data["tanggal_bayar"] = None

    # Metode pembayaran boleh kosong -> disimpan sebagai NULL
    if not data["metode_pembayaran"]:
        data["metode_pembayaran"] = None

    # Pembayaran Lunas harus punya tanggal bayar dan metode pembayaran
    if data["status"] == "Lunas" and (data["tanggal_bayar"] is None or data["metode_pembayaran"] is None):
        messagebox.showwarning("Warning", "Status Lunas harus diisi Tanggal Bayar dan Metode Pembayaran!")
        return None

    return data

# Memeriksa apakah mahasiswa sudah punya pembayaran yang sama (NIM, semester, tahun ajaran)
def cek_duplikat(cursor, data, id_pembayaran):
    sql = f"""SELECT id_pembayaran FROM {TABEL}
              WHERE nim=%s AND semester=%s AND tahun_ajaran=%s
                AND id_pembayaran <> %s"""
    cursor.execute(sql, (data["nim"], data["semester"], data["tahun_ajaran"], id_pembayaran))
    return cursor.fetchone()

# --- FUNGSI CRUD ---
# Menampilkan baris hasil query ke Treeview
def isi_tabel(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", "end", values=[tampil(v) for v in row])

# Memuat seluruh data pembayaran
def load_data():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT {', '.join(NAMA_KOLOM)} FROM {TABEL} ORDER BY id_pembayaran")
        isi_tabel(cursor.fetchall())
        db.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")

# Menambahkan pembayaran baru (id_pembayaran otomatis)
def tambah_data():
    data = ambil_dan_validasi()
    if data is None:
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        duplikat = cek_duplikat(cursor, data, 0)
        if duplikat:
            db.close()
            messagebox.showwarning("Data Ganda",
                f"Pembayaran yang sama sudah ada (ID Pembayaran {duplikat[0]}).")
            return
        placeholders = ", ".join(["%s"] * len(KOLOM_INPUT))
        sql = f"INSERT INTO {TABEL} ({', '.join(KOLOM_INPUT)}) VALUES ({placeholders})"
        cursor.execute(sql, [data[c] for c in KOLOM_INPUT])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
        clear_fields()
        load_data()
    except Exception as e:
        # Termasuk error foreign key jika NIM belum terdaftar
        messagebox.showerror("Error", f"Gagal menambah data: {e}")

# Memperbarui pembayaran yang dipilih (id_pembayaran dipakai sebagai acuan WHERE)
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
        duplikat = cek_duplikat(cursor, data, data["id_pembayaran"])
        if duplikat:
            db.close()
            messagebox.showwarning("Data Ganda",
                f"Pembayaran yang sama sudah ada (ID Pembayaran {duplikat[0]}).")
            return
        set_clause = ", ".join(f"{c}=%s" for c in KOLOM_INPUT)
        sql = f"UPDATE {TABEL} SET {set_clause} WHERE id_pembayaran=%s"
        cursor.execute(sql, [data[c] for c in KOLOM_INPUT] + [data["id_pembayaran"]])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
        clear_fields()
        load_data()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

# Menghapus pembayaran
def hapus_data():
    if not tree.selection():
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin dihapus!")
        return
    id_pembayaran = fields["id_pembayaran"].get()
    nim = fields["nim"].get()
    if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus pembayaran {nim} (ID {id_pembayaran})?"):
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute(f"DELETE FROM {TABEL} WHERE id_pembayaran = %s", (id_pembayaran,))
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
            clear_fields()
            load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus data: {e}")

# Mencari pembayaran berdasarkan NIM, tahun ajaran, atau status
def cari_data():
    keyword = entry_cari.get().strip()
    if not keyword:
        load_data()
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        sql = f"""SELECT {', '.join(NAMA_KOLOM)} FROM {TABEL}
                  WHERE nim LIKE %s OR tahun_ajaran LIKE %s OR status LIKE %s
                  ORDER BY id_pembayaran"""
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
root.title("Aplikasi Pembayaran - SIAKAD")
root.geometry("900x540")

# Frame form input
frame_form = tk.LabelFrame(root, text=" Form Pembayaran ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

# Membuat label + input untuk setiap kolom secara otomatis (grid 2 kolom)
for i, (col, label, _) in enumerate(KOLOM):
    baris, kolom = i // 2, (i % 2) * 2
    tk.Label(frame_form, text=label).grid(row=baris, column=kolom, sticky="w", padx=5, pady=3)
    if col == "metode_pembayaran":
        widget = ttk.Combobox(frame_form, values=PILIHAN_METODE, state="readonly")
    elif col == "status":
        widget = ttk.Combobox(frame_form, values=PILIHAN_STATUS, state="readonly")
    elif col == "id_pembayaran":
        # ID dibuat otomatis oleh database, jadi hanya untuk ditampilkan
        widget = tk.Entry(frame_form, state="readonly")
    else:
        widget = tk.Entry(frame_form)
    widget.grid(row=baris, column=kolom + 1, padx=5, pady=3, sticky="ew")
    fields[col] = widget

# Petunjuk pengisian
tk.Label(frame_form,
         text="Tahun Ajaran: YYYY/YYYY. Tanggal: YYYY-MM-DD. Tanggal & metode boleh kosong jika Belum Lunas.",
         fg="gray").grid(row=4, column=0, columnspan=4, sticky="w", padx=5)

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
entry_cari = tk.Entry(frame_btn, width=22)
entry_cari.pack(side="right", padx=5)
entry_cari.bind("<Return>", lambda e: cari_data())
tk.Label(frame_btn, text="Cari NIM/Tahun/Status:").pack(side="right")

# Frame tabel
frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=15, pady=10)

tree = ttk.Treeview(frame_table, columns=NAMA_KOLOM, show="headings")
for col, label, lebar in KOLOM:
    tree.heading(col, text=label)
    tree.column(col, width=lebar, minwidth=50)

tree.bind("<<TreeviewSelect>>", select_item)

scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Tampilkan data awal
load_data()

# Jalankan loop utama GUI
root.mainloop()
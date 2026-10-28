# Mengimpor datetime dan timedelta untuk validasi serta konversi jam
from datetime import datetime, timedelta
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
KOLOM = [
    ("id_jadwal",   "ID Jadwal",   70),
    ("kode_mk",     "Kode MK",     100),
    ("hari",        "Hari",        90),
    ("jam_mulai",   "Jam Mulai",   100),
    ("jam_selesai", "Jam Selesai", 100),
    ("ruangan",     "Ruangan",     180),
]
NAMA_KOLOM = [k[0] for k in KOLOM]
# Kolom yang diisi pengguna (id_jadwal dibuat otomatis oleh database / AUTO_INCREMENT)
KOLOM_INPUT = [c for c in NAMA_KOLOM if c != "id_jadwal"]

PILIHAN_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# Dictionary penampung widget input: {nama_kolom: widget}
fields = {}

# --- FUNGSI BANTU ---
# Mengubah nilai dari database menjadi teks tampilan.
# Kolom TIME dari MySQL dibaca sebagai timedelta (mis. 8:00:00), diubah ke format HH:MM:SS.
def tampil(v):
    if v is None:
        return ""
    if isinstance(v, timedelta):
        total = int(v.total_seconds())
        return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"
    return v

# Mengubah teks jam (HH:MM atau HH:MM:SS) menjadi objek time; None jika format salah
def parse_jam(teks):
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(teks, fmt).time()
        except ValueError:
            continue
    return None

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

    # Semua field wajib diisi
    for col in KOLOM_INPUT:
        if not data[col]:
            label = next(k[1] for k in KOLOM if k[0] == col)
            messagebox.showwarning("Warning", f"{label} wajib diisi!")
            return None

    # Validasi format jam
    mulai = parse_jam(data["jam_mulai"])
    selesai = parse_jam(data["jam_selesai"])
    if mulai is None or selesai is None:
        messagebox.showwarning("Warning", "Format jam harus HH:MM atau HH:MM:SS (contoh: 08:00)!")
        return None

    # Jam selesai harus lebih besar dari jam mulai
    if selesai <= mulai:
        messagebox.showwarning("Warning", "Jam selesai harus lebih besar dari jam mulai!")
        return None

    # Simpan dalam format HH:MM:SS yang seragam
    data["jam_mulai"] = mulai.strftime("%H:%M:%S")
    data["jam_selesai"] = selesai.strftime("%H:%M:%S")
    return data

# Memeriksa apakah ruangan sudah terpakai pada hari dan rentang jam yang beririsan
def cek_bentrok(cursor, data, id_jadwal):
    sql = """SELECT id_jadwal, kode_mk FROM jadwal_kuliah
             WHERE hari=%s AND ruangan=%s
               AND jam_mulai < %s AND jam_selesai > %s
               AND id_jadwal <> %s"""
    cursor.execute(sql, (data["hari"], data["ruangan"],
                         data["jam_selesai"], data["jam_mulai"], id_jadwal))
    return cursor.fetchone()

# --- FUNGSI CRUD ---
# Menampilkan baris hasil query ke Treeview
def isi_tabel(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", "end", values=[tampil(v) for v in row])

# Memuat seluruh data jadwal
def load_data():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT {', '.join(NAMA_KOLOM)} FROM jadwal_kuliah ORDER BY id_jadwal")
        isi_tabel(cursor.fetchall())
        db.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")

# Menambahkan jadwal baru (id_jadwal otomatis)
def tambah_data():
    data = ambil_dan_validasi()
    if data is None:
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        # Cek bentrok ruangan (id 0 karena data baru belum punya ID)
        bentrok = cek_bentrok(cursor, data, 0)
        if bentrok:
            db.close()
            messagebox.showwarning("Jadwal Bentrok",
                f"Ruangan {data['ruangan']} sudah dipakai pada hari {data['hari']} "
                f"di jam tersebut (ID jadwal {bentrok[0]}, {bentrok[1]}).")
            return
        placeholders = ", ".join(["%s"] * len(KOLOM_INPUT))
        sql = f"INSERT INTO jadwal_kuliah ({', '.join(KOLOM_INPUT)}) VALUES ({placeholders})"
        cursor.execute(sql, [data[c] for c in KOLOM_INPUT])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
        clear_fields()
        load_data()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menambah data: {e}")

# Memperbarui jadwal yang dipilih (id_jadwal dipakai sebagai acuan WHERE)
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
        bentrok = cek_bentrok(cursor, data, data["id_jadwal"])
        if bentrok:
            db.close()
            messagebox.showwarning("Jadwal Bentrok",
                f"Ruangan {data['ruangan']} sudah dipakai pada hari {data['hari']} "
                f"di jam tersebut (ID jadwal {bentrok[0]}, {bentrok[1]}).")
            return
        set_clause = ", ".join(f"{c}=%s" for c in KOLOM_INPUT)
        sql = f"UPDATE jadwal_kuliah SET {set_clause} WHERE id_jadwal=%s"
        cursor.execute(sql, [data[c] for c in KOLOM_INPUT] + [data["id_jadwal"]])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
        clear_fields()
        load_data()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

# Menghapus jadwal
def hapus_data():
    if not tree.selection():
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin dihapus!")
        return
    id_jadwal = fields["id_jadwal"].get()
    kode = fields["kode_mk"].get()
    if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus jadwal {kode} (ID {id_jadwal})?"):
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM jadwal_kuliah WHERE id_jadwal = %s", (id_jadwal,))
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
            clear_fields()
            load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus data: {e}")

# Mencari jadwal berdasarkan kode MK, hari, atau ruangan
def cari_data():
    keyword = entry_cari.get().strip()
    if not keyword:
        load_data()
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        sql = f"""SELECT {', '.join(NAMA_KOLOM)} FROM jadwal_kuliah
                  WHERE kode_mk LIKE %s OR hari LIKE %s OR ruangan LIKE %s
                  ORDER BY id_jadwal"""
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
root.title("Aplikasi Jadwal Kuliah - SIAKAD")
root.geometry("850x520")

# Frame form input
frame_form = tk.LabelFrame(root, text=" Form Jadwal Kuliah ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

# Membuat label + input untuk setiap kolom secara otomatis (grid 2 kolom)
for i, (col, label, _) in enumerate(KOLOM):
    baris, kolom = i // 2, (i % 2) * 2
    tk.Label(frame_form, text=label).grid(row=baris, column=kolom, sticky="w", padx=5, pady=3)
    if col == "hari":
        widget = ttk.Combobox(frame_form, values=PILIHAN_HARI, state="readonly")
    elif col == "id_jadwal":
        # ID dibuat otomatis oleh database, jadi hanya untuk ditampilkan
        widget = tk.Entry(frame_form, state="readonly")
    else:
        widget = tk.Entry(frame_form)
    widget.grid(row=baris, column=kolom + 1, padx=5, pady=3, sticky="ew")
    fields[col] = widget

# Petunjuk format jam
tk.Label(frame_form, text="Format jam: HH:MM (contoh 08:00)", fg="gray").grid(
    row=3, column=0, columnspan=4, sticky="w", padx=5)

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
tk.Label(frame_btn, text="Cari Kode MK/Hari/Ruangan:").pack(side="right")

# Frame tabel
frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=15, pady=10)

tree = ttk.Treeview(frame_table, columns=NAMA_KOLOM, show="headings")
for col, label, lebar in KOLOM:
    tree.heading(col, text=label)
    tree.column(col, width=lebar, minwidth=60)

tree.bind("<<TreeviewSelect>>", select_item)

scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Tampilkan data awal
load_data()

# Jalankan loop utama GUI
root.mainloop()
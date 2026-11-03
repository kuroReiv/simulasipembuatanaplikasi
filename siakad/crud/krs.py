# Mengimpor Decimal untuk menampilkan nilai angka dari database dengan format rapi
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

# --- DEFINISI KOLOM ---
# Setiap item: (nama kolom di database, label di form/tabel, lebar kolom tabel)
KOLOM = [
    ("id_krs",         "ID KRS",         60),
    ("nim",            "NIM",            100),
    ("kode_mk",        "Kode MK",        90),
    ("semester_ambil", "Semester Ambil", 100),
    ("tahun_ajaran",   "Tahun Ajaran",   100),
    ("nilai_huruf",    "Nilai Huruf",    80),
    ("nilai_angka",    "Nilai Angka",    80),
]
NAMA_KOLOM = [k[0] for k in KOLOM]
# Kolom yang diisi pengguna (id_krs dibuat otomatis oleh database / AUTO_INCREMENT)
KOLOM_INPUT = [c for c in NAMA_KOLOM if c != "id_krs"]

# Konversi nilai huruf ke angka (bobot). Silakan sesuaikan dengan aturan kampus Anda.
BOBOT_NILAI = {
    "A": "4.00", "A-": "3.75", "B+": "3.30", "B": "3.00", "B-": "2.75",
    "C+": "2.30", "C": "2.00", "D": "1.00", "E": "0.00",
}
# Pilihan pertama kosong untuk KRS yang nilainya belum keluar
PILIHAN_HURUF = [""] + list(BOBOT_NILAI.keys())

# Dictionary penampung widget input: {nama_kolom: widget}
fields = {}

# --- FUNGSI BANTU ---
# Mengubah nilai dari database menjadi teks tampilan (None -> kosong, Decimal -> 2 desimal)
def tampil(v):
    if v is None:
        return ""
    if isinstance(v, (Decimal, float)):
        return f"{v:.2f}"
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

# Saat nilai huruf dipilih, isi nilai angka otomatis (masih bisa diubah manual)
def isi_nilai_angka(event):
    huruf = fields["nilai_huruf"].get()
    set_field(fields["nilai_angka"], BOBOT_NILAI.get(huruf, ""))

# Mengambil nilai form, memvalidasi, lalu mengembalikan dict (atau None jika tidak valid)
def ambil_dan_validasi():
    data = {col: fields[col].get().strip() for col in NAMA_KOLOM}

    # NIM, Kode MK, Semester, dan Tahun Ajaran wajib diisi
    for col, label in [("nim", "NIM"), ("kode_mk", "Kode MK"),
                       ("semester_ambil", "Semester Ambil"), ("tahun_ajaran", "Tahun Ajaran")]:
        if not data[col]:
            messagebox.showwarning("Warning", f"{label} wajib diisi!")
            return None

    # Semester harus angka 1-14
    if not data["semester_ambil"].isdigit() or not (1 <= int(data["semester_ambil"]) <= 14):
        messagebox.showwarning("Warning", "Semester Ambil harus berupa angka 1 - 14!")
        return None

    # Tahun ajaran berformat YYYY/YYYY dan tahun kedua = tahun pertama + 1
    bagian = data["tahun_ajaran"].split("/")
    if (len(bagian) != 2 or not all(b.isdigit() and len(b) == 4 for b in bagian)
            or int(bagian[1]) != int(bagian[0]) + 1):
        messagebox.showwarning("Warning", "Tahun Ajaran harus berformat YYYY/YYYY (contoh: 2023/2024)!")
        return None

    # Nilai huruf boleh kosong (nilai belum keluar) -> disimpan sebagai NULL
    if not data["nilai_huruf"]:
        data["nilai_huruf"] = None

    # Nilai angka boleh kosong, jika diisi harus angka 0 - 4
    if data["nilai_angka"]:
        try:
            angka = float(data["nilai_angka"])
        except ValueError:
            messagebox.showwarning("Warning", "Nilai Angka harus berupa angka (contoh: 3.75)!")
            return None
        if not (0 <= angka <= 4):
            messagebox.showwarning("Warning", "Nilai Angka harus antara 0.00 dan 4.00!")
            return None
        data["nilai_angka"] = f"{angka:.2f}"
    else:
        data["nilai_angka"] = None

    return data

# Memeriksa apakah mahasiswa sudah punya KRS yang sama (NIM, MK, semester, tahun ajaran)
def cek_duplikat(cursor, data, id_krs):
    sql = """SELECT id_krs FROM krs
             WHERE nim=%s AND kode_mk=%s AND semester_ambil=%s AND tahun_ajaran=%s
               AND id_krs <> %s"""
    cursor.execute(sql, (data["nim"], data["kode_mk"], data["semester_ambil"],
                         data["tahun_ajaran"], id_krs))
    return cursor.fetchone()

# --- FUNGSI CRUD ---
# Menampilkan baris hasil query ke Treeview
def isi_tabel(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", "end", values=[tampil(v) for v in row])

# Memuat seluruh data KRS
def load_data():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT {', '.join(NAMA_KOLOM)} FROM krs ORDER BY id_krs")
        isi_tabel(cursor.fetchall())
        db.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")

# Menambahkan KRS baru (id_krs otomatis)
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
                f"KRS yang sama sudah ada (ID KRS {duplikat[0]}).")
            return
        placeholders = ", ".join(["%s"] * len(KOLOM_INPUT))
        sql = f"INSERT INTO krs ({', '.join(KOLOM_INPUT)}) VALUES ({placeholders})"
        cursor.execute(sql, [data[c] for c in KOLOM_INPUT])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
        clear_fields()
        load_data()
    except Exception as e:
        # Termasuk error foreign key jika NIM / Kode MK belum terdaftar
        messagebox.showerror("Error", f"Gagal menambah data: {e}")

# Memperbarui KRS yang dipilih (id_krs dipakai sebagai acuan WHERE)
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
        duplikat = cek_duplikat(cursor, data, data["id_krs"])
        if duplikat:
            db.close()
            messagebox.showwarning("Data Ganda",
                f"KRS yang sama sudah ada (ID KRS {duplikat[0]}).")
            return
        set_clause = ", ".join(f"{c}=%s" for c in KOLOM_INPUT)
        sql = f"UPDATE krs SET {set_clause} WHERE id_krs=%s"
        cursor.execute(sql, [data[c] for c in KOLOM_INPUT] + [data["id_krs"]])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
        clear_fields()
        load_data()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

# Menghapus KRS
def hapus_data():
    if not tree.selection():
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin dihapus!")
        return
    id_krs = fields["id_krs"].get()
    nim = fields["nim"].get()
    kode = fields["kode_mk"].get()
    if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus KRS {nim} - {kode} (ID {id_krs})?"):
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM krs WHERE id_krs = %s", (id_krs,))
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
            clear_fields()
            load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus data: {e}")

# Mencari KRS berdasarkan NIM, kode MK, atau tahun ajaran
def cari_data():
    keyword = entry_cari.get().strip()
    if not keyword:
        load_data()
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        sql = f"""SELECT {', '.join(NAMA_KOLOM)} FROM krs
                  WHERE nim LIKE %s OR kode_mk LIKE %s OR tahun_ajaran LIKE %s
                  ORDER BY id_krs"""
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
root.title("Aplikasi KRS - SIAKAD")
root.geometry("850x540")

# Frame form input
frame_form = tk.LabelFrame(root, text=" Form KRS ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

# Membuat label + input untuk setiap kolom secara otomatis (grid 2 kolom)
for i, (col, label, _) in enumerate(KOLOM):
    baris, kolom = i // 2, (i % 2) * 2
    tk.Label(frame_form, text=label).grid(row=baris, column=kolom, sticky="w", padx=5, pady=3)
    if col == "nilai_huruf":
        widget = ttk.Combobox(frame_form, values=PILIHAN_HURUF, state="readonly")
        widget.bind("<<ComboboxSelected>>", isi_nilai_angka)
    elif col == "id_krs":
        # ID dibuat otomatis oleh database, jadi hanya untuk ditampilkan
        widget = tk.Entry(frame_form, state="readonly")
    else:
        widget = tk.Entry(frame_form)
    widget.grid(row=baris, column=kolom + 1, padx=5, pady=3, sticky="ew")
    fields[col] = widget

# Petunjuk pengisian
tk.Label(frame_form, text="Tahun Ajaran: YYYY/YYYY (contoh 2023/2024). Nilai boleh dikosongkan jika belum keluar.",
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
tk.Label(frame_btn, text="Cari NIM/Kode MK/Tahun:").pack(side="right")

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
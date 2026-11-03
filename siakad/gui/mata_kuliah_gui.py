# Mengimpor modul tkinter dasar untuk pembuatan komponen GUI
import tkinter as tk
# Mengimpor ttk (Treeview) dan messagebox untuk dialog pop-up
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

# Nama tabel mata kuliah di database (ubah di sini jika nama tabelmu berbeda)
TABEL = "mata_kuliah"

# =====================================================================
# --- HALAMAN LOGIN ---
# Login memakai data yang sudah ada di tabel mata kuliah (tanpa daftar akun):
#   Username = kode_mk    (contoh: MK001)
#   Password = nip_dosen  (contoh: D001)
# Jadi pasangan yang valid mengikuti baris data, misalnya MK001 / D001, MK002 / D004, dst.
# =====================================================================
KOLOM_USERNAME = "kode_mk"
KOLOM_PASSWORD = "nip_dosen"

# Memeriksa username & password ke database, True jika ada baris yang cocok
def cek_login(username, password):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(
        f"SELECT 1 FROM {TABEL} WHERE {KOLOM_USERNAME}=%s AND {KOLOM_PASSWORD}=%s",
        (username, password)
    )
    hasil = cursor.fetchone()
    db.close()
    return hasil is not None

# Menampilkan jendela login. Mengembalikan True jika login berhasil, False jika ditutup/gagal
def tampilkan_login():
    status = {"berhasil": False}

    win = tk.Tk()
    win.title("Login - SIAKAD")
    lebar, tinggi = 480, 320
    # Letakkan jendela di tengah layar
    x = (win.winfo_screenwidth() - lebar) // 2
    y = (win.winfo_screenheight() - tinggi) // 2
    win.geometry(f"{lebar}x{tinggi}+{x}+{y}")
    win.resizable(False, False)

    tk.Label(win, text="SIAKAD LOGIN", font=("Arial", 16, "bold")).pack(pady=(30, 25))

    frame = tk.Frame(win)
    frame.pack()

    tk.Label(frame, text="Username:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=8)
    entry_user = tk.Entry(frame, width=28, font=("Arial", 10))
    entry_user.grid(row=0, column=1, padx=5, pady=8)

    tk.Label(frame, text="Password:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=5, pady=8)
    entry_pass = tk.Entry(frame, width=28, font=("Arial", 10), show="*")
    entry_pass.grid(row=1, column=1, padx=5, pady=8)

    def proses_login(event=None):
        username = entry_user.get().strip()
        password = entry_pass.get().strip()
        if not username or not password:
            messagebox.showwarning("Warning", "Username dan password wajib diisi!", parent=win)
            return
        try:
            if cek_login(username, password):
                status["berhasil"] = True
                win.destroy()
            else:
                messagebox.showerror("Login Gagal", "Username atau password salah!", parent=win)
                entry_pass.delete(0, tk.END)
                entry_pass.focus()
        except Exception as e:
            messagebox.showerror("Database Error", f"Gagal terhubung ke database: {e}", parent=win)

    tk.Button(win, text="Login", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
              width=20, command=proses_login).pack(pady=25)

    # Tekan Enter untuk login
    win.bind("<Return>", proses_login)
    entry_user.focus()

    win.mainloop()
    return status["berhasil"]

# Jika login gagal atau jendela login ditutup, program berhenti di sini
if not tampilkan_login():
    raise SystemExit

# =====================================================================
# --- APLIKASI UTAMA (MATA KULIAH) ---
# =====================================================================

# --- DEFINISI KOLOM ---
# Setiap item: (nama kolom di database, label di form/tabel, lebar kolom tabel)
KOLOM = [
    ("kode_mk",   "Kode MK",   90),
    ("nama_mk",   "Nama MK",   260),
    ("sks",       "SKS",       60),
    ("semester",  "Semester",  80),
    ("nip_dosen", "NIP Dosen", 100),
]
NAMA_KOLOM = [k[0] for k in KOLOM]
# Kolom yang diubah saat Edit (kode_mk adalah kunci utama sehingga dikunci saat edit)
KOLOM_EDIT = [c for c in NAMA_KOLOM if c != "kode_mk"]

# Dictionary penampung widget input: {nama_kolom: widget}
fields = {}

# --- FUNGSI BANTU ---
# Mengubah nilai dari database menjadi teks tampilan (None -> kosong)
def tampil(v):
    if v is None:
        return ""
    return v

# Mengatur isi sebuah widget Entry, termasuk Entry yang readonly
def set_field(widget, value):
    status_awal = str(widget.cget("state"))
    widget.config(state="normal")
    widget.delete(0, tk.END)
    widget.insert(0, value)
    widget.config(state=status_awal)

# Mengosongkan seluruh input form
def clear_fields(keep_selection=False):
    for widget in fields.values():
        set_field(widget, "")
    if not keep_selection:
        # Kode MK boleh diisi lagi (untuk data baru) dan pilihan baris di tabel dihapus
        fields["kode_mk"].config(state="normal")
        if tree.selection():
            tree.selection_remove(tree.selection())

# Mengambil nilai form, memvalidasi, lalu mengembalikan dict (atau None jika tidak valid)
def ambil_dan_validasi():
    data = {col: fields[col].get().strip() for col in NAMA_KOLOM}

    # Semua field wajib diisi
    for col, label, _ in KOLOM:
        if not data[col]:
            messagebox.showwarning("Warning", f"{label} wajib diisi!")
            return None

    # SKS harus angka 1-6
    if not data["sks"].isdigit() or not (1 <= int(data["sks"]) <= 6):
        messagebox.showwarning("Warning", "SKS harus berupa angka 1 - 6!")
        return None

    # Semester harus angka 1-14
    if not data["semester"].isdigit() or not (1 <= int(data["semester"]) <= 14):
        messagebox.showwarning("Warning", "Semester harus berupa angka 1 - 14!")
        return None

    return data

# Memeriksa apakah kode MK sudah dipakai
def cek_duplikat(cursor, kode_mk):
    cursor.execute(f"SELECT nama_mk FROM {TABEL} WHERE kode_mk=%s", (kode_mk,))
    return cursor.fetchone()

# --- FUNGSI CRUD ---
# Menampilkan baris hasil query ke Treeview
def isi_tabel(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", "end", values=[tampil(v) for v in row])

# Memuat seluruh data mata kuliah
def load_data():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT {', '.join(NAMA_KOLOM)} FROM {TABEL} ORDER BY kode_mk")
        isi_tabel(cursor.fetchall())
        db.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")

# Menambahkan mata kuliah baru
def tambah_data():
    # Jika baris sedang dipilih (kode MK terkunci), minta pengguna menekan Clear dulu
    if tree.selection():
        messagebox.showwarning("Warning", "Tekan Clear dulu untuk mengisi data baru!")
        return
    data = ambil_dan_validasi()
    if data is None:
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        duplikat = cek_duplikat(cursor, data["kode_mk"])
        if duplikat:
            db.close()
            messagebox.showwarning("Data Ganda",
                f"Kode MK {data['kode_mk']} sudah terdaftar ({duplikat[0]}).")
            return
        placeholders = ", ".join(["%s"] * len(NAMA_KOLOM))
        sql = f"INSERT INTO {TABEL} ({', '.join(NAMA_KOLOM)}) VALUES ({placeholders})"
        cursor.execute(sql, [data[c] for c in NAMA_KOLOM])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
        clear_fields()
        load_data()
    except Exception as e:
        # Termasuk error foreign key jika NIP Dosen belum terdaftar
        messagebox.showerror("Error", f"Gagal menambah data: {e}")

# Memperbarui mata kuliah yang dipilih (kode_mk dipakai sebagai acuan WHERE)
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
        set_clause = ", ".join(f"{c}=%s" for c in KOLOM_EDIT)
        sql = f"UPDATE {TABEL} SET {set_clause} WHERE kode_mk=%s"
        cursor.execute(sql, [data[c] for c in KOLOM_EDIT] + [data["kode_mk"]])
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
        clear_fields()
        load_data()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

# Menghapus mata kuliah
def hapus_data():
    if not tree.selection():
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin dihapus!")
        return
    kode = fields["kode_mk"].get()
    nama = fields["nama_mk"].get()
    if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus mata kuliah {kode} - {nama}?"):
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute(f"DELETE FROM {TABEL} WHERE kode_mk = %s", (kode,))
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
            clear_fields()
            load_data()
        except Exception as e:
            # Biasanya gagal jika mata kuliah masih dipakai di jadwal_kuliah / krs
            messagebox.showerror("Error", f"Gagal menghapus data "
                                          f"(mungkin masih dipakai di data lain): {e}")

# Mencari mata kuliah berdasarkan kode MK, nama MK, atau NIP dosen
def cari_data():
    keyword = entry_cari.get().strip()
    if not keyword:
        load_data()
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        sql = f"""SELECT {', '.join(NAMA_KOLOM)} FROM {TABEL}
                  WHERE kode_mk LIKE %s OR nama_mk LIKE %s OR nip_dosen LIKE %s
                  ORDER BY kode_mk"""
        like = f"%{keyword}%"
        cursor.execute(sql, (like, like, like))
        isi_tabel(cursor.fetchall())
        db.close()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal mencari data: {e}")

# Saat baris tabel dipilih, isi form dengan data baris tersebut dan kunci Kode MK
def select_item(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0], "values")
        clear_fields(keep_selection=True)
        for col, val in zip(NAMA_KOLOM, values):
            set_field(fields[col], val)
        fields["kode_mk"].config(state="readonly")

# Logout: tutup aplikasi utama
def logout():
    if messagebox.askyesno("Logout", "Yakin ingin logout?"):
        root.destroy()

# --- GUI MAIN WINDOW ---
root = tk.Tk()
root.title("Aplikasi Mata Kuliah - SIAKAD")
root.geometry("850x520")

# Frame form input
frame_form = tk.LabelFrame(root, text=" Form Mata Kuliah ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

# Membuat label + input untuk setiap kolom secara otomatis (grid 2 kolom)
for i, (col, label, _) in enumerate(KOLOM):
    baris, kolom = i // 2, (i % 2) * 2
    tk.Label(frame_form, text=label).grid(row=baris, column=kolom, sticky="w", padx=5, pady=3)
    widget = tk.Entry(frame_form)
    widget.grid(row=baris, column=kolom + 1, padx=5, pady=3, sticky="ew")
    fields[col] = widget

# Petunjuk pengisian
tk.Label(frame_form, text="SKS: 1 - 6, Semester: 1 - 14. Kode MK tidak bisa diubah saat Edit.",
         fg="gray").grid(row=3, column=0, columnspan=4, sticky="w", padx=5)

frame_form.grid_columnconfigure(1, weight=1)
frame_form.grid_columnconfigure(3, weight=1)

# Frame tombol aksi
frame_btn = tk.Frame(root)
frame_btn.pack(fill="x", padx=15, pady=5)

tk.Button(frame_btn, text="Tambah", bg="#4CAF50", fg="white", command=tambah_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Edit", bg="#2196F3", fg="white", command=edit_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Hapus", bg="#f44336", fg="white", command=hapus_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Clear", bg="#9E9E9E", fg="white", command=clear_fields, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Logout", bg="#607D8B", fg="white", command=logout, width=12).pack(side="left", padx=5)

# Kolom pencarian di sisi kanan
tk.Button(frame_btn, text="Cari", bg="#FF9800", fg="white", command=cari_data, width=8).pack(side="right", padx=5)
entry_cari = tk.Entry(frame_btn, width=22)
entry_cari.pack(side="right", padx=5)
entry_cari.bind("<Return>", lambda e: cari_data())
tk.Label(frame_btn, text="Cari Kode/Nama MK/NIP:").pack(side="right")

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
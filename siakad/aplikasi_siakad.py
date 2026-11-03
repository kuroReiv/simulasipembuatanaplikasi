"""
Aplikasi SIAKAD untuk MAHASISWA (Tkinter + MySQL) - melihat dan mencari informasi langsung

Alur aplikasi:
  Halaman Login  ->  Halaman utama (tab-tab informasi)  ->  Logout  ->  kembali ke Login

Login (khusus mahasiswa, memakai data tabel `mahasiswa` di database `siakad`):
  Username = NIM
  Password = email mahasiswa

Setelah login, mahasiswa bisa MELIHAT dan MENCARI data (tidak ada tombol
Tambah/Edit/Hapus). Tab yang tersedia:
  Profil Saya, Dosen, Mahasiswa, Mata Kuliah, Jadwal Kuliah, KRS, Pembayaran UKT

Cara mencari: cukup ketik langsung pada kolom di bagian "Detail" di tiap tab, tabel
otomatis tersaring. Klik satu baris untuk melihat detailnya, tombol Reset untuk
menampilkan semua data kembali.

Jalankan: python siakad_mahasiswa.py
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ======================= PENGATURAN =======================
DB_CONFIG = {
    "host": "localhost",      # Alamat host server MySQL
    "user": "root",           # Username MySQL
    "password": "",           # Password (kosongkan jika tidak ada)
    "database": "siakad",     # Nama database
}

# Pengaturan siapa yang datanya boleh dicari/dilihat (berlaku di tab KRS dan Pembayaran UKT):
#   True  = bisa melihat data semua mahasiswa
#   False = hanya data milik mahasiswa yang sedang login
KRS_SEMUA = True
PEMBAYARAN_SEMUA = False   # data pembayaran bersifat pribadi, jadi default hanya milik sendiri

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


# ======================= FUNGSI BANTU =======================
# Mengubah nilai dari database menjadi teks tampilan
# (None -> kosong, TIME -> HH:MM:SS, Decimal -> 2 desimal, DATE -> YYYY-MM-DD)
def tampil(v):
    if v is None:
        return ""
    if isinstance(v, timedelta):
        total = int(v.total_seconds())
        return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"
    if isinstance(v, (Decimal, float)):
        return f"{v:.2f}"
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, date):
        return v.isoformat()
    return str(v)


# Mengatur isi sebuah Entry
def set_field(widget, value):
    widget.delete(0, tk.END)
    widget.insert(0, value)


def tengah(win, lebar, tinggi):
    x = max((win.winfo_screenwidth() - lebar) // 2, 0)
    y = max((win.winfo_screenheight() - tinggi) // 2 - 20, 0)
    win.geometry(f"{lebar}x{tinggi}+{x}+{y}")


# Mengambil daftar nama kolom yang benar-benar ada di sebuah tabel (None jika gagal)
def ambil_kolom_tabel(tabel):
    db = None
    try:
        db = connect_db()
        cur = db.cursor()
        cur.execute(f"SHOW COLUMNS FROM {tabel}")
        return [r[0] for r in cur.fetchall()]
    except Exception:
        return None
    finally:
        if db is not None and db.is_connected():
            db.close()


# Menyesuaikan konfigurasi tab dengan kolom asli di database, supaya aplikasi tidak error
# bila ada kolom yang tidak ada / namanya berbeda:
#   - kolom yang tidak ada di tabel dilewati
#   - jika cfg["semua_kolom"] = True, semua kolom asli tabel ditampilkan
def sesuaikan_cfg(cfg):
    asli = ambil_kolom_tabel(cfg["tabel"])
    if not asli:
        return cfg
    cfg = dict(cfg)
    dikenal = {c: (label, lebar) for c, label, lebar in cfg["kolom"]}
    if cfg.get("semua_kolom"):
        cfg["kolom"] = [(c, *dikenal.get(c, (c.replace("_", " ").title(), 120))) for c in asli]
    else:
        cfg["kolom"] = [k for k in cfg["kolom"] if k[0] in asli]
    if cfg["urut"] not in asli:
        cfg["urut"] = cfg["kolom"][0][0]
    return cfg


# ======================= KONFIGURASI TIAP TAB =======================
# kolom: (nama kolom di database, label, lebar kolom tabel)
CFG_DOSEN = {
    "judul": "Data Dosen", "tabel": "dosen", "urut": "nip", "semua_kolom": True,
    "kolom": [
        ("nip", "NIP", 80),
        ("nama_dosen", "Nama Dosen", 210),
        ("jenis_kelamin", "Jenis Kelamin", 110),
        ("email", "Email", 180),
        ("no_telepon", "No Telepon", 120),
        ("pendidikan", "Pendidikan Terakhir", 130),
        ("bidang_keahlian", "Bidang Keahlian", 190),
    ],
}

# Tab "Mahasiswa" hanya menampilkan informasi umum. Email, alamat, no telepon, dan
# tanggal lahir mahasiswa lain tidak ditampilkan (email dipakai sebagai password login).
CFG_MAHASISWA = {
    "judul": "Data Mahasiswa", "tabel": "mahasiswa", "urut": "nim",
    "kolom": [
        ("nim", "NIM", 100),
        ("nama_lengkap", "Nama Lengkap", 220),
        ("jenis_kelamin", "Jenis Kelamin", 110),
        ("jurusan", "Jurusan", 180),
        ("angkatan", "Angkatan", 80),
        ("status", "Status", 90),
    ],
}

# Kolom lengkap, hanya dipakai untuk tab "Profil Saya" (data milik sendiri)
KOLOM_PROFIL = [
    ("nim", "NIM"), ("nama_lengkap", "Nama Lengkap"), ("jenis_kelamin", "Jenis Kelamin"),
    ("tanggal_lahir", "Tanggal Lahir"), ("tempat_lahir", "Tempat Lahir"),
    ("alamat", "Alamat"), ("no_telepon", "No Telepon"), ("email", "Email"),
    ("jurusan", "Jurusan"), ("angkatan", "Angkatan"), ("status", "Status"),
]

CFG_MATKUL = {
    "judul": "Mata Kuliah", "tabel": "mata_kuliah", "urut": "kode_mk",
    "kolom": [
        ("kode_mk", "Kode MK", 90),
        ("nama_mk", "Nama MK", 260),
        ("sks", "SKS", 60),
        ("semester", "Semester", 80),
        ("nip_dosen", "NIP Dosen", 100),
    ],
}

CFG_JADWAL = {
    "judul": "Jadwal Kuliah", "tabel": "jadwal_kuliah", "urut": "id_jadwal",
    "kolom": [
        ("id_jadwal", "ID Jadwal", 70),
        ("kode_mk", "Kode MK", 100),
        ("hari", "Hari", 90),
        ("jam_mulai", "Jam Mulai", 100),
        ("jam_selesai", "Jam Selesai", 100),
        ("ruangan", "Ruangan", 180),
    ],
}

CFG_KRS = {
    "judul": "KRS", "tabel": "krs", "urut": "id_krs", "kolom_nim": "nim",
    "kolom": [
        ("id_krs", "ID KRS", 60),
        ("nim", "NIM", 100),
        ("kode_mk", "Kode MK", 90),
        ("semester_ambil", "Semester Ambil", 100),
        ("tahun_ajaran", "Tahun Ajaran", 100),
        ("nilai_huruf", "Nilai Huruf", 80),
        ("nilai_angka", "Nilai Angka", 80),
    ],
}

CFG_PEMBAYARAN = {
    "judul": "Pembayaran UKT", "tabel": "pembayaran_ukt", "urut": "id_pembayaran",
    "kolom_nim": "nim",
    "kolom": [
        ("id_pembayaran", "ID Pembayaran", 100),
        ("nim", "NIM", 90),
        ("semester", "Semester", 70),
        ("tahun_ajaran", "Tahun Ajaran", 100),
        ("jumlah_bayar", "Jumlah Bayar", 110),
        ("tanggal_bayar", "Tanggal Bayar", 100),
        ("metode_pembayaran", "Metode Pembayaran", 130),
        ("status", "Status", 100),
    ],
}


# ======================= PANEL DATA (HANYA LIHAT) =======================
# Satu kelas dipakai untuk semua tab. Kolom pada bagian "Detail" berfungsi ganda:
#   - diketik  -> tabel langsung tersaring (pencarian langsung per kolom)
#   - klik baris tabel -> kolom Detail terisi dengan data baris tersebut
class DataPanel(ttk.Frame):
    def __init__(self, master, cfg, filter_nim=None):
        super().__init__(master, padding=8)
        self.cfg = sesuaikan_cfg(cfg)
        self.filter_nim = filter_nim    # Jika diisi, hanya tampilkan data milik NIM ini
        self.kolom = [k[0] for k in self.cfg["kolom"]]
        self.fields = {}    # {nama_kolom: Entry}
        self.rows = {}      # {iid: [nilai tampilan]} - menyimpan teks asli (mis. nol di depan)
        self.dari_pilihan = False   # True jika isi kolom Detail berasal dari klik baris tabel
        self._job = None            # penunda pencarian (agar tidak query tiap ketikan)

        self._bangun_detail()
        self._bangun_bar()
        self._bangun_tabel()
        self.load_data()

    # ---------- Tampilan ----------
    def _bangun_detail(self):
        form = tk.LabelFrame(self, text=f" Detail {self.cfg['judul']} ", padx=10, pady=10)
        form.pack(fill="x", pady=(0, 6))
        for i, (col, label, _) in enumerate(self.cfg["kolom"]):
            baris, kolom = i // 2, (i % 2) * 2
            tk.Label(form, text=label).grid(row=baris, column=kolom, sticky="w", padx=5, pady=3)
            w = tk.Entry(form)
            w.grid(row=baris, column=kolom + 1, padx=5, pady=3, sticky="ew")
            w.bind("<KeyRelease>", lambda e, c=col: self.saat_ketik(c))
            self.fields[col] = w
        baris_hint = (len(self.cfg["kolom"]) + 1) // 2
        tk.Label(form, text="Ketik pada kolom di atas untuk mencari langsung (tabel ikut tersaring). "
                            "Klik baris tabel untuk melihat detailnya.",
                 fg="gray").grid(row=baris_hint, column=0, columnspan=4, sticky="w", padx=5)
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)

    def _bangun_bar(self):
        bar = tk.Frame(self)
        bar.pack(fill="x", pady=4)
        tk.Button(bar, text="Reset", bg="#9E9E9E", fg="white", activebackground="#9E9E9E",
                  activeforeground="white", width=12, cursor="hand2",
                  command=self.reset).pack(side="left", padx=5)
        self.lbl_jumlah = tk.Label(bar, text="", fg="gray")
        self.lbl_jumlah.pack(side="left", padx=10)

    def _bangun_tabel(self):
        wrap = tk.Frame(self)
        wrap.pack(fill="both", expand=True, pady=(6, 0))
        self.tree = ttk.Treeview(wrap, columns=self.kolom, show="headings")
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)
        for col, label, lebar in self.cfg["kolom"]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=lebar, minwidth=50)
        self.tree.bind("<<TreeviewSelect>>", self.select_item)

    # ---------- Aksi ----------
    # Dipanggil setiap kali mengetik pada salah satu kolom Detail
    def saat_ketik(self, col):
        # Jika isi Detail berasal dari klik baris, kosongkan kolom lain: pencarian
        # hanya memakai kolom yang sedang diketik
        if self.dari_pilihan:
            for c, w in self.fields.items():
                if c != col:
                    w.delete(0, tk.END)
            self.dari_pilihan = False
        # Tunda sebentar agar tidak query database di setiap ketikan
        if self._job is not None:
            self.after_cancel(self._job)
        self._job = self.after(250, self.load_data)

    # Saat baris tabel dipilih, tampilkan detailnya pada kolom di atas
    def select_item(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        for col, val in zip(self.kolom, self.rows[sel[0]]):
            set_field(self.fields[col], val)
        self.dari_pilihan = True

    # Mengosongkan kolom Detail dan menampilkan seluruh data kembali
    def reset(self):
        for w in self.fields.values():
            w.delete(0, tk.END)
        self.dari_pilihan = False
        self.load_data()

    def _isi_tabel(self, rows):
        self.tree.delete(*self.tree.get_children())
        self.rows.clear()
        for i, row in enumerate(rows):
            nilai = [tampil(v) for v in row]
            iid = str(i)
            self.rows[iid] = nilai
            self.tree.insert("", "end", iid=iid, values=nilai)
        self.lbl_jumlah.config(text=f"{len(self.rows)} data")

    # Memuat data dari database, disaring oleh isi kolom Detail (jika ada)
    def load_data(self):
        self._job = None
        sql = f"SELECT {', '.join(self.kolom)} FROM {self.cfg['tabel']}"
        kondisi, param = [], []
        if self.filter_nim is not None:
            kondisi.append(f"{self.cfg['kolom_nim']} = %s")
            param.append(self.filter_nim)
        for col in self.kolom:
            teks = self.fields[col].get().strip()
            if teks:
                kondisi.append(f"{col} LIKE %s")
                param.append(f"%{teks}%")
        if kondisi:
            sql += " WHERE " + " AND ".join(kondisi)
        sql += f" ORDER BY {self.cfg['urut']}"
        db = None
        try:
            db = connect_db()
            cur = db.cursor()
            cur.execute(sql, param)
            self._isi_tabel(cur.fetchall())
        except Exception as e:
            messagebox.showerror("Database Error",
                                 f"Gagal mengambil data {self.cfg['judul']}: {e}")
        finally:
            if db is not None and db.is_connected():
                db.close()


# ======================= TAB: PROFIL SAYA =======================
class ProfilPanel(ttk.Frame):
    def __init__(self, master, nim):
        super().__init__(master, padding=14)
        box = tk.LabelFrame(self, text=" Profil Saya ", padx=16, pady=12)
        box.pack(anchor="nw")

        asli = ambil_kolom_tabel("mahasiswa")
        daftar = [k for k in KOLOM_PROFIL if asli is None or k[0] in asli]
        kolom = [k[0] for k in daftar]
        data = {}
        db = None
        try:
            db = connect_db()
            cur = db.cursor()
            cur.execute(f"SELECT {', '.join(kolom)} FROM mahasiswa WHERE nim=%s", (nim,))
            row = cur.fetchone()
            if row:
                data = dict(zip(kolom, row))
        except Exception as e:
            messagebox.showerror("Database Error", f"Gagal mengambil profil: {e}")
        finally:
            if db is not None and db.is_connected():
                db.close()

        for i, (col, label) in enumerate(daftar):
            tk.Label(box, text=f"{label}:", anchor="w").grid(
                row=i, column=0, sticky="nw", pady=3, padx=(0, 16))
            tk.Label(box, text=tampil(data.get(col)) or "-", font=("Arial", 10, "bold"),
                     wraplength=450, justify="left", anchor="w").grid(
                row=i, column=1, sticky="w", pady=3)


# ======================= HALAMAN LOGIN =======================
# Mengecek login mahasiswa ke database (NIM + email). Mengembalikan dict atau None.
def cek_login(nim, email):
    db = connect_db()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT nim, nama_lengkap FROM mahasiswa "
                    "WHERE nim = %s AND LOWER(email) = LOWER(%s)", (nim, email))
        r = cur.fetchone()
        if r:
            return {"id": r["nim"], "nama": r["nama_lengkap"]}
        return None
    finally:
        db.close()


class LoginFrame(tk.Frame):
    def __init__(self, master, aksi_login, pesan=""):
        super().__init__(master)
        self.aksi_login = aksi_login

        tk.Label(self, text="SIAKAD LOGIN", font=("Arial", 16, "bold")).pack(pady=(30, 5))
        # Pesan singkat (mis. setelah logout)
        tk.Label(self, text=pesan, fg="#4CAF50", font=("Arial", 10)).pack(pady=(0, 10))

        form = tk.Frame(self)
        form.pack()
        tk.Label(form, text="Username:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="e", padx=5, pady=8)
        self.entry_user = tk.Entry(form, width=28, font=("Arial", 10))
        self.entry_user.grid(row=0, column=1, padx=5, pady=8)
        tk.Label(form, text="Password:", font=("Arial", 10)).grid(
            row=1, column=0, sticky="e", padx=5, pady=8)
        self.entry_pass = tk.Entry(form, width=28, font=("Arial", 10), show="*")
        self.entry_pass.grid(row=1, column=1, padx=5, pady=8)

        self.v_lihat = tk.BooleanVar(value=False)
        tk.Checkbutton(form, text="Tampilkan password", variable=self.v_lihat,
                       command=self.toggle).grid(row=2, column=1, sticky="w", padx=5)

        tk.Label(self, text="Username = NIM   |   Password = Email",
                 fg="gray", font=("Arial", 9)).pack(pady=(10, 0))

        tk.Button(self, text="Login", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                  activebackground="#45a049", activeforeground="white", width=20,
                  cursor="hand2", command=self.kirim).pack(pady=18)

        self.entry_user.focus()
        self.entry_user.bind("<Return>", lambda e: self.entry_pass.focus())
        self.entry_pass.bind("<Return>", lambda e: self.kirim())

    def toggle(self):
        self.entry_pass.config(show="" if self.v_lihat.get() else "*")

    def kirim(self):
        self.aksi_login(self.entry_user.get().strip(), self.entry_pass.get().strip(), self)


# ======================= HALAMAN UTAMA (SETELAH LOGIN) =======================
class MainFrame(ttk.Frame):
    def __init__(self, master, user, aksi_logout):
        super().__init__(master, padding=8)

        # Bagian atas: identitas pengguna + tombol Logout
        bar = tk.Frame(self)
        bar.pack(fill="x", pady=(0, 6))
        tk.Label(bar, text="SIAKAD", font=("Arial", 14, "bold")).pack(side="left", padx=(4, 16))
        tk.Label(bar, text=f"Login sebagai: {user['nama']} (NIM {user['id']})",
                 font=("Arial", 10), fg="#4CAF50").pack(side="left")
        tk.Button(bar, text="Logout", bg="#f44336", fg="white", activebackground="#d32f2f",
                  activeforeground="white", font=("Arial", 10, "bold"), width=12,
                  cursor="hand2", command=aksi_logout).pack(side="right", padx=4)
        ttk.Separator(self).pack(fill="x", pady=(0, 6))

        # Tab-tab informasi
        milik_krs = None if KRS_SEMUA else user["id"]
        milik_bayar = None if PEMBAYARAN_SEMUA else user["id"]
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        nb.add(ProfilPanel(nb, user["id"]), text="  Profil Saya  ")
        nb.add(DataPanel(nb, CFG_DOSEN), text="  Dosen  ")
        nb.add(DataPanel(nb, CFG_MAHASISWA), text="  Mahasiswa  ")
        nb.add(DataPanel(nb, CFG_MATKUL), text="  Mata Kuliah  ")
        nb.add(DataPanel(nb, CFG_JADWAL), text="  Jadwal Kuliah  ")
        nb.add(DataPanel(nb, CFG_KRS, filter_nim=milik_krs), text="  KRS  ")
        nb.add(DataPanel(nb, CFG_PEMBAYARAN, filter_nim=milik_bayar), text="  Pembayaran UKT  ")


# ======================= APLIKASI UTAMA =======================
class Aplikasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.frame = None
        self.tampil_login()

    def ganti(self, frame):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = frame
        self.frame.pack(fill="both", expand=True)

    def tampil_login(self, pesan=""):
        self.title("Login - SIAKAD")
        self.minsize(1, 1)
        self.resizable(False, False)
        tengah(self, 480, 400)
        self.ganti(LoginFrame(self, self.proses_login, pesan))

    def tampil_utama(self, user):
        self.title("SIAKAD Mahasiswa - Sistem Informasi Akademik")
        self.resizable(True, True)
        tengah(self, 1100, 700)
        self.minsize(950, 600)
        self.ganti(MainFrame(self, user, self.proses_logout))

    def proses_login(self, nim, email, frame_login):
        if not nim or not email:
            messagebox.showwarning("Peringatan", "Username (NIM) dan Password (Email) wajib diisi!")
            return
        try:
            user = cek_login(nim, email)
        except Exception as e:
            messagebox.showerror("Database Error", f"Koneksi database bermasalah:\n{e}")
            return
        if user:
            self.tampil_utama(user)
        else:
            messagebox.showerror("Login Gagal", "Login gagal! Username atau Password salah.")
            frame_login.entry_pass.delete(0, tk.END)
            frame_login.entry_pass.focus()

    def proses_logout(self):
        if messagebox.askyesno("Logout", "Yakin ingin logout?"):
            self.tampil_login("Anda telah logout. Silakan login kembali.")


if __name__ == "__main__":
    Aplikasi().mainloop()
"""
Aplikasi Data Dosen - SIAKAD (Tkinter + SQLite) dengan Login & Logout

Login
  - Mahasiswa : username = NIM, password = email (dari tabel mahasiswa)
  - Admin     : username = admin, password = admin123 (ubah di bawah)

Setelah login
  - Tab "Data Dosen"    : tampilan form + tombol Tambah/Edit/Hapus/Clear + tabel dosen
  - Admin               : tab tambahan "Data Mahasiswa" (kelola data untuk login)
  - Mahasiswa           : tab tambahan "Profil Saya"; tab dosen hanya bisa dilihat
                          (ubah MAHASISWA_BOLEH_EDIT = True jika ingin boleh mengubah)

Data disimpan di mahasiswa.db (dibuat otomatis di folder yang sama dengan script).
Jalankan: python aplikasi_siakad.py
"""
import os
import re
import sqlite3
import tkinter as tk
from datetime import date, datetime
from tkinter import ttk, messagebox

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mahasiswa.db")

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
MAHASISWA_BOLEH_EDIT = False   # True = mahasiswa juga boleh tambah/edit/hapus dosen

# ---------- Konstanta data mahasiswa ----------
JENIS_KELAMIN = ["Laki-laki", "Perempuan"]
JURUSAN = ["Teknik Informatika", "Sistem Informasi", "Manajemen Informatika",
           "Teknik Sipil", "Manajemen", "Akuntansi", "Lainnya"]
STATUS = ["Aktif", "Cuti", "Lulus", "Non-aktif"]
TAHUN_INI = date.today().year
ANGKATAN = [str(t) for t in range(TAHUN_INI, TAHUN_INI - 10, -1)]

KOLOM = ["nim", "nama_lengkap", "jenis_kelamin", "tanggal_lahir", "tempat_lahir",
         "alamat", "no_telepon", "email", "jurusan", "angkatan", "status"]
LABEL = {
    "nim": "NIM", "nama_lengkap": "Nama lengkap", "jenis_kelamin": "Jenis kelamin",
    "tanggal_lahir": "Tanggal lahir (YYYY-MM-DD)", "tempat_lahir": "Tempat lahir",
    "alamat": "Alamat", "no_telepon": "No. telepon", "email": "Email",
    "jurusan": "Jurusan", "angkatan": "Angkatan", "status": "Status",
}

DATA_MAHASISWA = [
    ("2021001", "Budi Santoso", "Laki-laki", "2003-05-12", "Jakarta",
     "Jl. Merdeka No. 10", "081234567890", "budi@email.com",
     "Teknik Informatika", "2021", "Aktif"),
    ("2021002", "Siti Nurhaliza", "Perempuan", "2003-08-20", "Bandung",
     "Jl. Asia Afrika No. 5", "081234567891", "siti@email.com",
     "Sistem Informasi", "2021", "Aktif"),
    ("2022003", "Ahmad Fauzi", "Laki-laki", "2004-01-15", "Surabaya",
     "Jl. Diponegoro No. 22", "081234567892", "ahmad@email.com",
     "Teknik Informatika", "2022", "Aktif"),
    ("2022004", "Dewi Lestari", "Perempuan", "2004-03-10", "Yogyakarta",
     "Jl. Malioboro No. 8", "081234567893", "dewi@email.com",
     "Manajemen Informatika", "2022", "Aktif"),
    ("2023005", "Rizky Pratama", "Laki-laki", "2005-07-25", "Medan",
     "Jl. Gatot Subroto No. 17", "081234567894", "rizky@email.com",
     "Sistem Informasi", "2023", "Aktif"),
    ("2023006", "Putri Ayu", "Perempuan", "2005-11-30", "Semarang",
     "Jl. Pandanaran No. 3", "081234567895", "putri@email.com",
     "Teknik Informatika", "2023", "Cuti"),
    ("202512009", "fiah", "Laki-laki", "2005-02-12", "di Bumi",
     "jl.in aja dulu", "08676767", "well@email.com",
     "kehitaman", "2020", "Aktif"),
]

# ---------- Konstanta data dosen ----------
DOSEN_KOLOM = ["nip", "nama_dosen", "jenis_kelamin", "email", "no_telepon",
               "pendidikan", "bidang_keahlian"]
LABEL_DOSEN = {
    "nip": "NIP", "nama_dosen": "Nama Dosen", "jenis_kelamin": "Jenis Kelamin",
    "email": "Email", "no_telepon": "No Telepon",
    "pendidikan": "Pendidikan Terakhir", "bidang_keahlian": "Bidang Keahlian",
}

DATA_DOSEN = [
    ("D001", "Dr. Hendra Wijaya, M.Kom", "Laki-laki", "hendra@kampus.ac.id",
     "081298765432", "S3", "Kecerdasan Buatan"),
    ("D002", "Prof. Sri Mulyani, M.T", "Perempuan", "sri@kampus.ac.id",
     "081298765433", "S3", "Rekayasa Perangkat Lunak"),
    ("D003", "Ir. Bambang Sutrisno, M.Kom", "Laki-laki", "bambang@kampus.ac.id",
     "081298765434", "S2", "Jaringan Komputer"),
    ("D004", "Dr. Rina Marlina, M.Si", "Perempuan", "rina@kampus.ac.id",
     "081298765435", "S3", "Basis Data"),
    ("D005", "Yusuf Hamdani, M.Kom", "Laki-laki", "yusuf@kampus.ac.id",
     "081298765436", "S2", "Pemrograman Web"),
    ("D006", "fiah", "Laki-laki", "well@kampus.ac.id",
     "089764524424", "S3", "ilmu hitam"),
]


# ======================= DATABASE =======================
def koneksi():
    c = sqlite3.connect(DB_FILE)
    c.row_factory = sqlite3.Row
    return c


def jalankan(sql, params=(), ambil=None):
    """Jalankan query. ambil: None | 'satu' | 'semua'."""
    c = koneksi()
    try:
        cur = c.execute(sql, params)
        hasil = None
        if ambil == "semua":
            hasil = [dict(r) for r in cur.fetchall()]
        elif ambil == "satu":
            r = cur.fetchone()
            hasil = dict(r) if r else None
        c.commit()
        return hasil
    finally:
        c.close()


def siapkan_db():
    """Buat tabel + data awal untuk tabel yang belum ada."""
    c = koneksi()
    try:
        def ada(nama):
            return c.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                             "AND name=?", (nama,)).fetchone()

        if not ada("mahasiswa"):
            c.execute("""CREATE TABLE mahasiswa (
                nim            TEXT PRIMARY KEY,
                nama_lengkap   TEXT NOT NULL,
                jenis_kelamin  TEXT,
                tanggal_lahir  TEXT,
                tempat_lahir   TEXT,
                alamat         TEXT,
                no_telepon     TEXT,
                email          TEXT NOT NULL,
                jurusan        TEXT,
                angkatan       TEXT,
                status         TEXT DEFAULT 'Aktif')""")
            c.executemany("INSERT INTO mahasiswa VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                          DATA_MAHASISWA)
        if not ada("dosen"):
            c.execute("""CREATE TABLE dosen (
                nip              TEXT PRIMARY KEY,
                nama_dosen       TEXT NOT NULL,
                jenis_kelamin    TEXT,
                email            TEXT,
                no_telepon       TEXT,
                pendidikan       TEXT,
                bidang_keahlian  TEXT)""")
            c.executemany("INSERT INTO dosen VALUES (?,?,?,?,?,?,?)", DATA_DOSEN)
        c.commit()
    finally:
        c.close()


def ambil_row(tabel, kunci, nilai):
    return jalankan(f"SELECT * FROM {tabel} WHERE {kunci} = ?", (nilai,), "satu")


def tambah_row(tabel, kolom, d):
    daftar = ", ".join(kolom)
    isi = ", ".join(f":{k}" for k in kolom)
    jalankan(f"INSERT INTO {tabel} ({daftar}) VALUES ({isi})", d)


def ubah_row(tabel, kolom, kunci, kunci_lama, d):
    sets = ", ".join(f"{k} = :{k}" for k in kolom)
    jalankan(f"UPDATE {tabel} SET {sets} WHERE {kunci} = :kunci_lama",
             {**d, "kunci_lama": kunci_lama})


def hapus_row(tabel, kunci, nilai):
    jalankan(f"DELETE FROM {tabel} WHERE {kunci} = ?", (nilai,))


def semua_dosen():
    return jalankan("SELECT * FROM dosen ORDER BY nip", (), "semua")


def cari_mahasiswa(q=""):
    like = f"%{q.lower()}%"
    return jalankan(
        "SELECT * FROM mahasiswa WHERE LOWER(nim || ' ' || nama_lengkap || ' ' || "
        "COALESCE(jurusan,'') || ' ' || COALESCE(status,'')) LIKE ? ORDER BY nim",
        (like,), "semua")


def cek_login_mahasiswa(nim, email):
    return jalankan(
        "SELECT * FROM mahasiswa WHERE nim = ? AND LOWER(email) = LOWER(?)",
        (nim, email), "satu")


# ======================= KOMPONEN UMUM =======================
def header(parent, teks, aksi_logout):
    bar = ttk.Frame(parent)
    bar.pack(fill="x", pady=(0, 6))
    ttk.Label(bar, text=teks, font=("Segoe UI", 11, "bold")).pack(side="left")
    ttk.Button(bar, text="Logout", command=aksi_logout).pack(side="right")
    ttk.Separator(parent).pack(fill="x", pady=(0, 8))


# ======================= HALAMAN LOGIN =======================
class LoginFrame(ttk.Frame):
    def __init__(self, master, aksi_login):
        super().__init__(master, padding=20)
        self.aksi_login = aksi_login

        card = ttk.LabelFrame(self, text="Login", padding=20)
        card.place(relx=0.5, rely=0.42, anchor="center")

        ttk.Label(card, text="SIAKAD",
                  font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2,
                                                      pady=(0, 4))
        ttk.Label(card, text="Masuk dengan NIM dan Email",
                  foreground="gray").grid(row=1, column=0, columnspan=2, pady=(0, 14))

        self.v_user = tk.StringVar()
        self.v_pass = tk.StringVar()

        ttk.Label(card, text="NIM").grid(row=2, column=0, sticky="w", pady=4)
        self.e_user = ttk.Entry(card, textvariable=self.v_user, width=30)
        self.e_user.grid(row=2, column=1, pady=4, padx=(8, 0))

        ttk.Label(card, text="Email").grid(row=3, column=0, sticky="w", pady=4)
        self.e_pass = ttk.Entry(card, textvariable=self.v_pass, width=30, show="*")
        self.e_pass.grid(row=3, column=1, pady=4, padx=(8, 0))

        self.v_lihat = tk.BooleanVar(value=False)
        ttk.Checkbutton(card, text="Tampilkan email", variable=self.v_lihat,
                        command=self.toggle).grid(row=4, column=1, sticky="w",
                                                  padx=(8, 0))

        ttk.Button(card, text="Login", command=self.kirim).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(14, 0))

        self.e_user.focus()
        self.e_user.bind("<Return>", lambda e: self.e_pass.focus())
        self.e_pass.bind("<Return>", lambda e: self.kirim())

    def toggle(self):
        self.e_pass.config(show="" if self.v_lihat.get() else "*")

    def kirim(self):
        self.aksi_login(self.v_user.get().strip(), self.v_pass.get().strip())


# ======================= TAB: DATA DOSEN =======================
class DosenPanel(ttk.Frame):
    def __init__(self, master, boleh_edit=True):
        super().__init__(master, padding=10)
        self.boleh_edit = boleh_edit
        self.nip_terpilih = None
        self.v = {k: tk.StringVar() for k in DOSEN_KOLOM}

        # ---- Form ----
        form = ttk.LabelFrame(self, text="Form Data Dosen", padding=12)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        self.widget = {}
        kiri = ["nip", "jenis_kelamin", "no_telepon", "bidang_keahlian"]
        kanan = ["nama_dosen", "email", "pendidikan"]
        for r, k in enumerate(kiri):
            self._baris(form, r, 0, k)
        for r, k in enumerate(kanan):
            self._baris(form, r, 2, k)

        # ---- Tombol berwarna ----
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=12, padx=4)
        self.btn_tambah = self._tombol(bar, "Tambah", "#4CAF50", self.tambah)
        self.btn_edit = self._tombol(bar, "Edit", "#2196F3", self.edit)
        self.btn_hapus = self._tombol(bar, "Hapus", "#F44336", self.hapus)
        self._tombol(bar, "Clear", "#9E9E9E", self.clear)

        # ---- Tabel ----
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(wrap, orient="vertical")
        self.tree = ttk.Treeview(wrap, columns=DOSEN_KOLOM, show="headings",
                                 yscrollcommand=sb.set)
        sb.config(command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        for k, judul, w in [("nip", "NIP", 80), ("nama_dosen", "Nama Dosen", 210),
                            ("jenis_kelamin", "Jenis Kelamin", 120),
                            ("email", "Email", 190), ("no_telepon", "No Telepon", 130),
                            ("pendidikan", "Pendidikan", 100),
                            ("bidang_keahlian", "Bidang Keahlian", 190)]:
            self.tree.heading(k, text=judul)
            self.tree.column(k, width=w, anchor="w")
        self.tree.bind("<<TreeviewSelect>>", self.pilih)

        if not boleh_edit:
            for w in self.widget.values():
                w.config(state="disabled" if isinstance(w, ttk.Combobox) else "readonly")
            for b in (self.btn_tambah, self.btn_edit, self.btn_hapus):
                b.config(state="disabled", disabledforeground="#EEEEEE")

        self.tampilkan()

    def _baris(self, form, baris, kolom, k):
        ttk.Label(form, text=LABEL_DOSEN[k]).grid(row=baris, column=kolom,
                                                  sticky="w", padx=(8, 12), pady=5)
        if k == "jenis_kelamin":
            w = ttk.Combobox(form, textvariable=self.v[k], values=JENIS_KELAMIN,
                             state="readonly")
        else:
            w = ttk.Entry(form, textvariable=self.v[k])
        w.grid(row=baris, column=kolom + 1, sticky="ew", padx=(0, 18), pady=5)
        self.widget[k] = w

    def _tombol(self, parent, teks, warna, perintah):
        b = tk.Button(parent, text=teks, bg=warna, fg="white",
                      activebackground=warna, activeforeground="white",
                      font=("Segoe UI", 10), width=12, bd=2, relief="raised",
                      cursor="hand2", command=perintah)
        b.pack(side="left", padx=5)
        return b

    # ---- Data ----
    def tampilkan(self):
        self.tree.delete(*self.tree.get_children())
        for d in semua_dosen():
            self.tree.insert("", "end", iid=d["nip"],
                             values=[d[k] or "" for k in DOSEN_KOLOM])

    def pilih(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        d = ambil_row("dosen", "nip", sel[0])
        if not d:
            return
        self.nip_terpilih = d["nip"]
        for k in DOSEN_KOLOM:
            self.v[k].set(d[k] or "")

    def clear(self):
        self.nip_terpilih = None
        for k in DOSEN_KOLOM:
            self.v[k].set("")
        self.tree.selection_remove(self.tree.selection())

    def _ambil_valid(self, nip_lama=None):
        d = {k: self.v[k].get().strip() for k in DOSEN_KOLOM}
        if not d["nip"] or not d["nama_dosen"]:
            messagebox.showwarning("Data belum lengkap", "NIP dan Nama Dosen wajib diisi.")
            return None
        if d["email"] and not re.fullmatch(r"\S+@\S+\.\S+", d["email"]):
            messagebox.showwarning("Email tidak valid", "Format email tidak benar.")
            return None
        if d["no_telepon"] and not re.fullmatch(r"\d{8,15}", d["no_telepon"]):
            messagebox.showwarning("No. telepon tidak valid",
                                   "No. telepon harus 8-15 digit angka.")
            return None
        if d["nip"] != nip_lama and ambil_row("dosen", "nip", d["nip"]):
            messagebox.showwarning("Data ganda", "NIP sudah terdaftar.")
            return None
        return d

    def tambah(self):
        d = self._ambil_valid()
        if not d:
            return
        tambah_row("dosen", DOSEN_KOLOM, d)
        self.clear()
        self.tampilkan()
        messagebox.showinfo("Berhasil", "Data dosen ditambahkan.")

    def edit(self):
        if not self.nip_terpilih:
            messagebox.showinfo("Pilih data", "Klik satu baris di tabel dulu, "
                                              "ubah isinya, lalu klik Edit.")
            return
        d = self._ambil_valid(self.nip_terpilih)
        if not d:
            return
        ubah_row("dosen", DOSEN_KOLOM, "nip", self.nip_terpilih, d)
        self.clear()
        self.tampilkan()
        messagebox.showinfo("Berhasil", "Data dosen diperbarui.")

    def hapus(self):
        if not self.nip_terpilih:
            messagebox.showinfo("Pilih data", "Pilih satu baris dulu.")
            return
        if messagebox.askyesno("Hapus", "Hapus data dosen ini?"):
            hapus_row("dosen", "nip", self.nip_terpilih)
            self.clear()
            self.tampilkan()


# ======================= TAB: PROFIL MAHASISWA =======================
class ProfilPanel(ttk.Frame):
    def __init__(self, master, mhs):
        super().__init__(master, padding=14)
        box = ttk.LabelFrame(self, text="Profil saya", padding=16)
        box.pack(anchor="nw")
        for i, k in enumerate(KOLOM):
            ttk.Label(box, text=LABEL[k].split(" (")[0] + ":").grid(
                row=i, column=0, sticky="nw", pady=4, padx=(0, 16))
            ttk.Label(box, text=mhs.get(k) or "-", font=("Segoe UI", 10, "bold"),
                      wraplength=420, justify="left").grid(row=i, column=1,
                                                           sticky="w", pady=4)


# ======================= TAB: DATA MAHASISWA (admin) =======================
class MahasiswaPanel(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.edit_nim = None

        self.form = ttk.LabelFrame(self, text="Tambah mahasiswa", padding=10)
        self.form.pack(fill="x", pady=(0, 10))

        self.v = {k: tk.StringVar() for k in KOLOM}
        pilihan = {"jenis_kelamin": (JENIS_KELAMIN, "readonly"),
                   "jurusan": (JURUSAN, "normal"),
                   "angkatan": (ANGKATAN, "normal"),
                   "status": (STATUS, "readonly")}

        for i, k in enumerate(KOLOM):
            r, c = divmod(i, 2)
            ttk.Label(self.form, text=LABEL[k]).grid(row=r, column=c * 2, sticky="w",
                                                     padx=(0, 6), pady=4)
            if k in pilihan:
                w = ttk.Combobox(self.form, textvariable=self.v[k],
                                 values=pilihan[k][0], state=pilihan[k][1], width=30)
            else:
                w = ttk.Entry(self.form, textvariable=self.v[k], width=33)
            w.grid(row=r, column=c * 2 + 1, padx=(0, 18), pady=4, sticky="w")

        bar = ttk.Frame(self.form)
        bar.grid(row=6, column=0, columnspan=4, sticky="w", pady=(8, 0))
        self.btn_simpan = ttk.Button(bar, text="Simpan mahasiswa", command=self.simpan)
        self.btn_simpan.pack(side="left")
        self.btn_batal = ttk.Button(bar, text="Batal edit", command=self.reset_form)

        cari = ttk.Frame(self)
        cari.pack(fill="x")
        ttk.Label(cari, text="Cari:").pack(side="left")
        self.v_cari = tk.StringVar()
        self.v_cari.trace_add("write", lambda *a: self.tampilkan())
        ttk.Entry(cari, textvariable=self.v_cari, width=30).pack(side="left", padx=6)
        self.lbl_jumlah = ttk.Label(cari, text="")
        self.lbl_jumlah.pack(side="right")

        kol = ("nim", "nama_lengkap", "jenis_kelamin", "jurusan",
               "angkatan", "status", "email")
        self.tree = ttk.Treeview(self, columns=kol, show="headings", height=8)
        for k, j, w in [("nim", "NIM", 90), ("nama_lengkap", "Nama", 160),
                        ("jenis_kelamin", "Jenis kelamin", 100),
                        ("jurusan", "Jurusan", 160), ("angkatan", "Angkatan", 70),
                        ("status", "Status", 70), ("email", "Email", 180)]:
            self.tree.heading(k, text=j)
            self.tree.column(k, width=w)
        self.tree.pack(fill="both", expand=True, pady=8)
        self.tree.bind("<Double-1>", lambda e: self.edit())

        aksi = ttk.Frame(self)
        aksi.pack(fill="x")
        ttk.Button(aksi, text="Edit terpilih", command=self.edit).pack(side="left")
        ttk.Button(aksi, text="Hapus terpilih", command=self.hapus).pack(side="left", padx=6)

        self.reset_form()
        self.tampilkan()

    def tampilkan(self):
        data = cari_mahasiswa(self.v_cari.get().strip())
        self.tree.delete(*self.tree.get_children())
        for m in data:
            self.tree.insert("", "end", iid=m["nim"], values=(
                m["nim"], m["nama_lengkap"], m["jenis_kelamin"], m["jurusan"],
                m["angkatan"], m["status"], m["email"]))
        self.lbl_jumlah.config(text=f"{len(data)} mahasiswa")

    def reset_form(self):
        self.edit_nim = None
        for k in KOLOM:
            self.v[k].set("")
        self.v["jenis_kelamin"].set(JENIS_KELAMIN[0])
        self.v["jurusan"].set(JURUSAN[0])
        self.v["angkatan"].set(ANGKATAN[0])
        self.v["status"].set("Aktif")
        self.form.config(text="Tambah mahasiswa")
        self.btn_simpan.config(text="Simpan mahasiswa")
        self.btn_batal.pack_forget()

    def simpan(self):
        d = {k: self.v[k].get().strip() for k in KOLOM}

        if not d["nim"] or not d["nama_lengkap"] or not d["email"]:
            messagebox.showwarning("Data belum lengkap", "NIM, nama, dan email wajib diisi.")
            return
        if not re.fullmatch(r"\d{6,15}", d["nim"]):
            messagebox.showwarning("NIM tidak valid", "NIM harus 6-15 digit angka.")
            return
        if not re.fullmatch(r"\S+@\S+\.\S+", d["email"]):
            messagebox.showwarning("Email tidak valid", "Format email tidak benar.")
            return
        if d["tanggal_lahir"]:
            try:
                datetime.strptime(d["tanggal_lahir"], "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Tanggal tidak valid",
                                       "Format tanggal lahir harus YYYY-MM-DD, "
                                       "contoh 2003-05-12.")
                return
        if d["no_telepon"] and not re.fullmatch(r"\d{8,15}", d["no_telepon"]):
            messagebox.showwarning("No. telepon tidak valid",
                                   "No. telepon harus 8-15 digit angka.")
            return
        if d["nim"] != self.edit_nim and ambil_row("mahasiswa", "nim", d["nim"]):
            messagebox.showwarning("Data ganda", "NIM sudah terdaftar.")
            return

        if self.edit_nim:
            ubah_row("mahasiswa", KOLOM, "nim", self.edit_nim, d)
            pesan = "Data mahasiswa diperbarui."
        else:
            tambah_row("mahasiswa", KOLOM, d)
            pesan = "Data mahasiswa disimpan."
        self.reset_form()
        self.tampilkan()
        messagebox.showinfo("Berhasil", pesan)

    def edit(self):
        pilih = self.tree.selection()
        if not pilih:
            messagebox.showinfo("Pilih data", "Pilih satu baris dulu.")
            return
        m = ambil_row("mahasiswa", "nim", pilih[0])
        if not m:
            return
        self.edit_nim = m["nim"]
        for k in KOLOM:
            self.v[k].set(m[k] or "")
        self.form.config(text="Edit mahasiswa")
        self.btn_simpan.config(text="Simpan perubahan")
        self.btn_batal.pack(side="left", padx=6)

    def hapus(self):
        pilih = self.tree.selection()
        if not pilih:
            messagebox.showinfo("Pilih data", "Pilih satu baris dulu.")
            return
        if messagebox.askyesno("Hapus", "Hapus data mahasiswa ini?"):
            hapus_row("mahasiswa", "nim", pilih[0])
            self.tampilkan()


# ======================= HALAMAN UTAMA SETELAH LOGIN =======================
class MainFrame(ttk.Frame):
    def __init__(self, master, teks_user, mhs, aksi_logout):
        """mhs = None untuk admin, dict data mahasiswa untuk login mahasiswa."""
        super().__init__(master, padding=10)
        header(self, teks_user, aksi_logout)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        if mhs is None:   # admin
            nb.add(DosenPanel(nb, boleh_edit=True), text="  Data Dosen  ")
            nb.add(MahasiswaPanel(nb), text="  Data Mahasiswa  ")
        else:
            nb.add(DosenPanel(nb, boleh_edit=MAHASISWA_BOLEH_EDIT), text="  Data Dosen  ")
            nb.add(ProfilPanel(nb, mhs), text="  Profil Saya  ")


# ======================= APLIKASI UTAMA =======================
class Aplikasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1100x740")
        self.minsize(900, 600)
        ttk.Style().configure("Treeview", rowheight=26)
        siapkan_db()
        self.frame = None
        self.tampil_login()

    def ganti(self, frame):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = frame
        self.frame.pack(fill="both", expand=True)

    def tampil_login(self):
        self.title("SIAKAD - Login")
        self.ganti(LoginFrame(self, self.login))

    def masuk(self, teks_user, mhs):
        self.title("Aplikasi Data Dosen - SIAKAD")
        self.ganti(MainFrame(self, teks_user, mhs, self.logout))

    def login(self, username, password):
        if not username or not password:
            messagebox.showwarning("Login", "NIM dan email wajib diisi.")
            return

        if username.lower() == ADMIN_USER and password == ADMIN_PASS:
            self.masuk("Login sebagai: Admin", None)
            return

        mhs = cek_login_mahasiswa(username, password)
        if mhs:
            self.masuk(f"Login sebagai: {mhs['nama_lengkap']} (Mahasiswa)", mhs)
        else:
            messagebox.showerror("Login gagal", "NIM atau email salah.")

    def logout(self):
        if messagebox.askyesno("Logout", "Yakin ingin keluar?"):
            self.tampil_login()


if __name__ == "__main__":
    Aplikasi().mainloop()
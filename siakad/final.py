from datetime import datetime, date, timedelta
from decimal import Decimal
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ======================= PENGATURAN TEMA & WARNA SAAS =======================
BG_MAIN = "#0a0a0c"         # Latar belakang utama (Sangat gelap/deep black)
BG_SIDEBAR = "#121215"      # Warna sidebar kiri
BG_CARD = "#17171c"         # Warna card / panel konten
BG_INPUT = "#202026"        # Warna form input / entry
ACCENT_RED = "#b71c1c"      # Warna merah crimson/maroon ala referensi
ACCENT_HOVER = "#d32f2f"    # Warna hover merah
TEXT_LIGHT = "#ffffff"      # Teks putih
TEXT_MUTED = "#8e8e93"      # Teks abu-abu redup
BORDER_LINE = "#27272f"     # Garis border tipis modern

# ======================= PENGATURAN DATABASE =======================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "siakad",
}

# Diubah ke True agar data KRS dan Pembayaran UKT seluruh mahasiswa tampil dan tidak kosong
KRS_SEMUA = True
PEMBAYARAN_SEMUA = True 

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

# ======================= FUNGSI BANTU =======================
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

def set_field(widget, value):
    widget.delete(0, tk.END)
    widget.insert(0, value)

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
CFG_DOSEN = {
    "judul": "Data Dosen", "tabel": "dosen", "urut": "nip", "pk": "nip", "semua_kolom": True,
    "kolom": [
        ("nip", "NIP", 90),
        ("nama_dosen", "Nama Dosen", 220),
        ("jenis_kelamin", "Jenis Kelamin", 110),
        ("email", "Email", 200),
        ("no_telepon", "No Telepon", 130),
        ("pendidikan", "Pendidikan", 130),
        ("bidang_keahlian", "Bidang Keahlian", 200),
    ],
}

CFG_MAHASISWA = {
    "judul": "Data Mahasiswa", "tabel": "mahasiswa", "urut": "nim", "pk": "nim", "semua_kolom": True,
    "kolom": [
        ("nim", "NIM", 100),
        ("nama_lengkap", "Nama Lengkap", 200),
        ("jenis_kelamin", "Jenis Kelamin", 100),
        ("tanggal_lahir", "Tanggal Lahir", 110),
        ("tempat_lahir", "Tempat Lahir", 110),
        ("alamat", "Alamat", 150),
        ("no_telepon", "No Telepon", 110),
        ("email", "Email", 150),
        ("jurusan", "Jurusan", 150),
        ("angkatan", "Angkatan", 80),
        ("status", "Status", 90),
    ],
}

KOLOM_PROFIL = [
    ("nim", "NIM"), ("nama_lengkap", "Nama Lengkap"), ("jenis_kelamin", "Jenis Kelamin"),
    ("tanggal_lahir", "Tanggal Lahir"), ("tempat_lahir", "Tempat Lahir"),
    ("alamat", "Alamat"), ("no_telepon", "No Telepon"), ("email", "Email"),
    ("jurusan", "Jurusan"), ("angkatan", "Angkatan"), ("status", "Status"),
]

CFG_MATKUL = {
    "judul": "Mata Kuliah", "tabel": "mata_kuliah", "urut": "kode_mk", "pk": "kode_mk",
    "kolom": [
        ("kode_mk", "Kode MK", 100),
        ("nama_mk", "Nama MK", 280),
        ("sks", "SKS", 70),
        ("semester", "Semester", 90),
        ("nip_dosen", "NIP Dosen", 110),
    ],
}

CFG_JADWAL = {
    "judul": "Jadwal Kuliah", "tabel": "jadwal_kuliah", "urut": "id_jadwal", "pk": "id_jadwal",
    "kolom": [
        ("id_jadwal", "ID Jadwal", 80),
        ("kode_mk", "Kode MK", 100),
        ("hari", "Hari", 100),
        ("jam_mulai", "Jam Mulai", 100),
        ("jam_selesai", "Jam Selesai", 100),
        ("ruangan", "Ruangan", 180),
    ],
}

CFG_KRS = {
    "judul": "KRS Mahasiswa", "tabel": "krs", "urut": "id_krs", "pk": "id_krs", "kolom_nim": "nim",
    "kolom": [
        ("id_krs", "ID KRS", 70),
        ("nim", "NIM", 110),
        ("kode_mk", "Kode MK", 100),
        ("semester_ambil", "Sem. Ambil", 100),
        ("tahun_ajaran", "Tahun Ajaran", 120),
        ("nilai_huruf", "Nilai Huruf", 90),
        ("nilai_angka", "Nilai Angka", 90),
    ],
}

CFG_PEMBAYARAN = {
    "judul": "Pembayaran UKT", "tabel": "pembayaran_ukt", "urut": "id_pembayaran", "pk": "id_pembayaran", "kolom_nim": "nim",
    "kolom": [
        ("id_pembayaran", "ID Pembayaran", 110),
        ("nim", "NIM", 100),
        ("semester", "Semester", 80),
        ("tahun_ajaran", "Tahun Ajaran", 110),
        ("jumlah_bayar", "Jumlah Bayar", 120),
        ("tanggal_bayar", "Tanggal Bayar", 110),
        ("metode_pembayaran", "Metode", 130),
        ("status", "Status", 100),
    ],
}

# ======================= PANEL DATA (DENGAN TAMBAH, EDIT, HAPUS) =======================
class DataPanel(tk.Frame):
    def __init__(self, master, cfg, filter_nim=None):
        super().__init__(master, bg=BG_MAIN)
        self.cfg = sesuaikan_cfg(cfg)
        self.filter_nim = filter_nim
        self.kolom = [k[0] for k in self.cfg["kolom"]]
        self.fields = {}
        self.rows = {}
        self.dari_pilihan = False
        self._job = None

        self._bangun_detail()
        self._bangun_bar()
        self._bangun_tabel()
        self.load_data()

    def _bangun_detail(self):
        form = tk.Frame(self, bg=BG_CARD, highlightbackground=BORDER_LINE, highlightthickness=1)
        form.pack(fill="x", padx=24, pady=(20, 12))
        
        tk.Label(form, text=f"Form Detail & Aksi {self.cfg['judul']}", bg=BG_CARD, fg=TEXT_LIGHT, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=18, pady=(14, 10))

        fields_inner = tk.Frame(form, bg=BG_CARD)
        fields_inner.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=18, pady=(0, 10))

        for i, (col, label, _) in enumerate(self.cfg["kolom"]):
            baris, kolom = i // 2, (i % 2) * 2
            tk.Label(fields_inner, text=label, bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 9)).grid(row=baris, column=kolom, sticky="w", padx=(0, 12), pady=6)
            w = tk.Entry(fields_inner, bg=BG_INPUT, fg=TEXT_LIGHT, insertbackground=TEXT_LIGHT, relief="flat", font=("Segoe UI", 10), highlightbackground=BORDER_LINE, highlightcolor=ACCENT_RED, highlightthickness=1)
            w.grid(row=baris, column=kolom + 1, padx=(0, 24), pady=6, sticky="ew", ipady=4)
            w.bind("<KeyRelease>", lambda e, c=col: self.saat_ketik(c))
            self.fields[col] = w
            
        fields_inner.grid_columnconfigure(1, weight=1)
        fields_inner.grid_columnconfigure(3, weight=1)

        tk.Label(form, text="💡 Ketik untuk mencari, klik baris tabel untuk memuat data ke form, lalu gunakan tombol aksi di bawah.",
                 bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 9, "italic")).grid(row=2, column=0, columnspan=4, sticky="w", padx=18, pady=(0, 14))

    def _bangun_bar(self):
        bar = tk.Frame(self, bg=BG_MAIN)
        bar.pack(fill="x", padx=24, pady=6)
        
        tk.Button(bar, text="Tambah Data", bg="#2e7d32", fg=TEXT_LIGHT, activebackground="#388e3c",
                  activeforeground=TEXT_LIGHT, width=12, bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2",
                  relief="flat", command=self.tambah_data).pack(side="left", padx=(0, 8))

        tk.Button(bar, text="Simpan Ubah", bg="#1565c0", fg=TEXT_LIGHT, activebackground="#1976d2",
                  activeforeground=TEXT_LIGHT, width=12, bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2",
                  relief="flat", command=self.ubah_data).pack(side="left", padx=(0, 8))

        tk.Button(bar, text="Hapus Data", bg=ACCENT_RED, fg=TEXT_LIGHT, activebackground=ACCENT_HOVER,
                  activeforeground=TEXT_LIGHT, width=12, bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2",
                  relief="flat", command=self.hapus_data).pack(side="left", padx=(0, 8))

        tk.Button(bar, text="Reset", bg=BG_INPUT, fg=TEXT_LIGHT, activebackground="#2c2c35",
                  activeforeground=TEXT_LIGHT, width=10, bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2",
                  relief="flat", command=self.reset).pack(side="left", padx=(0, 16))
        
        self.lbl_jumlah = tk.Label(bar, text="", bg=BG_MAIN, fg=TEXT_MUTED, font=("Segoe UI", 9))
        self.lbl_jumlah.pack(side="left")

    def _bangun_tabel(self):
        wrap = tk.Frame(self, bg=BG_CARD, highlightbackground=BORDER_LINE, highlightthickness=1)
        wrap.pack(fill="both", expand=True, padx=24, pady=(8, 24))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("SaaS.Treeview", background=BG_CARD, foreground=TEXT_LIGHT, fieldbackground=BG_CARD, borderwidth=0, rowheight=30, font=("Segoe UI", 9))
        style.configure("SaaS.Treeview.Heading", background="#1e1e24", foreground=TEXT_LIGHT, font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("SaaS.Treeview", background=[('selected', ACCENT_RED)], foreground=[('selected', TEXT_LIGHT)])

        self.tree = ttk.Treeview(wrap, columns=self.kolom, show="headings", style="SaaS.Treeview")
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
            self.tree.column(col, width=lebar, minwidth=60)
            
        self.tree.bind("<<TreeviewSelect>>", self.select_item)

    def saat_ketik(self, col):
        if self.dari_pilihan:
            for c, w in self.fields.items():
                if c != col:
                    w.delete(0, tk.END)
            self.dari_pilihan = False
        if self._job is not None:
            self.after_cancel(self._job)
        self._job = self.after(250, self.load_data)

    def select_item(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        for col, val in zip(self.kolom, self.rows[sel[0]]):
            set_field(self.fields[col], val)
        self.dari_pilihan = True

    def reset(self):
        for w in self.fields.values():
            w.delete(0, tk.END)
        self.dari_pilihan = False
        self.load_data()

    def tambah_data(self):
        data_input = {col: self.fields[col].get().strip() for col in self.kolom}
        pk = self.cfg["pk"]
        if not data_input.get(pk):
            messagebox.showwarning("Peringatan", f"Kolom Primary Key ({pk}) wajib diisi untuk menambah data!")
            return

        cols = [c for c, v in data_input.items() if v != ""]
        vals = [v for c, v in data_input.items() if v != ""]
        if not cols:
            messagebox.showwarning("Peringatan", "Form data masih kosong!")
            return

        sql = f"INSERT INTO {self.cfg['tabel']} ({', '.join(cols)}) VALUES ({', '.join(['%s']*len(vals))})"
        db = None
        try:
            db = connect_db()
            cur = db.cursor()
            cur.execute(sql, vals)
            db.commit()
            messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
            self.reset()
        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal menambah data:\n{e}")
        finally:
            if db and db.is_connected():
                db.close()

    def ubah_data(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih baris pada tabel yang ingin diubah datanya!")
            return
        
        pk = self.cfg["pk"]
        pk_val = self.fields[pk].get().strip()
        if not pk_val:
            messagebox.showwarning("Peringatan", f"Nilai {pk} tidak boleh kosong!")
            return

        data_input = {col: self.fields[col].get().strip() for col in self.kolom if col != pk and self.fields[col].get().strip() != ""}
        if not data_input:
            messagebox.showwarning("Peringatan", "Tidak ada perubahan data yang diisi!")
            return

        set_clauses = [f"{col} = %s" for col in data_input.keys()]
        vals = list(data_input.values()) + [pk_val]

        sql = f"UPDATE {self.cfg['tabel']} SET {', '.join(set_clauses)} WHERE {pk} = %s"
        db = None
        try:
            db = connect_db()
            cur = db.cursor()
            cur.execute(sql, vals)
            db.commit()
            messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
            self.reset()
        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal mengubah data:\n{e}")
        finally:
            if db and db.is_connected():
                db.close()

    def hapus_data(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih baris pada tabel yang ingin dihapus!")
            return

        pk = self.cfg["pk"]
        pk_val = self.fields[pk].get().strip()
        if not pk_val:
            messagebox.showwarning("Peringatan", "Data yang dipilih tidak valid!")
            return

        if not messagebox.askyesno("Konfirmasi Hapus", f"Yakin ingin menghapus data dengan {pk} = {pk_val}?"):
            return

        sql = f"DELETE FROM {self.cfg['tabel']} WHERE {pk} = %s"
        db = None
        try:
            db = connect_db()
            cur = db.cursor()
            cur.execute(sql, (pk_val,))
            db.commit()
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
            self.reset()
        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal menghapus data:\n{e}")
        finally:
            if db and db.is_connected():
                db.close()

    def _isi_tabel(self, rows):
        self.tree.delete(*self.tree.get_children())
        self.rows.clear()
        for i, row in enumerate(rows):
            nilai = [tampil(v) for v in row]
            iid = str(i)
            self.rows[iid] = nilai
            self.tree.insert("", "end", iid=iid, values=nilai)
        self.lbl_jumlah.config(text=f"Total Ditemukan: {len(self.rows)} data")

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
            messagebox.showerror("Database Error", f"Gagal mengambil data {self.cfg['judul']}: {e}")
        finally:
            if db is not None and db.is_connected():
                db.close()

# ======================= TAB: PROFIL SAYA =======================
class ProfilPanel(tk.Frame):
    def __init__(self, master, nim):
        super().__init__(master, bg=BG_MAIN)
        
        box = tk.Frame(self, bg=BG_CARD, highlightbackground=BORDER_LINE, highlightthickness=1)
        box.pack(anchor="nw", padx=24, pady=24, fill="both", expand=True)

        tk.Label(box, text="Profil Mahasiswa", bg=BG_CARD, fg=TEXT_LIGHT, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=24, pady=(24, 16))

        content_inner = tk.Frame(box, bg=BG_CARD)
        content_inner.pack(anchor="w", padx=24, pady=10, fill="both", expand=True)

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
            tk.Label(content_inner, text=f"{label}", bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold"), anchor="w").grid(
                row=i, column=0, sticky="nw", pady=8, padx=(0, 40))
            tk.Label(content_inner, text=tampil(data.get(col)) or "-", bg=BG_CARD, fg=TEXT_LIGHT, font=("Segoe UI", 10),
                     wraplength=600, justify="left", anchor="w").grid(
                row=i, column=1, sticky="w", pady=8)

# ======================= HALAMAN LOGIN (FULLSCREEN & MODERN) =======================
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
        super().__init__(master, bg=BG_MAIN)
        self.aksi_login = aksi_login

        card = tk.Frame(self, bg=BG_CARD, highlightbackground=BORDER_LINE, highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=720, height=440)

        left_frame = tk.Frame(card, bg=BG_CARD)
        left_frame.pack(side="left", fill="both", expand=True, padx=45, pady=45)

        tk.Label(left_frame, text="Login", font=("Segoe UI", 22, "bold"), bg=BG_CARD, fg=TEXT_LIGHT).pack(anchor="w", pady=(0, 6))
        if pesan:
            tk.Label(left_frame, text=pesan, fg="#4cd137", bg=BG_CARD, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))

        tk.Label(left_frame, text="Username (NIM)", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(10, 2))
        self.entry_user = tk.Entry(left_frame, font=("Segoe UI", 11), bg=BG_INPUT, fg=TEXT_LIGHT, insertbackground=TEXT_LIGHT, relief="flat", highlightbackground=BORDER_LINE, highlightcolor=ACCENT_RED, highlightthickness=1)
        self.entry_user.pack(anchor="w", fill="x", ipady=6, pady=(0, 12))

        tk.Label(left_frame, text="Password (Email)", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(2, 2))
        self.entry_pass = tk.Entry(left_frame, font=("Segoe UI", 11), show="*", bg=BG_INPUT, fg=TEXT_LIGHT, insertbackground=TEXT_LIGHT, relief="flat", highlightbackground=BORDER_LINE, highlightcolor=ACCENT_RED, highlightthickness=1)
        self.entry_pass.pack(anchor="w", fill="x", ipady=6, pady=(0, 8))

        self.v_lihat = tk.BooleanVar(value=False)
        tk.Checkbutton(left_frame, text="Tampilkan password", variable=self.v_lihat,
                       command=self.toggle, bg=BG_CARD, fg=TEXT_MUTED, selectcolor=BG_INPUT, activebackground=BG_CARD, activeforeground=TEXT_LIGHT, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 15))

        tk.Button(left_frame, text="Login ke SIAKAD", bg=ACCENT_RED, fg=TEXT_LIGHT, font=("Segoe UI", 10, "bold"),
                  activebackground=ACCENT_HOVER, activeforeground=TEXT_LIGHT, bd=0,
                  cursor="hand2", command=self.kirim, height=2, relief="flat").pack(fill="x")

        right_frame = tk.Frame(card, bg="#0e0e12", width=240, highlightbackground=BORDER_LINE, highlightthickness=1)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="SIAKAD", font=("Segoe UI", 24, "bold"), bg="#0e0e12", fg=TEXT_LIGHT).pack(expand=True)

        self.entry_user.focus()
        self.entry_user.bind("<Return>", lambda e: self.entry_pass.focus())
        self.entry_pass.bind("<Return>", lambda e: self.kirim())

    def toggle(self):
        self.entry_pass.config(show="" if self.v_lihat.get() else "*")

    def kirim(self):
        self.aksi_login(self.entry_user.get().strip(), self.entry_pass.get().strip(), self)

# ======================= HALAMAN UTAMA (SAAS DASHBOARD LAYOUT) =======================
class MainFrame(tk.Frame):
    def __init__(self, master, user, aksi_logout):
        super().__init__(master, bg=BG_MAIN)
        self.user = user
        self.aksi_logout = aksi_logout

        topbar = tk.Frame(self, bg=BG_SIDEBAR, height=64, highlightbackground=BORDER_LINE, highlightthickness=1)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="SIAKAD", font=("Segoe UI", 15, "bold"), bg=BG_SIDEBAR, fg=TEXT_LIGHT).pack(side="left", padx=(24, 16))
        tk.Label(topbar, text=f"Welcome back, {user['nama']}  •  NIM: {user['id']}",
                 font=("Segoe UI", 10), bg=BG_SIDEBAR, fg=TEXT_MUTED).pack(side="left", padx=10)
        
        btn_logout = tk.Button(topbar, text="Logout", bg=BG_INPUT, fg=TEXT_LIGHT, activebackground=ACCENT_RED,
                               activeforeground=TEXT_LIGHT, font=("Segoe UI", 9, "bold"), width=10, bd=0,
                               cursor="hand2", command=self.aksi_logout, relief="flat")
        btn_logout.pack(side="right", padx=24)

        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(body, bg=BG_SIDEBAR, width=250, highlightbackground=BORDER_LINE, highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content_area = tk.Frame(body, bg=BG_MAIN)
        self.content_area.pack(side="right", fill="both", expand=True)

        milik_krs = None if KRS_SEMUA else user["id"]
        milik_bayar = None if PEMBAYARAN_SEMUA else user["id"]

        self.menus = [
            ("Profil Saya", lambda: ProfilPanel(self.content_area, user["id"])),
            ("Data Dosen", lambda: DataPanel(self.content_area, CFG_DOSEN)),
            ("Data Mahasiswa", lambda: DataPanel(self.content_area, CFG_MAHASISWA)),
            ("Mata Kuliah", lambda: DataPanel(self.content_area, CFG_MATKUL)),
            ("Jadwal Kuliah", lambda: DataPanel(self.content_area, CFG_JADWAL)),
            ("KRS", lambda: DataPanel(self.content_area, CFG_KRS, filter_nim=milik_krs)),
            ("Pembayaran UKT", lambda: DataPanel(self.content_area, CFG_PEMBAYARAN, filter_nim=milik_bayar)),
        ]

        self.btn_refs = {}

        tk.Label(self.sidebar, text="MENU NAVIGASI", font=("Segoe UI", 8, "bold"), bg=BG_SIDEBAR, fg=TEXT_MUTED).pack(anchor="w", padx=20, pady=(24, 10))

        for nama, fungsi_panel in self.menus:
            btn = tk.Button(self.sidebar, text=nama, font=("Segoe UI", 10), bg=BG_SIDEBAR, fg=TEXT_MUTED,
                            activebackground=ACCENT_RED, activeforeground=TEXT_LIGHT, anchor="w",
                            bd=0, padx=18, pady=10, cursor="hand2", relief="flat",
                            command=lambda n=nama, f=fungsi_panel: self.pilih_menu(n, f))
            btn.pack(fill="x", padx=12, pady=3)
            self.btn_refs[nama] = btn

        self.pilih_menu("Profil Saya", lambda: ProfilPanel(self.content_area, user["id"]))

    def pilih_menu(self, nama_menu, fungsi_panel):
        for nama, btn in self.btn_refs.items():
            if nama == nama_menu:
                btn.config(bg=ACCENT_RED, fg=TEXT_LIGHT)
            else:
                btn.config(bg=BG_SIDEBAR, fg=TEXT_MUTED)

        for widget in self.content_area.winfo_children():
            widget.destroy()

        panel_baru = fungsi_panel()
        panel_baru.pack(fill="both", expand=True)

# ======================= APLIKASI UTAMA =======================
class Aplikasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg=BG_MAIN)
        self.frame = None
        self.tampil_login()

    def ganti(self, frame):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = frame
        self.frame.pack(fill="both", expand=True)

    def tampil_login(self, pesan=""):
        self.title("Login - SIAKAD")
        self.state('zoomed')
        self.ganti(LoginFrame(self, self.proses_login, pesan))

    def tampil_utama(self, user):
        self.title("SIAKAD Mahasiswa - Sistem Informasi Akademik")
        self.state('zoomed')
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
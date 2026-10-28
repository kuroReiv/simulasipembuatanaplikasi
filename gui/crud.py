# Mengimpor modul os untuk interaksi sistem operasi jika diperlukan
import os
# Mengimpor modul tkinter dasar untuk pembuatan komponen GUI
import tkinter as tk
# Mengimpor modul ttk untuk widget bertema (seperti Combobox & Treeview) dan messagebox untuk dialog pop-up
from tkinter import ttk, messagebox
# Mengimpor mysql.connector untuk mengendalikan koneksi dan operasi database MySQL
import mysql.connector

# --- KONEKSI DATABASE ---
# Fungsi untuk membuat dan mengembalikan objek koneksi ke database MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",      # Alamat host server MySQL
        user="root",           # Username untuk login ke MySQL
        password="",           # Password pengguna (kosongkan jika tidak ada password)
        database="siakad"      # Nama database yang dituju
    )

# --- FUNGSI CRUD ---
# Fungsi untuk memuat dan menampilkan seluruh data dari tabel database ke Treeview
def load_data():
    # Menghapus seluruh baris data lama yang ada di Treeview sebelum memuat data baru
    for row in tree.get_children():
        tree.delete(row)
    try:
        # Membuka koneksi ke database
        db = connect_db()
        # Membuat objek kursor untuk mengeksekusi query SQL
        cursor = db.cursor()
        # Mengeksekusi query untuk mengambil semua record dari tabel dosen
        cursor.execute("SELECT * FROM dosen")
        # Mengambil seluruh baris hasil query SQL
        rows = cursor.fetchall()
        # Memasukkan setiap baris data hasil query ke dalam komponen Treeview (tabel GUI)
        for row in rows:
            tree.insert("", "end", values=row)
        # Menutup koneksi database
        db.close()
    except Exception as e:
        # Menampilkan pop-up error jika terjadi kegagalan pengambilan data dari database
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")

# Fungsi untuk menambahkan record dosen baru ke database
def tambah_data():
    # Mengambil nilai teks dari masing-masing field form input
    nip = entry_nip.get()
    nama = entry_nama.get()
    jk = combo_jk.get()
    email = entry_email.get()
    tlp = entry_tlp.get()
    pendidikan = entry_pendidikan.get()
    bidang = entry_bidang.get()

    # Validasi input wajib (NIP dan Nama Dosen tidak boleh kosong)
    if not nip or not nama:
        messagebox.showwarning("Warning", "NIP dan Nama Dosen wajib diisi!")
        return

    try:
        # Membuka koneksi database
        db = connect_db()
        cursor = db.cursor()
        # Query SQL INSERT dengan placeholder (%s) untuk mencegah SQL Injection
        sql = "INSERT INTO dosen (nip, nama_dosen, jenis_kelamin, email, no_telepon, pendidikan_terakhir, bidang_keahlian) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        # Tuple berisi kumpulan nilai variabel input
        val = (nip, nama, jk, email, tlp, pendidikan, bidang)
        # Mengeksekusi query INSERT beserta nilainya
        cursor.execute(sql, val)
        # Menyimpan perubahan transaksi ke database secara permanen
        db.commit()
        # Menutup koneksi database
        db.close()
        # Menampilkan notifikasi sukses
        messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
        # Mengosongkan form input
        clear_fields()
        # Memperbarui tampilan data pada tabel Treeview
        load_data()
    except Exception as e:
        # Menampilkan pesan error jika query INSERT gagal dieksekusi
        messagebox.showerror("Error", f"Gagal menambah data: {e}")

# Fungsi untuk memperbarui (update) data dosen yang dipilih
def edit_data():
    # Memeriksa baris mana yang sedang dipilih di Treeview
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin diubah!")
        return

    # Mengambil nilai terbaru dari masing-masing field form input
    nip = entry_nip.get()
    nama = entry_nama.get()
    jk = combo_jk.get()
    email = entry_email.get()
    tlp = entry_tlp.get()
    pendidikan = entry_pendidikan.get()
    bidang = entry_bidang.get()

    try:
        # Membuka koneksi database
        db = connect_db()
        cursor = db.cursor()
        # Query SQL UPDATE untuk mengubah data berdasarkan klausa WHERE nip
        sql = """UPDATE dosen SET nama_dosen=%s, jenis_kelamin=%s, email=%s, 
                 no_telepon=%s, pendidikan_terakhir=%s, bidang_keahlian=%s WHERE nip=%s"""
        # Tuple nilai parameter query
        val = (nama, jk, email, tlp, pendidikan, bidang, nip)
        # Mengeksekusi query UPDATE
        cursor.execute(sql, val)
        # Menyimpan perubahan transaksi secara permanen
        db.commit()
        # Menutup koneksi database
        db.close()
        # Menampilkan notifikasi sukses
        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
        # Mengosongkan form input dan merefresh tabel
        clear_fields()
        load_data()
    except Exception as e:
        # Menampilkan pop-up error jika terjadi kendala saat mengedit data
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

# Fungsi untuk menghapus record dosen dari database
def hapus_data():
    # Memeriksa apakah ada item tabel yang dipilih
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin dihapus!")
        return

    # Mengambil NIP dari input field sebagai acuan penghapusan
    nip = entry_nip.get()
    # Menampilkan dialog konfirmasi Ya/Tidak sebelum menghapus
    confirm = messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus dosen NIP {nip}?")
    if confirm:
        try:
            # Membuka koneksi database
            db = connect_db()
            cursor = db.cursor()
            # Mengeksekusi query DELETE berdasarkan NIP
            cursor.execute("DELETE FROM dosen WHERE nip = %s", (nip,))
            # Simpan perubahan secara permanen
            db.commit()
            # Menutup koneksi
            db.close()
            # Notifikasi sukses
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
            # Bersihkan form dan refresh tabel Treeview
            clear_fields()
            load_data()
        except Exception as e:
            # Notifikasi kegagalan hapus data
            messagebox.showerror("Error", f"Gagal menghapus data: {e}")

# Fungsi callback event saat salah satu baris pada tabel Treeview diklik/dipilih
def select_item(event):
    # Mendapatkan ID item baris yang dipilih
    selected = tree.selection()
    if selected:
        # Mengambil daftar nilai kolom dari baris yang dipilih
        values = tree.item(selected[0], "values")
        # Mengosongkan isian form sebelum diisi data baru
        clear_fields()
        # Memasukkan data kolom tabel ke masing-masing elemen input form
        entry_nip.insert(0, values[0])
        entry_nama.insert(0, values[1])
        combo_jk.set(values[2])
        entry_email.insert(0, values[3])
        entry_tlp.insert(0, values[4])
        entry_pendidikan.insert(0, values[5])
        entry_bidang.insert(0, values[6])

# Fungsi helper untuk menghapus/mengosongkan seluruh kotak input form
def clear_fields():
    entry_nip.delete(0, tk.END)
    entry_nama.delete(0, tk.END)
    combo_jk.set("")
    entry_email.delete(0, tk.END)
    entry_tlp.delete(0, tk.END)
    entry_pendidikan.delete(0, tk.END)
    entry_bidang.delete(0, tk.END)

# --- GUI MAIN WINDOW ---
# Membuat objek jendela utama Tkinter
root = tk.Tk()
# Mengatur judul jendela aplikasi
root.title("Aplikasi Data Dosen - SIAKAD")
# Mengatur dimensi ukuran jendela awal (lebar 900px, tinggi 550px)
root.geometry("900x550")

# Membuat frame bergaris tepi (LabelFrame) untuk mengelompokkan form input data
frame_form = tk.LabelFrame(root, text=" Form Data Dosen ", padx=10, pady=10)
# Menampilkan frame form di bagian atas jendela yang memenuhi lebar secara horizontal
frame_form.pack(fill="x", padx=15, pady=10)

# Daftar teks label untuk setiap field data
labels = ["NIP", "Nama Dosen", "Jenis Kelamin", "Email", "No Telepon", "Pendidikan Terakhir", "Bidang Keahlian"]
# Perulangan untuk membuat label teks secara dinamis menggunakan layout Grid 2 kolom
for i, label_text in enumerate(labels):
    tk.Label(frame_form, text=label_text).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=3)

# Membuat elemen Entry untuk input NIP
entry_nip = tk.Entry(frame_form)
entry_nip.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

# Membuat elemen Entry untuk input Nama Dosen
entry_nama = tk.Entry(frame_form)
entry_nama.grid(row=0, column=3, padx=5, pady=3, sticky="ew")

# Membuat elemen Combobox untuk opsi pilihan Jenis Kelamin
combo_jk = ttk.Combobox(frame_form, values=["Laki-laki", "Perempuan"], state="readonly")
combo_jk.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

# Membuat elemen Entry untuk input Email
entry_email = tk.Entry(frame_form)
entry_email.grid(row=1, column=3, padx=5, pady=3, sticky="ew")

# Membuat elemen Entry untuk input Nomor Telepon
entry_tlp = tk.Entry(frame_form)
entry_tlp.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

# Membuat elemen Entry untuk input Pendidikan Terakhir
entry_pendidikan = tk.Entry(frame_form)
entry_pendidikan.grid(row=2, column=3, padx=5, pady=3, sticky="ew")

# Membuat elemen Entry untuk input Bidang Keahlian
entry_bidang = tk.Entry(frame_form)
entry_bidang.grid(row=3, column=1, padx=5, pady=3, sticky="ew")

# Konfigurasi tata letak grid agar kolom input bersifat responsif menyesuaikan lebar frame
frame_form.grid_columnconfigure(1, weight=1)
frame_form.grid_columnconfigure(3, weight=1)

# Membuat frame penampung tombol-tombol aksi CRUD
frame_btn = tk.Frame(root)
frame_btn.pack(fill="x", padx=15, pady=5)

# Membuat dan menampilkan tombol Tambah, Edit, Hapus, dan Clear secara berdampingan
tk.Button(frame_btn, text="Tambah", bg="#4CAF50", fg="white", command=tambah_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Edit", bg="#2196F3", fg="white", command=edit_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Hapus", bg="#f44336", fg="white", command=hapus_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Clear", bg="#9E9E9E", fg="white", command=clear_fields, width=12).pack(side="left", padx=5)

# Membuat frame penampung komponen tabel (Treeview)
frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=15, pady=10)

# Definisi nama identifier untuk setiap kolom tabel
columns = ("nip", "nama_dosen", "jenis_kelamin", "email", "no_telepon", "pendidikan_terakhir", "bidang_keahlian")
# Membuat komponen Treeview untuk menampilkan struktur data tabular
tree = ttk.Treeview(frame_table, columns=columns, show="headings")

# Mengatur judul header yang tampil pada setiap kolom tabel
tree.heading("nip", text="NIP")
tree.heading("nama_dosen", text="Nama Dosen")
tree.heading("jenis_kelamin", text="Laki-laki/Perempuan")
tree.heading("email", text="Email")
tree.heading("no_telepon", text="No Telepon")
tree.heading("pendidikan_terakhir", text="Pendidikan")
tree.heading("bidang_keahlian", text="Bidang Keahlian")

# Mengatur lebar relatif dari masing-masing kolom tabel
tree.column("nip", width=70)
tree.column("nama_dosen", width=160)
tree.column("jenis_kelamin", width=100)
tree.column("email", width=140)
tree.column("no_telepon", width=100)
tree.column("pendidikan_terakhir", width=80)
tree.column("bidang_keahlian", width=150)

# Mengikat event klik/pilih item pada Treeview dengan fungsi handler select_item
tree.bind("<<TreeviewSelect>>", select_item)

# Membuat scrollbar vertikal dan menghubungkannya dengan komponen Treeview
scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# Menampilkan Treeview dan Scrollbar ke dalam frame tabel
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Memanggil fungsi load_data() untuk menampilkan data awal saat aplikasi pertama kali dijalankan
load_data()

# Memulai loop utama peristiwa GUI Tkinter
root.mainloop()
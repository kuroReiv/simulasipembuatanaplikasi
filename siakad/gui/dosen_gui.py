# Mengimpor modul mysql.connector untuk mengendalikan koneksi ke database MySQL
import mysql.connector
# Mengimpor modul dasar tkinter untuk pembuatan komponen GUI
import tkinter as tk
# Mengimpor ttk (themed tkinter) dan messagebox untuk dialog peringatan/notifikasi
from tkinter import ttk, messagebox


# Deklarasi kelas utama untuk mengelola antarmuka (GUI) jendela login
class LoginWindow:
    # Konstruktor kelas yang dipanggil pertama kali saat objek dikreasikan
    def __init__(self, root):
        # Menyimpan reference jendela utama (root window) Tkinter ke atribut kelas
        self.root = root
        # Mengatur judul yang ditampilkan pada title bar jendela aplikasi
        self.root.title("Login - SIAKAD")
        # Menentukan dimensi resolusi jendela (lebar 380px dan tinggi 250px)
        self.root.geometry("380x250")
        # Mengunci ukuran jendela agar tidak bisa diubah ukurannya (disable resize)
        self.root.resizable(False, False)
        # Mengatur warna latar belakang seluruh jendela menjadi abu-abu terang (#f0f0f0)
        self.root.configure(bg="#f0f0f0")

        # konfigurasi koneksi database MySQL
        self.db_config = {
            'host': 'localhost',      # Alamat database
            'user': 'root',           # Nama pengguna akun MySQL
            'password': '',           # Kata sandi akses MySQL (kosong secara default)
            'database': 'siakad'      # Nama database yang digunakan
        }

        # Membuat container/frame utama untuk menampung seluruh elemen visual
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        # Menempatkan frame utama dengan padding horizontal (padx) & vertikal (pady) sebesar 20px
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Membuat elemen teks/label judul utama form login
        lbl_title = tk.Label(
            main_frame, 
            text="SIAKAD LOGIN",      # Teks judul yang ditampilkan
            font=("Arial", 14, "bold"),# Jenis huruf Arial, ukuran 14, dicetak tebal
            bg="#f0f0f0",             # Warna latar disesuaikan dengan warna induknya
            fg="black"                # Warna teks judul hitam
        )
        # Posisikan label judul di bagian atas frame utama dengan margin bawah 20px
        lbl_title.pack(pady=(0, 20))

        # Membuat sub-frame khusus untuk menyusun label dan input teks menggunakan tata letak Grid
        form_frame = tk.Frame(main_frame, bg="#f0f0f0")
        # Menampilkan sub-frame form di dalam main_frame
        form_frame.pack()

        # Baris 0: Label petunjuk input Username (NIP)
        lbl_user = tk.Label(form_frame, text="Username:", font=("Arial", 10), bg="#f0f0f0", anchor="e", width=10)
        # Menempatkan label di baris 0 kolom 0, dengan posisi rata kanan (sticky="e")
        lbl_user.grid(row=0, column=0, padx=5, pady=6, sticky="e")
        # Membuat kotak isian teks (entry) untuk memasukkan NIP
        self.entry_nip = tk.Entry(form_frame, font=("Arial", 10), width=22, relief=tk.SOLID, bd=1)
        # Menempatkan kotak input NIP di baris 0 kolom 1
        self.entry_nip.grid(row=0, column=1, padx=5, pady=6)
        # Mengatur kursor agar otomatis aktif pada kotak input NIP saat program dibuka
        self.entry_nip.focus()

        # Baris 1: Label petunjuk input Password (Email)
        lbl_pass = tk.Label(form_frame, text="Password:", font=("Arial", 10), bg="#f0f0f0", anchor="e", width=10)
        # Menempatkan label password di baris 1 kolom 0
        lbl_pass.grid(row=1, column=0, padx=5, pady=6, sticky="e")
        # Membuat kotak isian teks untuk email/password dengan karakter khusus (show="*")
        self.entry_email = tk.Entry(form_frame, font=("Arial", 10), width=22, show="*", relief=tk.SOLID, bd=1)
        # Menempatkan kotak input password di baris 1 kolom 1
        self.entry_email.grid(row=1, column=1, padx=5, pady=6)

        # Membuat tombol (button) untuk eksekusi tindakan login
        btn_login = tk.Button(
            main_frame, 
            text="Login",             # Teks pada tombol
            font=("Arial", 10, "bold"),# Gaya penulisan teks tombol
            bg="#4CAF50",             # Warna latar belakang tombol (hijau)
            fg="white",               # Warna teks tombol (putih)
            activebackground="#45a049",# Warna tombol saat diklik
            activeforeground="white", # Warna teks saat diklik
            width=15,                 # Lebar ukuran tombol
            bd=1,                     # Ketebalan garis tepi tombol
            cursor="hand2",           # Mengubah ikon kursor mouse menjadi bentuk tangan
            command=self.proses_login # Menghubungkan klik tombol dengan metode proses_login()
        )
        # Posisikan tombol login di bawah blok form input dengan jarak atas 20px
        btn_login.pack(pady=(20, 0))

        # Mengikat (binding) tombol 'Enter' pada keyboard untuk menjalankan fungsi proses_login()
        self.root.bind('<Return>', lambda event: self.proses_login())

    # Metode untuk menangani alur verifikasi data login pengampu
    def proses_login(self):
        # Mengambil input dari entry_nip dan menghapus spasi ekstra di awal/akhir
        nip = self.entry_nip.get().strip()
        # Mengambil input dari entry_email dan menghapus spasi ekstra di awal/akhir
        email = self.entry_email.get().strip()

        # Memeriksa apakah ada salah satu atau kedua field yang kosong
        if not nip or not email:
            # Menampilkan pesan peringatan dalam bentuk messagebox pop-up
            messagebox.showwarning("Peringatan", "Username (NIP) dan Password (Email) wajib diisi!")
            # Menghentikan eksekusi fungsi jika data belum lengkap
            return

        # Inisialisasi variabel objek koneksi dengan nilai awal None
        conn = None
        # Inisialisasi variabel objek cursor dengan nilai awal None
        cursor = None

        try:
            # Mengatur ikatan koneksi ke database menggunakan kredensial yang tersimpan
            conn = mysql.connector.connect(**self.db_config)
            # Membuat objek kursor dengan output format dictionary (dictionary=True)
            cursor = conn.cursor(dictionary=True)

            # Query SQL dengan parameterize placeholder (%s) untuk mencegah serangan SQL Injection
            query = "SELECT nip, nama_dosen, email FROM dosen WHERE nip = %s AND email = %s"
            # Mengeksekusi perintah query SQL dengan menyisipkan nilai nip dan email
            cursor.execute(query, (nip, email))
            # Mengambil satu baris data hasil pencarian dari database
            user = cursor.fetchone()

            # Mengecek apakah data dosen ditemukan di dalam database
            if user:
                # Menampilkan pesan pop-up sukses login disertai nama dosen
                messagebox.showinfo("Berhasil", f"Login berhasil!\nSelamat datang, {user['nama_dosen']}.")
                # Memanggil metode pembuka dashboard utama
                self.buka_dashboard(user)
            else:
                # Menampilkan pesan pop-up kegagalan autentikasi
                messagebox.showerror("Gagal", "Login gagal! Username atau Password salah.")

        # Menangkap galat/error yang berkaitan dengan kegagalan koneksi atau query MySQL
        except mysql.connector.Error as err:
            # Menampilkan rincian kesalahan sistem database ke pengguna
            messagebox.showerror("Database Error", f"Koneksi database bermasalah:\n{err}")
        # Blok yang pasti akan dieksekusi setelah try/except selesai dijalankan
        finally:
            # Menutup kursor jika kursor aktif/terbuka
            if cursor:
                cursor.close()
            # Menutup koneksi database jika status koneksi sedang terhubung
            if conn and conn.is_connected():
                conn.close()

    # Metode pembersih jendela login setelah autentikasi berhasil
    def buka_dashboard(self, user):
        # Memusnahkan/menutup seluruh komponen jendela login saat ini
        self.root.destroy()


# Titik awal eksekusi program Python (Main Entry Point)
if __name__ == "__main__":
    # Menginisialisasi objek aplikasi utama Tkinter
    root = tk.Tk()
    # Membuat objek/instance kelas LoginWindow
    app = LoginWindow(root)
    # Jalankan loop acara (event loop) utama agar GUI tetap terbuka dan responsif
    root.mainloop()
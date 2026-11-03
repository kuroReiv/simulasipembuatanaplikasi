# Mengimpor modul tkinter untuk membuat antarmuka grafis (GUI)
import tkinter as tk
# Mengimpor modul os untuk mengelola alur path/direktori file sistem
import os

# Memunculkan jendela utama aplikasi Tkinter
root = tk.Tk()
# Mengatur teks pada judul jendela aplikasi
root.title("Konverter Suhu")
# Menentukan ukuran resolusi jendela aplikasi (lebar 300px, tinggi 180px)
root.geometry("300x180")

# Mengambil lokasi path folder dari file skrip Python ini berada
base_dir = os.path.dirname(__file__)
# Menggabungkan direktori utama dengan nama file ikon 'calc.ico'
icon_path = os.path.join(base_dir, "calc.ico")

# Mengecek apakah file ikon 'calc.ico' tersedia sebelum dimuat ke title bar
if os.path.exists(icon_path):
    # Mengganti ikon default Tkinter pada title bar menggunakan file .ico
    root.iconbitmap(icon_path)

# --- FUNGSI LOGIKA KONVERSI SUHU ---
def konversi():
    try:
        # Mengambil nilai masukan dari Entry dan mengubah tipe datanya menjadi desimal (float)
        celsius = float(entry_celsius.get())
        # Menghitung konversi suhu dari Celsius ke Fahrenheit (ditambahkan operator perkalian '*')
        fahrenheit = (celsius * 9/5) + 32
        # Memperbarui teks hasil konversi pada label dengan warna hijau
        label_hasil.config(text=f"Hasil: {fahrenheit:.1f} °F", fg="green")
    except ValueError:
        # Menampilkan pesan error jika teks yang dimasukkan user bukan angka
        label_hasil.config(text="Masukkan angka yang valid!", fg="red")

# Membuat dan menampilkan label petunjuk "Suhu (Celsius):"
tk.Label(root, text="Suhu (Celsius):", font=('Arial', 11)).pack(pady=(15, 5))

# Membuat kotak input teks untuk nilai Celsius dengan teks berada di tengah (justify="center")
entry_celsius = tk.Entry(root, font=('Arial', 12), justify="center")
# Menampilkan kotak input di jendela
entry_celsius.pack(pady=5)

# Membuat tombol untuk mengeksekusi fungsi konversi() saat diklik
btn_hitung = tk.Button(root, text="Konversi ke Fahrenheit", command=konversi, font=('Arial', 10, 'bold'))
# Menampilkan tombol konversi
btn_hitung.pack(pady=10)

# Membuat label untuk menampilkan teks status atau hasil perhitungan
label_hasil = tk.Label(root, text="Hasil: -", font=('Arial', 11, 'bold'))
# Menampilkan label hasil
label_hasil.pack(pady=5)

# Memulai event loop utama agar GUI tetap berjalan dan dapat berinteraksi
root.mainloop()

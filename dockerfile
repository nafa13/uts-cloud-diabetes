# 1. Menggunakan sistem operasi dasar Python versi ringan (slim)
FROM python:3.9-slim

# 2. Menentukan folder kerja di dalam wadah Docker
WORKDIR /app

# 3. Menyalin file daftar library ke dalam Docker
COPY requirements.txt .

# 4. Menginstal semua library yang dibutuhkan aplikasi
RUN pip install --no-cache-dir -r requirements.txt

# 5. Menyalin seluruh kodingan aplikasi Akang ke dalam Docker
COPY . .

# 6. Membuka pintu jaringan (port) nomor 5000 
EXPOSE 5000

# 7. Perintah yang otomatis dijalankan saat Docker dinyalakan
CMD ["python", "app.py"]
# Deskripsi
Aplikasi sentiment analysis secara real-time berbasis modifikasi metode VADER untuk Bahasa Indonesia. Dibuat untuk memenuhi penugasan mata kuliah TIF21-51-31 Pemrosesan Bahasa Alami.

# Anggota Kelompok
| Nama | NIM |
| :----------------: | :--------------: |
| Ahmad Zidan | 19/439806/TK/48536 |
| Krisna Mughni Jiwandaru | 19/444057/TK/49253 |


# Pemakaian
*Install* semua *package* dan *depedencies*-nya
> pip install -U -r requirements.txt

## *Streaming* data Twitter

Masukan **BEARER_KEY** dari Twitter API ke dalam file stream.py
> BEARER_TOKEN = "BEARER_KEY"

Jalankan *script* stream.py untuk mulai *streaming* data dari Twitter
> python stream.py

## Pemrosesan data secara *(near) real-time* menggunakan Spark

Jalankan *service* yang dibutuhkan
> docker compose up

Jalankan *script* spark_sentiment.py untuk memulai Spark
> python spark_sentiment.py

# 🖥️ PC Hardware Diagnostic Studio — Sistem Pakar Forward Chaining

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Built--in-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-CDN-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Method](https://img.shields.io/badge/Inference-Forward_Chaining-06B6D4?style=for-the-badge)

**PC Hardware Diagnostic Studio** adalah aplikasi sistem pakar berbasis web untuk mendiagnosis indikasi kerusakan komponen hardware pada **PC Desktop (komputer rakitan)** menggunakan metode penalaran maju (**Forward Chaining**). Sistem ini dirancang untuk membantu teknisi komputer, asisten laboratorium (aslab), dan pengguna dengan pengetahuan dasar hardware dalam melakukan identifikasi awal kerusakan secara cepat, terstruktur, dan transparan.

---

## ✨ Fitur Utama

* **🗺️ Skematik Topologi Hardware Interaktif (SVG):** Visualisasi blok komponen internal PC Desktop dan periferal utama (`K01`–`K08`). Pengguna dapat mengklik blok komponen pada diagram untuk memfilter gejala terkait, serta memantau indikator sorotan merah (*fault pulse*) secara otomatis pada komponen yang terdeteksi bermasalah.
* **🎯 Filter Berbasis Kondisi Awal (*State-Based Filtering*):** Membagi alur konsultasi berdasarkan 4 kondisi awal perangkat (`Tidak Menyala`, `Menyala tapi Blank`, `Masuk BIOS`, `Masuk Windows`) sehingga hanya kategori gejala yang relevan yang ditampilkan.
* **⚡ Mesin Inferensi Forward Chaining Murni:** Mengevaluasi seluruh basis aturan secara penuh (*full iteration*) berdasarkan fakta awal yang dipilih pengguna tanpa berhenti pada aturan pertama yang cocok.
* **🛡️ Deteksi Kontradiksi Real-Time (*UX Guard*):** Memberikan peringatan otomatis ketika pengguna memilih kombinasi kondisi awal dan gejala yang saling bertentangan secara logis (misalnya kondisi awal PC menyala namun mencentang gejala mati daya total).
* **🚀 Simulasi Cepat (*Quick Presets*):** Menyediakan tombol uji coba instan untuk mendemonstrasikan kasus tunggal maupun multi-kerusakan secara langsung.
* **📋 Laporan Analisis & Solusi 3 Tahap:** Menampilkan alur penalaran (*Working Memory* $\rightarrow$ *Rule Fired* $\rightarrow$ *Kesimpulan*), analisis gangguan, kemungkinan penyebab, pemeriksaan awal, penanganan mandiri, tindakan teknisi ahli, serta fitur salin laporan ke *clipboard*.
* **🗄️ Zero-Config SQLite Database:** Database relasional (`sistem_pakar.db`) dibuat dan diisi otomatis saat server pertama kali dijalankan tanpa memerlukan konfigurasi XAMPP atau phpMyAdmin.

---

## ⚙️ Cara Kerja Mesin Inferensi

Sistem menerapkan pendekatan **Forward Chaining** (*data-driven reasoning*) dengan prinsip *open-world assumption*:

1. **Penentuan Kondisi Awal (`S1`):** Pengguna memilih satu kondisi awal PC yang bersifat *mutually exclusive* (radio button).
2. **Pengumpulan Fakta Awal (*Working Memory*):** Pengguna mencentang minimal **2 gejala** yang teramati. Gejala yang tidak dicentang tidak dianggap sebagai fakta negatif ("komponen pasti normal").
3. **Pencocokan Aturan (*Rule Matching*):** Backend memeriksa seluruh **29 aturan valid** dari database. Sebuah aturan aktif (*fired*) apabila seluruh premis `IF` pada aturan tersebut merupakan himpunan bagian (*subset*) dari fakta awal pengguna.
4. **Akumulasi Kesimpulan:** Sistem mengumpulkan seluruh kesimpulan kerusakan (`THEN`) dari aturan-aturan yang terpenuhi dan menampilkannya secara setara tanpa menebak-nebak apabila tidak ada aturan yang cocok.

---

## 🧠 Basis Pengetahuan (*Knowledge Base*)

Seluruh data gejala, kerusakan, dan aturan disusun secara deterministik berdasarkan sintesis **7 jurnal referensi** dan difokuskan pada komponen utama **PC Desktop**.

### 1. Daftar Kerusakan / Komponen (`K01`–`K08`)

| Kode          | Nama Kerusakan              | Komponen Terkait         | Section Utama               |
| :------------ | :-------------------------- | :----------------------- | :-------------------------- |
| **K01** | Motherboard Rusak           | Motherboard              | `S3` (Booting & BIOS)     |
| **K02** | Processor (CPU) Rusak       | Processor / Cooler       | `S5` (Kinerja & Sistem)   |
| **K03** | RAM (Memori) Rusak          | RAM / Memori             | `S3` (Booting & BIOS)     |
| **K04** | Power Supply (PSU) Rusak    | Power Supply Unit        | `S2` (Daya & Fisik)       |
| **K05** | VGA Card (GPU) Rusak        | Kartu Grafis (GPU)       | `S4` (Tampilan & Grafis)  |
| **K06** | Harddisk / SSD Rusak        | Media Penyimpanan        | `S6` (Penyimpanan & Data) |
| **K07** | Monitor Rusak               | Monitor / Display        | `S4` (Tampilan & Grafis)  |
| **K08** | Sistem Operasi (OS) Corrupt | OS Windows *(Overlap)* | `S7` (Sistem Operasi)     |

> **Catatan:** `K08` (Sistem Operasi) disertakan karena gejala kerusakan OS sering tumpang tindih dengan indikasi kerusakan komponen hardware seperti RAM dan Harddisk/SSD.

### 2. Struktur Section & Gejala (`G01`–`G44`)

Terdapat **44 gejala terverifikasi** yang dikelompokkan ke dalam 6 section gejala setelah pemilihan kondisi awal (`S1`):

* **`S1` — Kondisi Awal Perangkat:** `off` (Tidak Menyala), `blank` (Menyala tapi Blank), `bios` (Masuk BIOS), `windows` (Masuk Windows).
* **`S2` — Gejala Daya & Fisik (7 Gejala):** `G01`, `G02`, `G03`, `G04`, `G05`, `G06`, `G25`.
* **`S3` — Gejala Booting & BIOS (6 Gejala):** `G08`, `G09`, `G10`, `G12`, `G13`, `G38`.
* **`S4` — Gejala Tampilan & Grafis (12 Gejala):** `G07`, `G14`, `G15`, `G16`, `G17`, `G18`, `G19`, `G20`, `G21`, `G34`, `G35`, `G36`.
* **`S5` — Gejala Kinerja & Sistem (7 Gejala):** `G22`, `G23`, `G24`, `G26`, `G27`, `G28`, `G37`.
* **`S6` — Gejala Penyimpanan & Data (7 Gejala):** `G29`, `G30`, `G31`, `G32`, `G33`, `G39`, `G44`.
* **`S7` — Gejala Sistem Operasi (5 Gejala):** `G11`, `G40`, `G41`, `G42`, `G43`.

### 3. Basis Aturan (*Rule Base*)

* **Total Aturan Aktif:** **29 Aturan Valid** (`R01`–`R07`, `R10`–`R20`, `R23`–`R33`), terdiri dari 24 aturan kombinasi `AND` dan 5 aturan kondisi tunggal (`R25`, `R27`, `R29`, `R32`, `R33`) yang dimitigasi dengan syarat input minimal 2 gejala.
* **Aturan Dikecualikan:** `R08` dan `R09` tidak digunakan karena tidak memiliki dukungan kombinasi eksplisit di jurnal sumber, sedangkan `R21` ditahan menunggu validasi teknisi ahli.

---

## 📁 Struktur Direktori

```text
KB-Sistem-pakar-kerusakan-pc-desktop-dan-hardware/
├── app.py                  # Server Flask, REST API, & Mesin Inferensi Forward Chaining
├── requirements.txt        # Daftar dependensi Python (flask, flask-cors)
├── .gitignore              # Konfigurasi file cache & database lokal yang diabaikan Git
├── README.md               # Dokumentasi sistem
├── sistem_pakar.db         # Database SQLite (otomatis dibuat saat app.py dijalankan)
└── templates/
    └── index.html          # Antarmuka Web & Skematik Topologi Hardware SVG
```

---

## 🔌 Dokumentasi API Backend

| Method   | Endpoint             | Deskripsi                                                                                                                                                         |
| :------- | :------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET`  | `/`                | Merender halaman utama antarmuka pengguna (`templates/index.html`).                                                                                             |
| `GET`  | `/api/master-data` | Mengambil data master kondisi awal (`S1`), kategori section (`S2`–`S7`), dan 44 daftar gejala dari SQLite.                                                 |
| `POST` | `/api/diagnose`    | Menerima payload JSON `{"symptoms": ["G08", "G37"]}`, menjalankan pencocokan aturan Forward Chaining, dan mengembalikan hasil diagnosis beserta solusi lengkap. |

---

## 🚀 Cara Menjalankan Aplikasi

### Prasyarat

* **Python 3.10** atau versi lebih baru.
* Koneksi internet untuk memuat CDN Tailwind CSS dan Google Fonts (*Plus Jakarta Sans* & *JetBrains Mono*).

### Langkah Instalasi

1. **Clone repositori ini:**

   ```bash
   git clone [https://github.com/H45T4CK/KB-Sistem-pakar-kerusakan-pc-desktop-dan-hardware.git](https://github.com/H45T4CK/KB-Sistem-pakar-kerusakan-pc-desktop-dan-hardware.git)
   cd KB-Sistem-pakar-kerusakan-pc-desktop-dan-hardware
   ```
2. **Instal dependensi Python:**

   ```bash
   pip install -r requirements.txt
   ```
3. **Jalankan server Flask:**

   ```bash
   python app.py
   ```

   > Saat pertama kali dijalankan, `app.py` akan otomatis membuat file **`sistem_pakar.db`** dan mengisi seluruh tabel master gejala, kerusakan, serta aturan.
   >
4. **Buka aplikasi di browser:**
   Kunjungi **`http://127.0.0.1:5000`** melalui browser.

---

## 📚 Referensi Jurnal

Basis pengetahuan pada sistem ini disusun berdasarkan 7 publikasi ilmiah berikut:

1. **J1:** Alfareza, M., Kurniawansyah, K., & Akbar, Z. (2024). *Sistem Pakar Kerusakan Hardware Komputer dengan Metode Forward Chaining pada Eleven Komputer*.
2. **J2:** Putri, S. R., & Firmansyah, M. D. (2024). *Sistem Pakar Diagnosa Kerusakan pada Harddisk Menggunakan Metode Forward Chaining Berbasis Web*.
3. **J3:** Murdoko, A., Suprapto, B., Rahmatullah, S., & Sulasminarti. (2026). *Sistem Pakar Diagnosis Kerusakan Hardware Komputer Menggunakan Metode Forward Chaining*.
4. **J4:** Akbar, M., & Sari, Y. P. (2024). *Implementasi Sistem Pakar Diagnosa Kerusakan Hardware dan Software Laptop dengan Metode Forward Chaining Berbasis Website*.
5. **J5:** Budianto, A., & Pramusinto, W. *Implementasi Sistem Pakar dengan Metode Forward Chaining untuk Menganalisa Kerusakan Komputer pada Media Indonesia*.
6. **J6:** Pratama, H. S., Efendy, M. P., Roby, M., & Tusakdivah, S. H. (2022). *Sistem Pakar Deteksi Kerusakan Laptop atau Komputer Menggunakan Metode Forward Chaining*.
7. **J7:** Permadi, D., Handayani, D., Kustanto, P., Yasir, M., Noeman, A., & Hidayat, A. (2025). *Perancangan Sistem Pakar Diagnosis Kerusakan Laptop Berbasis Website Menggunakan Algoritma Forward Chaining*.

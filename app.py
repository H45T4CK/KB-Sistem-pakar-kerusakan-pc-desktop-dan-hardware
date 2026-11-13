import os
import json
import sqlite3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = "sistem_pakar.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Otomatis membuat tabel dan mengisi data dari Dokumen Final jika database belum ada."""
    if os.path.exists(DB_PATH):
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE kondisi_awal (
        kode_kondisi TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        deskripsi TEXT
    );

    CREATE TABLE section_gejala (
        kode_section TEXT PRIMARY KEY,
        nama_section TEXT NOT NULL,
        kondisi_tampil TEXT NOT NULL
    );

    CREATE TABLE kerusakan (
        kode_kerusakan TEXT PRIMARY KEY,
        nama_kerusakan TEXT NOT NULL,
        komponen_terkait TEXT NOT NULL,
        penjelasan TEXT,
        penyebab TEXT,
        pemeriksaan_awal TEXT,
        rekomendasi_penanganan TEXT,
        tindakan_teknisi TEXT
    );

    CREATE TABLE gejala (
        kode_gejala TEXT PRIMARY KEY,
        nama_gejala TEXT NOT NULL,
        deskripsi TEXT,
        kode_section TEXT,
        FOREIGN KEY (kode_section) REFERENCES section_gejala(kode_section)
    );

    CREATE TABLE aturan (
        kode_rule TEXT PRIMARY KEY,
        kode_kerusakan TEXT NOT NULL,
        operator_logika TEXT DEFAULT 'AND',
        catatan TEXT,
        status TEXT DEFAULT 'Valid',
        FOREIGN KEY (kode_kerusakan) REFERENCES kerusakan(kode_kerusakan)
    );

    CREATE TABLE aturan_detail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_rule TEXT NOT NULL,
        kode_gejala TEXT NOT NULL,
        FOREIGN KEY (kode_rule) REFERENCES aturan(kode_rule),
        FOREIGN KEY (kode_gejala) REFERENCES gejala(kode_gejala)
    );
    """)

    # 1. Seed Kondisi Awal (S1)
    states_data = [
        ('off', 'PC Tidak Menyala Sama Sekali', 'Tidak ada tanda daya atau kipas tidak bergerak.'),
        ('blank', 'PC Menyala, Tetapi Layar Blank', 'Kipas/lampu menyala, tetapi tidak ada tampilan.'),
        ('bios', 'PC Dapat Masuk BIOS', 'Tampilan BIOS muncul, tetapi Windows belum tentu bisa dibuka.'),
        ('windows', 'PC Dapat Masuk Windows', 'Windows terbuka, tetapi ada gangguan saat digunakan.')
    ]
    cursor.executemany("INSERT INTO kondisi_awal VALUES (?, ?, ?)", states_data)

    # 2. Seed Section Gejala (S2 - S7)
    sections_data = [
        ('S2', 'Gejala Daya & Fisik', '["off", "blank"]'),
        ('S3', 'Gejala Booting & BIOS', '["blank", "bios", "windows"]'),
        ('S4', 'Gejala Tampilan & Grafis', '["blank", "bios", "windows"]'),
        ('S5', 'Gejala Kinerja & Sistem', '["bios", "windows"]'),
        ('S6', 'Gejala Penyimpanan & Data', '["bios", "windows"]'),
        ('S7', 'Gejala Sistem Operasi', '["windows"]')
    ]
    cursor.executemany("INSERT INTO section_gejala VALUES (?, ?, ?)", sections_data)

    # 3. Seed Kerusakan (K01 - K08)
    kerusakan_data = [
        ('K01', 'Motherboard Rusak', 'Motherboard', 'Papan sirkuit utama mengalami gangguan, sistem tidak bisa berkomunikasi dengan baik.', 'Kapasitor mengembung, korsleting akibat debu/cairan, tegangan tidak stabil.', 'Periksa visual komponen gosong/mengembung; cabut dan pasang ulang RAM/VGA.', 'Bersihkan dan pasang ulang komponen. Jika ada kapasitor mengembung, motherboard perlu diganti.', 'Penggantian kapasitor atau reballing membutuhkan solder uap. Bawa ke teknisi.'),
        ('K02', 'Processor (CPU) Rusak', 'Processor', 'Otak komputer gagal memproses instruksi, biasanya akibat panas berlebih atau kerusakan fisik.', 'Pasta thermal kering, kipas mati/berdebu, pin bengkok.', 'Cek kipas processor berputar; periksa suhu di BIOS.', 'Bersihkan kipas dan heatsink dari debu. Ganti pasta thermal jika kering.', 'Penggantian processor memerlukan keahlian khusus karena rawan pin bengkok.'),
        ('K03', 'RAM (Memori) Rusak', 'RAM', 'Memori jangka pendek gagal membaca/menyimpan data sementara.', 'Pin kuningan kotor, RAM kendor, kerusakan chip.', 'Lepas RAM, gosok pin dengan penghapus karet, pasang kembali.', 'Coba ganti posisi slot atau uji satu keping secara bergantian.', 'Jika tetap tidak terbaca setelah dibersihkan dan dipindah slot, ganti modul RAM.'),
        ('K04', 'Power Supply (PSU) Rusak', 'PSU', 'Komponen penyedia daya gagal mengalirkan tegangan cukup.', 'Komponen terbakar, kipas macet, korsleting.', 'Cek kabel daya tercolok kencang; cium aroma terbakar.', 'Jangan membongkar PSU sendiri (berbahaya). Ganti dengan PSU baru yang berkualitas.', 'Penggantian PSU harus disesuaikan dengan kebutuhan watt seluruh komponen.'),
        ('K05', 'VGA Card (GPU) Rusak', 'VGA Card', 'Kartu grafis gagal memproses gambar, tampilan rusak atau tidak muncul.', 'Panas berlebih, kipas berdebu, VGA kendor, chip grafis aus.', 'Pastikan kabel monitor terpasang kencang; lepas VGA, bersihkan pin, pasang kembali.', 'Bersihkan kipas VGA secara rutin. Jika muncul garis/artefak, periksa memori/chip VGA.', 'Perbaikan chip VGA (reballing) harus dilakukan teknisi berpengalaman.'),
        ('K06', 'Harddisk / SSD Rusak', 'Harddisk/SSD', 'Media penyimpanan mengalami bad sector atau kerusakan mekanik.', 'Harddisk terjatuh, usia pakai lama, mati listrik mendadak, kabel SATA longgar.', 'Periksa kabel SATA; dengarkan suara klik; segera backup data penting.', 'Jika bad sector ringan, coba format ulang/chkdsk setelah backup.', 'Jika tidak terdeteksi di BIOS atau berbunyi mekanik kasar, ganti ke SSD baru.'),
        ('K07', 'Monitor Rusak', 'Monitor', 'Panel layar atau komponen internal monitor gagal menampilkan gambar normal.', 'Kabel data rusak, inverter rusak, dead pixel, panel retak.', 'Colok monitor ke perangkat lain; ganti kabel monitor; cek pengaturan resolusi.', 'Atur kecerahan di menu monitor. Jika ada garis permanen, kemungkinan kerusakan panel.', 'Penggantian panel LCD/LED atau inverter sebaiknya diserahkan ke teknisi servis monitor.'),
        ('K08', 'Sistem Operasi (OS) Corrupt', 'OS', 'File sistem Windows rusak atau hilang, tidak bisa masuk desktop.', 'Virus/malware, update gagal, mati mendadak saat booting.', 'Coba masuk Safe Mode (F8); jalankan System Restore atau Startup Repair.', 'Pindai virus dengan antivirus bootable atau siapkan flashdisk instalasi untuk repair.', 'Instalasi ulang bersih (clean install) beserta backup data.')
    ]
    cursor.executemany("INSERT INTO kerusakan VALUES (?, ?, ?, ?, ?, ?, ?, ?)", kerusakan_data)

    # 4. Seed Gejala (G01 - G44)
    gejala_data = [
        ('G01', 'PC Tidak Menyala Sama Sekali', 'Menekan tombol power tidak menghasilkan reaksi apa pun.', 'S2'),
        ('G02', 'PC Hidup Sebentar Lalu Mati', 'Komputer menyala beberapa detik, lalu mati sendiri.', 'S2'),
        ('G03', 'Lampu Indikator Tidak Menyala', 'Lampu daya pada casing tidak menyala saat dicolokkan.', 'S2'),
        ('G04', 'Bau Terbakar atau Asap', 'Tercium aroma gosong atau keluar asap dari dalam casing.', 'S2'),
        ('G05', 'Suara Mendesis pada PSU', 'Terdengar suara desis dari dalam power supply.', 'S2'),
        ('G06', 'Kipas (Fan) Tidak Berputar', 'Kipas pendingin pada PSU, processor, atau casing tidak berputar.', 'S2'),
        ('G25', 'Kipas Processor Berisik/Mati', 'Kipas pendingin di atas processor mengeluarkan suara kasar atau mati.', 'S2'),
        ('G08', 'Bunyi Beep Panjang Berulang', 'Terdengar bunyi "tit" panjang terus-menerus saat komputer dinyalakan.', 'S3'),
        ('G09', 'Bunyi Beep Pendek Berkali-kali', 'Terdengar bunyi beep pendek (1x, 3x, atau lebih) saat proses booting.', 'S3'),
        ('G10', 'Stuck di Logo BIOS', 'Komputer berhenti/terjebak pada tampilan logo BIOS saat awal menyalakan.', 'S3'),
        ('G12', 'Korosi pada Motherboard', 'Terdapat karat atau kerak pada komponen papan sirkuit utama.', 'S3'),
        ('G13', 'Pengaturan BIOS Sering Reset', 'Waktu dan tanggal di BIOS sering kembali ke pengaturan awal (CMOS lemah).', 'S3'),
        ('G38', 'Sering Masuk BIOS Sendiri', 'Komputer tiba-tiba masuk ke menu BIOS saat dinyalakan.', 'S3'),
        ('G07', 'PC Hidup Tapi Layar Blank/Hitam', 'Komputer menyala (kipas berputar) tetapi tidak ada tampilan di monitor.', 'S4'),
        ('G14', 'Monitor Sering Berkedip', 'Tampilan layar sering mati-hidup atau berkedip saat digunakan.', 'S4'),
        ('G15', 'Gambar Layar Redup/Gelap', 'Tampilan pada monitor terlihat sangat gelap atau redup.', 'S4'),
        ('G16', 'Muncul Garis pada Layar', 'Terdapat garis vertikal atau horizontal yang mengganggu tampilan.', 'S4'),
        ('G17', 'Warna Layar Tidak Normal', 'Warna pada tampilan monitor berubah-ubah atau tidak sesuai aslinya.', 'S4'),
        ('G18', 'Ukuran Tampilan Tidak Sesuai', 'Resolusi layar berubah, logo atau aplikasi terlihat terlalu besar/kecil.', 'S4'),
        ('G19', 'Dead Pixel / Blank Putih', 'Terdapat titik-titik mati atau area putih pada layar monitor.', 'S4'),
        ('G20', 'Layar Hanya Tampil Sebagian', 'Gambar yang muncul hanya sebagian (tergores atau terpotong).', 'S4'),
        ('G21', 'Artefak Grafis / Gambar Rusak', 'Muncul gambar berantakan, garis tidak beraturan, atau glitch saat main game.', 'S4'),
        ('G34', 'FPS Game Turun Drastis', 'Performa grafis menurun tajam saat bermain game atau rendering.', 'S4'),
        ('G35', 'VGA Tidak Terdeteksi OS', 'Kartu grafis tidak terbaca oleh Windows (cek di Device Manager).', 'S4'),
        ('G36', 'Kipas VGA Berisik', 'Kipas pada kartu grafis mengeluarkan suara berisik.', 'S4'),
        ('G22', 'Kinerja Komputer Lambat', 'Komputer terasa sangat lemot saat menjalankan aplikasi.', 'S5'),
        ('G23', 'Komputer Sering Hang/Freeze', 'Komputer sering macet dan tidak merespon perintah.', 'S5'),
        ('G24', 'Komputer Restart Sendiri', 'Komputer tiba-tiba mati dan menyala kembali tanpa perintah.', 'S5'),
        ('G26', 'Overheating (Panas Berlebih)', 'Suhu komputer sangat panas, sering menyebabkan mati mendadak.', 'S5'),
        ('G27', 'Aplikasi Sering Crash', 'Program yang berjalan tiba-tiba tertutup sendiri (Not Responding).', 'S5'),
        ('G28', 'Gagal Menyimpan Data', 'Komputer tidak bisa menyimpan file atau proses save gagal.', 'S5'),
        ('G37', 'Layar Biru (BSOD)', 'Muncul layar biru berisi kode error (Blue Screen of Death).', 'S5'),
        ('G29', "Harddisk Berbunyi 'Tek'", 'Terdengar suara mekanik/klik dari dalam harddisk.', 'S6'),
        ('G30', 'Harddisk Sulit Diformat', 'Proses format drive tidak bisa diselesaikan.', 'S6'),
        ('G31', 'Tidak Bisa Copy/Reading File', 'Gagal menyalin atau membuka file dari harddisk.', 'S6'),
        ('G32', 'Lampu Indikator Harddisk Mati', 'Lampu aktivitas harddisk menyala terus tanpa berkedip.', 'S6'),
        ('G33', 'Masuk Windows Sangat Lama', 'Proses loading saat masuk sistem operasi memakan waktu lama.', 'S6'),
        ('G39', 'Pesan "No Bootable Device"', 'Muncul pesan error "OS not found" atau "Disk boot failure" saat booting.', 'S6'),
        ('G44', 'File Tiba-tiba Hilang/Korup', 'Data hilang secara misterius atau file menjadi rusak tidak bisa dibuka.', 'S6'),
        ('G11', 'Port/Slot Tidak Berfungsi', 'Colokan USB, audio, atau slot komponen tidak bisa mendeteksi perangkat.', 'S7'),
        ('G40', 'Gagal Instalasi OS', 'Proses instalasi ulang Windows selalu gagal atau error di tengah jalan.', 'S7'),
        ('G41', 'Windows Corrupt / Tidak Bisa Masuk', 'Sistem operasi rusak, tidak bisa masuk ke desktop meski hardware nyala.', 'S7'),
        ('G42', 'Serangan Virus/Malware', 'Komputer terinfeksi virus yang tidak bisa dibersihkan oleh antivirus.', 'S7'),
        ('G43', 'Update Windows Gagal', 'Proses pembaruan sistem Windows selalu mengalami error.', 'S7')
    ]
    cursor.executemany("INSERT INTO gejala VALUES (?, ?, ?, ?)", gejala_data)

    # 5. Seed Aturan (29 Rule Valid sesuai Dokumen Final Bagian 6.1)
    rules_map = {
        'R01': ('K01', ['G07', 'G08', 'G10', 'G11', 'G12']),
        'R02': ('K01', ['G13', 'G24', 'G23', 'G38', 'G37']),
        'R03': ('K01', ['G23', 'G27', 'G22', 'G10', 'G11']),
        'R04': ('K02', ['G07', 'G23', 'G06', 'G26', 'G10', 'G22']),
        'R05': ('K02', ['G23', 'G09', 'G27', 'G22', 'G07']),
        'R06': ('K02', ['G02', 'G24', 'G01', 'G10']),
        'R07': ('K03', ['G07', 'G37', 'G08', 'G27', 'G28']),
        'R10': ('K04', ['G24', 'G04', 'G05', 'G06', 'G03']),
        'R11': ('K04', ['G04', 'G05']),
        'R12': ('K04', ['G01', 'G04', 'G10']),
        'R13': ('K05', ['G21', 'G34', 'G35', 'G36', 'G16']),
        'R14': ('K05', ['G21', 'G34']),
        'R15': ('K05', ['G21', 'G07', 'G17', 'G19']),
        'R16': ('K06', ['G33', 'G29', 'G38', 'G30', 'G31', 'G32']),
        'R17': ('K06', ['G23', 'G37', 'G22', 'G29', 'G44']),
        'R18': ('K06', ['G37', 'G39', 'G40', 'G44']),
        'R19': ('K07', ['G15', 'G16', 'G14', 'G18', 'G17']),
        'R20': ('K07', ['G15', 'G16', 'G20']),
        'R23': ('K08', ['G22', 'G40', 'G42', 'G43', 'G41']),
        'R24': ('K01', ['G08', 'G10']),
        'R25': ('K01', ['G10']),
        'R26': ('K02', ['G23', 'G06']),
        'R27': ('K02', ['G23']),
        'R28': ('K03', ['G37', 'G08']),
        'R29': ('K03', ['G08']),
        'R30': ('K06', ['G33', 'G29']),
        'R31': ('K06', ['G29', 'G38']),
        'R32': ('K06', ['G33']),
        'R33': ('K06', ['G29'])
    }

    for rule_id, (dmg_id, sym_list) in rules_map.items():
        op = 'Tunggal' if len(sym_list) == 1 else 'AND'
        cursor.execute(
            "INSERT INTO aturan (kode_rule, kode_kerusakan, operator_logika, status) VALUES (?, ?, ?, 'Valid')",
            (rule_id, dmg_id, op)
        )
        for sym_id in sym_list:
            cursor.execute(
                "INSERT INTO aturan_detail (kode_rule, kode_gejala) VALUES (?, ?)",
                (rule_id, sym_id)
            )

    conn.commit()
    conn.close()
    print("✅ Database SQLite (sistem_pakar.db) berhasil dibuat dan diisi otomatis!")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/master-data", methods=["GET"])
def get_master_data():
    conn = get_db_connection()
    states = [dict(row) for row in conn.execute("SELECT * FROM kondisi_awal").fetchall()]
    sections = [dict(row) for row in conn.execute("SELECT * FROM section_gejala").fetchall()]
    symptoms = [dict(row) for row in conn.execute("SELECT * FROM gejala ORDER BY kode_gejala ASC").fetchall()]
    conn.close()

    groups = []
    for sec in sections:
        sec_symptoms = [s for s in symptoms if s["kode_section"] == sec["kode_section"]]
        groups.append({
            "id": sec["kode_section"],
            "title": sec["nama_section"],
            "states": json.loads(sec["kondisi_tampil"]),
            "items": sec_symptoms
        })

    return jsonify({"states": states, "groups": groups})

@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    data = request.get_json()
    selected_symptoms = set(data.get("symptoms", []))

    if len(selected_symptoms) < 2:
        return jsonify({
            "status": "warning",
            "message": "Pilih minimal 2 gejala yang teramati agar sistem dapat melakukan analisis akurat."
        }), 400

    contradiction_note = None
    if "G01" in selected_symptoms and "G07" in selected_symptoms:
        contradiction_note = "Peringatan: Gejala G01 (Tidak Menyala) dan G07 (Menyala Tapi Blank) secara logis bertentangan. Periksa kembali pilihan Anda."

    conn = get_db_connection()
    query = """
        SELECT a.kode_rule, a.kode_kerusakan, a.catatan,
               GROUP_CONCAT(ad.kode_gejala) AS daftar_gejala
        FROM aturan a
        JOIN aturan_detail ad ON a.kode_rule = ad.kode_rule
        WHERE a.status = 'Valid'
        GROUP BY a.kode_rule
    """
    rules = [dict(row) for row in conn.execute(query).fetchall()]

    matched_rules = []
    for rule in rules:
        required_symptoms = set(rule["daftar_gejala"].split(","))
        if required_symptoms.issubset(selected_symptoms):
            matched_rules.append({
                "kode_rule": rule["kode_rule"],
                "kode_kerusakan": rule["kode_kerusakan"],
                "catatan": rule["catatan"]
            })

    if not matched_rules:
        conn.close()
        return jsonify({
            "status": "not_found",
            "message": "Maaf, kombinasi gejala yang Anda pilih belum dapat diidentifikasi berdasarkan aturan pakar yang tersedia.",
            "contradiction": contradiction_note
        })

    unique_damage_codes = list({r["kode_kerusakan"] for r in matched_rules})
    placeholders = ','.join(['?'] * len(unique_damage_codes))
    damages = [dict(row) for row in conn.execute(
        f"SELECT * FROM kerusakan WHERE kode_kerusakan IN ({placeholders})", unique_damage_codes
    ).fetchall()]
    conn.close()

    results = []
    for dmg in damages:
        triggering_rules = [r["kode_rule"] for r in matched_rules if r["kode_kerusakan"] == dmg["kode_kerusakan"]]
        results.append({**dmg, "triggered_by": triggering_rules})

    return jsonify({
        "status": "success",
        "facts": sorted(list(selected_symptoms)),
        "matched_rules": [r["kode_rule"] for r in matched_rules],
        "results": results,
        "contradiction": contradiction_note
    })

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
# IPO NASDAQ Calendar Feed

Bikin feed kalender `.ics` otomatis dari data IPO NASDAQ di
[stockanalysis.com/ipos/calendar](https://stockanalysis.com/ipos/calendar/),
di-refresh tiap 6 jam lewat GitHub Actions, dan bisa di-subscribe langsung
ke Apple Calendar / Google Calendar / Outlook.

## Cara Setup (sekali saja, ±10 menit)

### 1. Buat repo GitHub baru
1. Buka [github.com/new](https://github.com/new)
2. Nama repo bebas, misal `ipo-nasdaq-calendar`
3. Set **Public** (Pages gratis butuh repo public, kecuali punya GitHub Pro)
4. Klik **Create repository**

### 2. Upload isi folder ini
Upload semua file di project ini (pertahankan struktur folder):
```
ipo-nasdaq-calendar/
├── .github/workflows/update.yml
├── docs/ipo_nasdaq.ics
├── scrape.py
├── requirements.txt
└── README.md
```
Cara termudah: di halaman repo, klik **Add file > Upload files**, drag semua
file (termasuk folder `.github` dan `docs`), lalu **Commit changes**.

### 3. Aktifkan GitHub Pages
1. Di repo, buka **Settings > Pages**
2. Source: **Deploy from a branch**
3. Branch: **main**, folder: **/docs**
4. Klik **Save**
5. Tunggu 1-2 menit, URL Pages akan muncul di bagian atas, formatnya:
   `https://<username>.github.io/ipo-nasdaq-calendar/`

### 4. Jalankan scraper pertama kali
1. Buka tab **Actions** di repo
2. Klik workflow **Update IPO Calendar**
3. Klik **Run workflow > Run workflow** (trigger manual)
4. Tunggu selesai (~30 detik), cek log untuk memastikan sukses
5. Setelah itu, file `docs/ipo_nasdaq.ics` akan otomatis ter-update dan
   ter-commit setiap 6 jam

### 5. Ambil URL feed ICS
URL final feed kamu:
```
https://<username>.github.io/ipo-nasdaq-calendar/ipo_nasdaq.ics
```

### 6. Subscribe di Apple Calendar (iPhone)
1. **Settings > Apps > Calendar > Accounts > Add Account > Other**
2. Tap **Add Subscribed Calendar**
3. Tempel URL di atas, tap **Next**, lalu **Save**

### 6b. Subscribe di Mac
**Calendar app > File > New Calendar Subscription**, tempel URL yang sama.

## Cara kerja
- `scrape.py` ambil HTML stockanalysis.com/ipos/calendar, cari tabel IPO,
  filter baris `Exchange == NASDAQ`, lalu generate file ICS.
- GitHub Actions (`update.yml`) menjalankan script ini tiap 6 jam dan
  otomatis commit perubahan.
- GitHub Pages men-serve isi folder `docs/` sebagai website statis, jadi
  file `.ics` bisa diakses via URL publik dan di-subscribe kalender apapun.

## Kalau situs stockanalysis.com ubah struktur HTML-nya
Script akan gagal dengan pesan error "Tabel IPO tidak ditemukan". Kalau ini
terjadi, cek ulang struktur tabel di halaman dan sesuaikan nama kolom yang
dicari di fungsi `fetch_ipo_table()` / `clean_rows()` pada `scrape.py`.

## Catatan
- Refresh kalender di sisi Apple/Google/Outlook mengikuti jadwal polling
  masing-masing aplikasi (biasanya beberapa jam), bukan real-time — tapi
  datanya sendiri di sumber (GitHub Pages) sudah ter-update tiap 6 jam.
- Ini murni scraping data publik untuk keperluan personal; gunakan dengan
  wajar dan jangan jalankan lebih sering dari yang perlu.

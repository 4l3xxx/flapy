Flappy Bird Clone – Desain & Implementasi

Ringkas
- Dua versi: web (HTML5 Canvas) dan Python (pygame).
- Kontrol: Spasi/Klik/Touch untuk terbang. R untuk restart.
- Skor bertambah saat melewati pipa; tabrak pipa/tanah = Game Over.

Tujuan Game
- Pemain mengendalikan burung yang terbang dengan menekan tombol.
- Melewati celah di antara pipa yang bergerak tanpa menabrak.
- Skor setinggi mungkin (infinite game).

Desain Sistem
- Komponen
  - Burung (Bird): posisi `(x, y)`, kecepatan `vy`, terkena gravitasi, flap memberi `vy` negatif.
  - Pipa (Pipes): pasangan pipa atas-bawah, bergerak dari kanan ke kiri; celah (gap) diacak.
  - Tanah (Ground): batas bawah layar; menyentuh tanah = game over.
  - Skor: bertambah setiap melewati satu set pipa.
- Logika Game
  - Gravitasi: `vy += gravity`, `y += vy`.
  - Kontrol: Space/Klik/Touch → `vy = jumpVelocity`.
  - Pipa: spawn berkala, `x -= speed`, hapus jika di luar layar.
  - Kalah: tabrakan bird dengan pipa atau menyentuh tanah.
  - Menang: tidak ada; permainan tak berujung.
- Desain Visual
  - Latar langit biru, tanah cokelat.
  - Burung kuning sederhana (lingkaran + sayap/mata).
  - Pipa hijau, gap acak.
  - Skor di tengah atas.

Parameter Utama (default)
- Gravitasi `0.5`, kecepatan flap `-8.5`.
- Kecepatan pipa `~2.6 px/frame @60fps`.
- Jarak celah pipa `140 px`.
- Interval spawn `1500 ms`.

Struktur Proyek
- `index.html` – Kanvas + bootstrap UI versi web.
- `src/main.js` – Loop permainan (update/render), input, logika fisika, pipa, skor.
- `flappy.py` – Implementasi setara dengan pygame (tanpa aset eksternal).
- `README.md` – Desain & instruksi.

Menjalankan – Versi Web (Disarankan, tanpa dependency)
1) Buka langsung file `index.html` di browser modern (Chrome/Edge/Firefox).
2) Kontrol: Spasi/Klik/Touch untuk terbang, `R` untuk restart.

Menjalankan – Versi Python (pygame)
1) Pastikan Python 3 terpasang.
2) Instal pygame:
   - `pip install pygame`
3) Jalankan:
   - `python flappy.py`

Catatan Teknis
- Deteksi Tabrakan: circle-vs-rect menggunakan pendekatan clamp ke tepi rect lalu cek jarak ≤ radius².
- Skor: ditambah sekali saat pusat pipa lewat di belakang posisi X burung.
- Game State: `ready` → mulai saat input pertama; `running` → update normal; `gameover` → berhenti dan tunggu restart.
- Delta Time: versi Canvas menskalakan kecepatan terhadap `dt` agar gerak stabil pada fps berbeda.

Ide Peningkatan (Opsional)
- Animasi sprite burung, efek suara.
- Variasi gap/kecepatan adaptif berdasarkan skor.
- Menu utama dan papan skor lokal.
- Mode “ghost” untuk latihan tanpa game over.


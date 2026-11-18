========================================================================
  COSMIC ODYSSEY: SPACE CADET — Fast Brain & Logic Training
  Edisi SMA (~16 Tahun)  |  Python 3.10  |  PyGame-ce  |  NumPy
========================================================================

Deskripsi:
  Game edukasi bertema Sci-Fi antariksa berkecepatan tinggi yang melatih 
  kecepatan berhitung mental, refleks navigasi kinetik, dan logika pola aljabar.

Cara Menjalankan:
  1. Cukup double-click file:
       run.bat
  2. Atau jalankan lewat terminal / PowerShell:
       python main.py

========================================================================
Daftar Misi / Permainan:
========================================================================

1. 🚀 Mission 1: Rocket Speed Warp (Speed Mental Math & Algebra)
   - Melatih kecepatan berhitung cepat di bawah tekanan waktu (Timer 12 detik).
   - Operasi: Perkalian cepat, pembagian, kuadrat n², dan aljabar linier (mx + c).
   - Fitur Combo Multiplier: Semakin cepat & konsisten menjawab benar, 
     kecepatan roket (km/s) semakin melesat dan partikel warp menyala!
   - Kontrol: Klik mouse atau tekan angka [1], [2], [3], [4] di keyboard.

2. 🛸 Mission 2: Star Drifter (Kinetic Navigation & Asteroid Dodge)
   - Kendalikan kapal antariksa dengan inersia melayang di sabuk asteroid.
   - Kumpulkan 15 Energy Cores (bintang kristal) untuk menyalakan Hyperdrive.
   - Hindari asteroid yang bergerak bebas agar perisai (Shield) tidak berkurang.
   - Kontrol: 
     * Keyboard : W, A, S, D atau Tombol Panah
     * Mouse    : Tahan klik kiri atau arahkan kursor mouse untuk bermanuver
     * R        : Reset ronde

3. 🪐 Mission 3: Cyber Matrix (Pattern & Code Breaker)
   - Melatih logika pola deret bilangan (Aritmatika, Geometri, Fibonacci, 
     dan deret bertingkat tipe TPA/UTBK SMA).
   - Dilengkapi penjelasan/analisis rumus setiap kali menjawab sehingga 
     menambah pemahaman matematika.
   - Kontrol: Klik tombol A/B/C/D atau tekan tombol [1], [2], [3], [4].

========================================================================
Kostumisasi Audio & Musik Latar (Modular):
========================================================================
Kamu bisa mengganti musik atau efek suara kapan saja tanpa perlu menyentuh kode:

- Musik Latar (BGM):
  Taruh file lagu favoritmu di:
    assets/music/bgm.mp3  (atau bgm.ogg / bgm.wav)
  Game akan otomatis memutar lagu ini secara looping saat menu dibuka.

- Efek Suara (SFX):
  Taruh file suara di folder assets/sounds/:
    assets/sounds/correct.wav -> Suara jawaban benar
    assets/sounds/wrong.wav   -> Suara jawaban salah
    assets/sounds/launch.wav  -> Suara roket meluncur
    assets/sounds/star.wav    -> Suara kristal/bintang terkumpul
    assets/sounds/win.wav     -> Suara kemenangan misi
    assets/sounds/hit.wav     -> Suara tabrakan asteroid

*Catatan: Jika file audio belum dimasukkan, game otomatis menggunakan 
suara sintetis retro bawaan (berbasis NumPy) sehingga tidak akan pernah error.
========================================================================

# Tugas 1 - Vigenere & Autokey Cipher

Program enkripsi dan dekripsi menggunakan Vigenere Cipher dan Autokey Cipher, ditulis dengan Python.

- **Plaintext:** `ASPRAKGANTENG`
- **Key:** `Dion Febrian Halim` (diproses menjadi `DIONFEBRIANHALIM`)

## File

| File | Isi |
|---|---|
| `vigenere_autokey.py` | Program Python (enkripsi dan dekripsi Vigenere dan Autokey) |
| `Tugas1_Vigenere_Autokey.xlsx` | Perhitungan manual di Excel (sheet `Vigenere` dan `Autokey`) |

## Cara Menjalankan

```bash
python vigenere_autokey.py
```

Output yang diharapkan:

```
== Vigenere ==
Ciphertext: DADEFOHRVTRUG
Decrypted : ASPRAKGANTENG

== Autokey ==
Ciphertext: DADEFOHRVTRUG
Decrypted : ASPRAKGANTENG
```

## Alur Program

### 1. Pembersihan input (`clean`)

Teks diubah menjadi huruf kapital, lalu karakter selain huruf (spasi, angka, simbol) dibuang. Dengan begitu `Dion Febrian Halim` menjadi `DIONFEBRIANHALIM`.

### 2. Konversi huruf ke angka

Setiap huruf dipetakan ke angka sesuai tabel di soal: A = 0, B = 1, ..., Z = 25. Di kode, ini dilakukan dengan `ord(huruf) - 65`. Hasil hitungan dikembalikan menjadi huruf dengan `chr(angka + 65)`.

### 3. Vigenere Cipher (`vigenere`)

1. Key diulang (dicycle) sampai panjangnya sama dengan plaintext. Kode memakai `key[i % len(key)]`.
2. Setiap huruf plaintext (P) dijumlahkan dengan huruf key (K) pada posisi yang sama.
3. Hasilnya di-mod 26 lalu dikonversi kembali menjadi huruf.

```
Enkripsi: C = (P + K) mod 26
Dekripsi: P = (C - K) mod 26
```

Parameter `decrypt=True` mengganti operasi penjumlahan menjadi pengurangan.

### 4. Autokey Cipher (`autokey_encrypt`, `autokey_decrypt`)

Bedanya dengan Vigenere ada di key stream. Key tidak diulang, tetapi diikuti oleh plaintext itu sendiri:

```
key stream = key + plaintext
```

- **Enkripsi:** key stream dibentuk dari `key + plaintext`, dipotong sesuai panjang plaintext, lalu dihitung dengan rumus yang sama (`C = (P + K) mod 26`).
- **Dekripsi:** key stream awalnya hanya `key`. Setiap satu huruf plaintext berhasil didekripsi, huruf itu ditambahkan ke key stream untuk dipakai pada huruf berikutnya.

Pada tugas ini panjang key (16 huruf) lebih besar dari plaintext (13 huruf), sehingga plaintext tidak sempat terpakai sebagai key. Akibatnya key stream Autokey sama dengan Vigenere dan ciphertext-nya juga sama.

## Contoh Perhitungan (3 huruf pertama)

| No | Plain | P | Key | K | (P + K) mod 26 | Cipher |
|---|---|---|---|---|---|---|
| 1 | A | 0 | D | 3 | 3 | D |
| 2 | S | 18 | I | 8 | 26 mod 26 = 0 | A |
| 3 | P | 15 | O | 14 | 29 mod 26 = 3 | D |

Hasil lengkap: `ASPRAKGANTENG` menjadi `DADEFOHRVTRUG`.

## Alur di Excel

Kolom pada sheet mengikuti langkah di atas:

1. `Plain` diambil per huruf dari plaintext (`MID`).
2. `P` = `CODE(huruf) - 65`.
3. `Key` diambil dari key (Vigenere: diulang dengan `MOD`; Autokey: key lalu plaintext).
4. `K` = `CODE(huruf key) - 65`.
5. `C` = `MOD(P + K, 26)`.
6. `Cipher` = `CHAR(C + 65)`.

Blok `DEKRIPSI` di sebelah kanan membalik prosesnya (`MOD(C - K, 26)`) dan kolom `Cocok plaintext?` memastikan hasil dekripsi sama dengan plaintext awal.
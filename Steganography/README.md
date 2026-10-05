# Steganografi LSB (Python)

Program encode/decode steganografi untuk menyembunyikan pesan teks atau file (termasuk gambar) di dalam gambar cover dengan metode LSB (Least Significant Bit).

## Instalasi
```
pip install -r requirements.txt
```

## Penggunaan
```
# cek kapasitas cover
python stego.py info -c contoh/cover.png

# sembunyikan teks
python stego.py encode -c contoh/cover.png -o hasil/stego_teks.png -t "pesan rahasia"
python stego.py decode -s hasil/stego_teks.png

# sembunyikan gambar/file
python stego.py encode -c contoh/cover.png -o hasil/stego_gambar.png -f contoh/rahasia.png
python stego.py decode -s hasil/stego_gambar.png -o hasil/rahasia_hasil.png
```

Output stego-image selalu PNG (lossless). Jangan dikonversi ke JPEG karena pesan akan rusak.

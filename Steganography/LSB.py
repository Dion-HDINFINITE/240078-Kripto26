#!/usr/bin/env python3
"""
Steganografi LSB (Least Significant Bit) untuk gambar.

Menyembunyikan pesan teks atau file (misalnya gambar) ke dalam bit paling
tidak signifikan dari setiap kanal warna (R, G, B) pada gambar cover.
Output harus lossless (PNG), karena format lossy seperti JPEG merusak LSB.

Format paket yang disisipkan:
    MAGIC (4 byte) | tipe (1) | panjang nama (2) | panjang data (4) | nama | data
"""
import argparse
import os
import struct
import sys

import numpy as np
from PIL import Image

MAGIC = b"STG1"
TIPE_TEKS, TIPE_FILE = 0, 1
HEADER_FMT = ">4sBHI"
HEADER_LEN = struct.calcsize(HEADER_FMT)  # 11 byte


def kapasitas_byte(lebar, tinggi):
    """Jumlah byte maksimum yang muat (1 bit per kanal, 3 kanal per piksel)."""
    return lebar * tinggi * 3 // 8


def buka_cover(path):
    return Image.open(path).convert("RGB")


def sembunyikan(cover_path, out_path, data, tipe, nama=""):
    img = buka_cover(cover_path)
    lebar, tinggi = img.size
    nama_b = nama.encode("utf-8")
    paket = struct.pack(HEADER_FMT, MAGIC, tipe, len(nama_b), len(data)) + nama_b + data

    kap = kapasitas_byte(lebar, tinggi)
    if len(paket) > kap:
        raise ValueError(
            f"Payload terlalu besar: {len(paket)} byte, kapasitas cover {kap} byte."
        )

    piksel = np.array(img, dtype=np.uint8).flatten()
    bit = np.unpackbits(np.frombuffer(paket, dtype=np.uint8))
    asli = piksel.copy()
    piksel[: len(bit)] = (piksel[: len(bit)] & 0xFE) | bit

    Image.fromarray(piksel.reshape(tinggi, lebar, 3), "RGB").save(out_path, format="PNG")

    mse = np.mean((asli.astype(float) - piksel.astype(float)) ** 2)
    psnr = float("inf") if mse == 0 else 10 * np.log10(255**2 / mse)
    return {
        "ukuran_payload": len(paket),
        "kapasitas": kap,
        "bit_disisipkan": len(bit),
        "nilai_berubah": int(np.sum(asli != piksel)),
        "psnr": psnr,
    }


def _baca_byte(piksel, awal_bit, jumlah_byte):
    bit = piksel[awal_bit : awal_bit + jumlah_byte * 8] & 1
    return np.packbits(bit).tobytes()


def ekstrak(stego_path):
    piksel = np.array(buka_cover(stego_path), dtype=np.uint8).flatten()

    magic, tipe, len_nama, len_data = struct.unpack(
        HEADER_FMT, _baca_byte(piksel, 0, HEADER_LEN)
    )
    if magic != MAGIC:
        raise ValueError("Tidak ditemukan pesan tersembunyi pada gambar ini.")

    total = HEADER_LEN + len_nama + len_data
    if total * 8 > len(piksel):
        raise ValueError("Header rusak: panjang data melebihi ukuran gambar.")

    isi = _baca_byte(piksel, HEADER_LEN * 8, len_nama + len_data)
    nama = isi[:len_nama].decode("utf-8")
    return tipe, nama, isi[len_nama:]


def cmd_encode(a):
    if a.teks is not None:
        data, tipe, nama = a.teks.encode("utf-8"), TIPE_TEKS, ""
    else:
        with open(a.file, "rb") as f:
            data = f.read()
        tipe, nama = TIPE_FILE, os.path.basename(a.file)

    r = sembunyikan(a.cover, a.out, data, tipe, nama)
    print(f"[+] Cover           : {a.cover}")
    print(f"[+] Jenis pesan     : {'teks' if tipe == TIPE_TEKS else 'file (' + nama + ')'}")
    print(f"[+] Ukuran payload  : {r['ukuran_payload']} byte (kapasitas {r['kapasitas']} byte)")
    print(f"[+] Nilai kanal yg berubah: {r['nilai_berubah']} dari {r['bit_disisipkan']} bit")
    print(f"[+] PSNR            : {r['psnr']:.2f} dB")
    print(f"[+] Stego-image     : {a.out}")


def cmd_decode(a):
    tipe, nama, data = ekstrak(a.stego)
    if tipe == TIPE_TEKS:
        print("[+] Jenis pesan : teks")
        print(f"[+] Isi pesan   : {data.decode('utf-8')}")
    else:
        out = a.out or f"hasil_{nama}"
        with open(out, "wb") as f:
            f.write(data)
        print(f"[+] Jenis pesan : file ({nama}, {len(data)} byte)")
        print(f"[+] Disimpan ke : {out}")


def cmd_info(a):
    lebar, tinggi = buka_cover(a.cover).size
    print(f"[+] Resolusi : {lebar} x {tinggi}")
    print(f"[+] Kapasitas: {kapasitas_byte(lebar, tinggi)} byte")


def main():
    p = argparse.ArgumentParser(description="Steganografi LSB pada gambar PNG.")
    sub = p.add_subparsers(dest="perintah", required=True)

    e = sub.add_parser("encode", help="sembunyikan pesan/file ke gambar")
    e.add_argument("-c", "--cover", required=True, help="gambar cover")
    e.add_argument("-o", "--out", required=True, help="stego-image (PNG)")
    g = e.add_mutually_exclusive_group(required=True)
    g.add_argument("-t", "--teks", help="pesan teks")
    g.add_argument("-f", "--file", help="file yang disembunyikan (mis. gambar)")
    e.set_defaults(fn=cmd_encode)

    d = sub.add_parser("decode", help="ambil kembali pesan/file")
    d.add_argument("-s", "--stego", required=True, help="stego-image")
    d.add_argument("-o", "--out", help="nama file output (jika pesan berupa file)")
    d.set_defaults(fn=cmd_decode)

    i = sub.add_parser("info", help="cek kapasitas gambar cover")
    i.add_argument("-c", "--cover", required=True)
    i.set_defaults(fn=cmd_info)

    a = p.parse_args()
    try:
        a.fn(a)
    except (ValueError, OSError) as err:
        print(f"[!] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

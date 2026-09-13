"""
Hill Cipher (2x2) - Enkripsi, Dekripsi, dan Pencarian Kunci
Praktikum Kriptografi - Pertemuan 2
Dion Febrian Halim - NPM 140810240078
"""

import numpy as np

M = 26  # ukuran alfabet (A-Z)


# ---------- Util dasar ----------
def clean_text(text: str) -> str:
    """Hapus non-huruf dan ubah ke huruf kapital."""
    return "".join(ch for ch in text.upper() if ch.isalpha())


def text_to_nums(text: str):
    return [ord(ch) - 65 for ch in text]


def nums_to_text(nums):
    return "".join(chr(int(n) % M + 65) for n in nums)


def mod_inverse(a: int, m: int = M) -> int:
    """Mencari invers modulo a terhadap m menggunakan Extended Euclidean Algorithm."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"{a} tidak memiliki invers modulo {m} (gcd != 1)")


def matrix_mod_inverse(K: np.ndarray, m: int = M) -> np.ndarray:
    """Mencari invers matriks kunci K (2x2) secara modulo m."""
    det = int(round(np.linalg.det(K)))
    det_mod = det % m
    det_inv = mod_inverse(det_mod, m)

    # adjoint untuk matriks 2x2: [[d,-b],[-c,a]]
    adj = np.array([[K[1][1], -K[0][1]],
                     [-K[1][0], K[0][0]]])

    K_inv = (det_inv * adj) % m
    return K_inv.astype(int)


def pad_to_even(nums, block_size=2):
    """Menambahkan padding 'X' (23) jika panjang teks tidak habis dibagi block_size."""
    while len(nums) % block_size != 0:
        nums.append(23)  # X sebagai padding
    return nums


# ---------- Fungsi utama ----------
def is_key_valid(K: np.ndarray, m: int = M) -> bool:
    """Cek apakah matriks kunci K punya invers mod m (determinan koprima dengan m)."""
    det = int(round(np.linalg.det(K))) % m
    try:
        mod_inverse(det, m)
        return True
    except ValueError:
        return False


def hill_encrypt(plaintext: str, K: np.ndarray) -> str:
    plaintext = clean_text(plaintext)
    nums = pad_to_even(text_to_nums(plaintext))
    result = []

    if not is_key_valid(K, M):
        det = int(round(np.linalg.det(K))) % M
        print(f"\n[PERINGATAN] Determinan matriks K = {det} (mod 26) tidak koprima dengan 26 "
              f"(gcd != 1). Kunci ini TIDAK memiliki invers, sehingga ciphertext di bawah ini "
              f"TIDAK BISA didekripsi kembali. Pilih kunci lain (determinan harus ganjil dan "
              f"bukan kelipatan 13) jika kunci ini akan dipakai untuk dekripsi juga.\n")

    print(f"\nPlaintext  : {plaintext}")
    print(f"Angka      : {nums}")

    for i in range(0, len(nums), 2):
        block = np.array(nums[i:i + 2])
        cipher_block = K.dot(block) % M
        result.extend(cipher_block)
        print(f"  Blok {block.tolist()} -> K.P = {K.dot(block).tolist()} "
              f"mod 26 = {cipher_block.tolist()} -> "
              f"{nums_to_text(cipher_block)}")

    ciphertext = nums_to_text(result)
    print(f"Ciphertext : {ciphertext}")
    return ciphertext


def hill_decrypt(ciphertext: str, K: np.ndarray) -> str:
    ciphertext = clean_text(ciphertext)
    nums = text_to_nums(ciphertext)
    K_inv = matrix_mod_inverse(K, M)
    result = []

    print(f"\nCiphertext    : {ciphertext}")
    print(f"K^-1 (mod 26) :\n{K_inv}")

    for i in range(0, len(nums), 2):
        block = np.array(nums[i:i + 2])
        plain_block = K_inv.dot(block) % M
        result.extend(plain_block)
        print(f"  Blok {block.tolist()} -> K^-1.C = {K_inv.dot(block).tolist()} "
              f"mod 26 = {plain_block.tolist()} -> "
              f"{nums_to_text(plain_block)}")

    plaintext = nums_to_text(result)
    print(f"Plaintext     : {plaintext}")
    return plaintext


def hill_find_key(plaintext: str, ciphertext: str) -> np.ndarray:
    """Mencari matriks kunci K (2x2) dari pasangan plaintext-ciphertext (known-plaintext attack).

    Mencoba semua kombinasi 2 blok (bukan cuma 2 blok pertama), karena matriks P yang
    dibentuk dari suatu pasangan blok bisa jadi tidak invertible mod 26 (blok-bloknya
    tidak bebas linear), meskipun kuncinya sendiri valid.
    """
    plaintext = clean_text(plaintext)
    ciphertext = clean_text(ciphertext)
    if len(plaintext) < 4 or len(ciphertext) < 4:
        raise ValueError("Butuh minimal 4 huruf plaintext & ciphertext (2 blok) untuk K 2x2")

    p_nums = text_to_nums(plaintext)
    c_nums = text_to_nums(ciphertext)
    p_blocks = [p_nums[i:i + 2] for i in range(0, len(p_nums) - 1, 2)]
    c_blocks = [c_nums[i:i + 2] for i in range(0, len(c_nums) - 1, 2)]
    n_blocks = min(len(p_blocks), len(c_blocks))

    tried = []
    for i in range(n_blocks):
        for j in range(i + 1, n_blocks):
            P = np.array([[p_blocks[i][0], p_blocks[j][0]],
                           [p_blocks[i][1], p_blocks[j][1]]])
            C = np.array([[c_blocks[i][0], c_blocks[j][0]],
                           [c_blocks[i][1], c_blocks[j][1]]])
            det_mod = int(round(np.linalg.det(P))) % M
            tried.append((i, j, det_mod))
            if not is_key_valid(P, M):
                continue

            print(f"\nMenggunakan blok ke-{i+1} dan ke-{j+1} (blok lain dilewati karena "
                  f"matriks P dari kombinasi tersebut tidak invertible mod 26).")
            print(f"P (plaintext matrix) =\n{P}")
            print(f"C (ciphertext matrix) =\n{C}")

            P_inv = matrix_mod_inverse(P, M)
            print(f"P^-1 (mod 26) =\n{P_inv}")

            K = C.dot(P_inv) % M
            print(f"K = C . P^-1 (mod 26) =\n{K}")
            return K.astype(int)

    detail = ", ".join(f"blok {i+1}&{j+1}: det mod 26={d}" for i, j, d in tried)
    raise ValueError(
        "Tidak ditemukan kombinasi 2 blok yang membentuk matriks P invertible mod 26 "
        f"dari plaintext/ciphertext yang diberikan ({detail}). Coba gunakan plaintext "
        "yang lebih panjang atau kombinasi huruf lain."
    )


# ---------- CLI ----------
def parse_key_input(k_raw: str) -> np.ndarray:
    """Parsing input matriks K agar tahan terhadap pemisah koma/spasi berlebih."""
    cleaned = k_raw.replace(",", " ")
    k_vals = [int(v) for v in cleaned.split()]
    if len(k_vals) != 4:
        raise ValueError(
            f"Matriks K harus terdiri dari 4 angka (2x2), tapi yang terbaca ada {len(k_vals)}. "
            f"Contoh input yang benar: 7 6 2 5"
        )
    return np.array(k_vals).reshape(2, 2)


def main():
    print("=" * 50)
    print(" HILL CIPHER (2x2) - Enkripsi / Dekripsi / Cari Kunci")
    print(" [v2 - auto block-pair search untuk cari kunci]")
    print("=" * 50)
    print("1. Enkripsi")
    print("2. Dekripsi")
    print("3. Cari Kunci (known-plaintext attack)")
    choice = input("Pilih menu (1/2/3): ").strip()

    if choice == "1":
        pt = input("Plaintext        : ")
        k_raw = input("Matriks K (contoh: 7 6 2 5) : ")
        K = parse_key_input(k_raw)
        hill_encrypt(pt, K)

    elif choice == "2":
        ct = input("Ciphertext       : ")
        k_raw = input("Matriks K (contoh: 3 2 2 7) : ")
        K = parse_key_input(k_raw)
        hill_decrypt(ct, K)

    elif choice == "3":
        pt = input("Plaintext (known) : ")
        ct = input("Ciphertext (known): ")
        hill_find_key(pt, ct)

    else:
        print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()

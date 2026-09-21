"""Tugas 1 - Vigenere & Autokey Cipher (enkripsi + dekripsi)."""


def clean(text):
    """Huruf saja, kapital (spasi & simbol dibuang)."""
    return "".join(c for c in text.upper() if c.isalpha())


def vigenere(text, key, decrypt=False):
    text, key = clean(text), clean(key)
    out = []
    for i, ch in enumerate(text):
        p = ord(ch) - 65
        k = ord(key[i % len(key)]) - 65
        v = (p - k) % 26 if decrypt else (p + k) % 26
        out.append(chr(v + 65))
    return "".join(out)


def autokey_encrypt(plaintext, key):
    plaintext, key = clean(plaintext), clean(key)
    stream = (key + plaintext)[: len(plaintext)]
    return "".join(
        chr((ord(p) - 65 + ord(k) - 65) % 26 + 65)
        for p, k in zip(plaintext, stream)
    )


def autokey_decrypt(ciphertext, key):
    ciphertext, key = clean(ciphertext), clean(key)
    stream = list(key)
    out = []
    for i, c in enumerate(ciphertext):
        p = (ord(c) - 65 - (ord(stream[i]) - 65)) % 26
        out.append(chr(p + 65))
        stream.append(out[-1])  # plaintext hasil dekripsi jadi key berikutnya
    return "".join(out)


if __name__ == "__main__":
    plaintext = "ASPRAKGANTENG"
    key = "Dion Febrian Halim"

    print("Plaintext :", plaintext)
    print("Key       :", clean(key))

    print("\n== Vigenere ==")
    c = vigenere(plaintext, key)
    print("Ciphertext:", c)
    print("Decrypted :", vigenere(c, key, decrypt=True))

    print("\n== Autokey ==")
    c = autokey_encrypt(plaintext, key)
    print("Ciphertext:", c)
    print("Decrypted :", autokey_decrypt(c, key))
#Plaintext + Key + Nonce
#→ ChaCha20 Encrypt
#→ Ciphertext
C#iphertext + Poly1305
#→ ตรวจว่าโดนแก้ไหม
#Ciphertext + Key
#→ Decrypt กลับเป็นข้อความเดิม

import os
import struct
import hmac


def rotl32(x, n):
    return ((x << n) & 0xffffffff) | (x >> (32 - n))


def quarter_round(state, a, b, c, d):
    state[a] = (state[a] + state[b]) & 0xffffffff
    state[d] ^= state[a]
    state[d] = rotl32(state[d], 16)

    state[c] = (state[c] + state[d]) & 0xffffffff
    state[b] ^= state[c]
    state[b] = rotl32(state[b], 12)

    state[a] = (state[a] + state[b]) & 0xffffffff
    state[d] ^= state[a]
    state[d] = rotl32(state[d], 8)

    state[c] = (state[c] + state[d]) & 0xffffffff
    state[b] ^= state[c]
    state[b] = rotl32(state[b], 7)


def chacha20_block(key, counter, nonce):
    constants = b"expand 32-byte k"

    state = list(struct.unpack("<4I", constants))
    state += list(struct.unpack("<8I", key))
    state.append(counter)
    state += list(struct.unpack("<3I", nonce))

    working = state[:]

    for _ in range(10):
        quarter_round(working, 0, 4, 8, 12)
        quarter_round(working, 1, 5, 9, 13)
        quarter_round(working, 2, 6, 10, 14)
        quarter_round(working, 3, 7, 11, 15)

        quarter_round(working, 0, 5, 10, 15)
        quarter_round(working, 1, 6, 11, 12)
        quarter_round(working, 2, 7, 8, 13)
        quarter_round(working, 3, 4, 9, 14)

    output = [(working[i] + state[i]) & 0xffffffff for i in range(16)]
    return struct.pack("<16I", *output)


def chacha20_encrypt(key, nonce, plaintext, counter=1):
    result = bytearray()

    for block_index in range(0, len(plaintext), 64):
        block = plaintext[block_index:block_index + 64]
        keystream = chacha20_block(key, counter, nonce)
        counter += 1

        encrypted = bytes([b ^ k for b, k in zip(block, keystream)])
        result.extend(encrypted)

    return bytes(result)


def clamp_r(r):
    r = bytearray(r)
    r[3] &= 15
    r[7] &= 15
    r[11] &= 15
    r[15] &= 15
    r[4] &= 252
    r[8] &= 252
    r[12] &= 252
    return bytes(r)


def poly1305_mac(msg, key):
    r = int.from_bytes(clamp_r(key[:16]), "little")
    s = int.from_bytes(key[16:], "little")

    p = (1 << 130) - 5
    acc = 0

    for i in range(0, len(msg), 16):
        block = msg[i:i + 16]
        n = int.from_bytes(block + b"\x01", "little")
        acc = (acc + n) % p
        acc = (acc * r) % p

    tag = (acc + s) % (1 << 128)
    return tag.to_bytes(16, "little")


def pad16(data):
    if len(data) % 16 == 0:
        return b""
    return b"\x00" * (16 - (len(data) % 16))


def build_mac_data(aad, ciphertext):
    return (
        aad +
        pad16(aad) +
        ciphertext +
        pad16(ciphertext) +
        struct.pack("<Q", len(aad)) +
        struct.pack("<Q", len(ciphertext))
    )


def encrypt(message, key, aad=b""):
    if len(key) != 32:
        raise ValueError("Key ต้องยาว 32 bytes")

    nonce = os.urandom(12)

    poly_key = chacha20_block(key, 0, nonce)[:32]
    ciphertext = chacha20_encrypt(key, nonce, message, counter=1)

    mac_data = build_mac_data(aad, ciphertext)
    tag = poly1305_mac(mac_data, poly_key)

    return nonce + ciphertext + tag


def decrypt(data, key, aad=b""):
    if len(key) != 32:
        raise ValueError("Key ต้องยาว 32 bytes")

    nonce = data[:12]
    tag = data[-16:]
    ciphertext = data[12:-16]

    poly_key = chacha20_block(key, 0, nonce)[:32]
    mac_data = build_mac_data(aad, ciphertext)
    expected_tag = poly1305_mac(mac_data, poly_key)

    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("Invalid tag: ข้อมูลถูกแก้ไข หรือ key ผิด")

    plaintext = chacha20_encrypt(key, nonce, ciphertext, counter=1)
    return plaintext


# -------------------------
# TEST
# -------------------------

key = os.urandom(32)

text = "hello world สวัสดีครับ".encode("utf-8")

encrypted = encrypt(text, key)
decrypted = decrypt(encrypted, key)

print("Key:", key.hex())
print("Encrypted:", encrypted.hex())
print("Decrypted:", decrypted.decode("utf-8"))
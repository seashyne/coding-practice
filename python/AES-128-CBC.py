import os

SBOX = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]

INV_SBOX = [0] * 256
for i, v in enumerate(SBOX):
    INV_SBOX[v] = i

RCON = [0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36]

def xtime(a):
    return ((a << 1) ^ 0x1b) & 0xff if a & 0x80 else (a << 1)

def gmul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        a = xtime(a)
        b >>= 1
    return p & 0xff

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def sub_word(word):
    return [SBOX[b] for b in word]

def rot_word(word):
    return word[1:] + word[:1]

def key_expansion(key):
    if len(key) != 16:
        raise ValueError("AES-128 key ต้องยาว 16 bytes")

    words = [list(key[i:i+4]) for i in range(0, 16, 4)]

    for i in range(4, 44):
        temp = words[i - 1].copy()

        if i % 4 == 0:
            temp = sub_word(rot_word(temp))
            temp[0] ^= RCON[i // 4]

        words.append([words[i - 4][j] ^ temp[j] for j in range(4)])

    round_keys = []
    for r in range(11):
        round_key = []
        for w in words[4*r:4*r+4]:
            round_key += w
        round_keys.append(round_key)

    return round_keys

def bytes_to_state(block):
    return [[block[r + 4*c] for c in range(4)] for r in range(4)]

def state_to_bytes(state):
    return bytes(state[r][c] for c in range(4) for r in range(4))

def add_round_key(state, round_key):
    for c in range(4):
        for r in range(4):
            state[r][c] ^= round_key[r + 4*c]

def sub_bytes(state):
    for r in range(4):
        for c in range(4):
            state[r][c] = SBOX[state[r][c]]

def inv_sub_bytes(state):
    for r in range(4):
        for c in range(4):
            state[r][c] = INV_SBOX[state[r][c]]

def shift_rows(state):
    for r in range(1, 4):
        state[r] = state[r][r:] + state[r][:r]

def inv_shift_rows(state):
    for r in range(1, 4):
        state[r] = state[r][-r:] + state[r][:-r]

def mix_columns(state):
    for c in range(4):
        a = [state[r][c] for r in range(4)]

        state[0][c] = gmul(a[0],2) ^ gmul(a[1],3) ^ a[2] ^ a[3]
        state[1][c] = a[0] ^ gmul(a[1],2) ^ gmul(a[2],3) ^ a[3]
        state[2][c] = a[0] ^ a[1] ^ gmul(a[2],2) ^ gmul(a[3],3)
        state[3][c] = gmul(a[0],3) ^ a[1] ^ a[2] ^ gmul(a[3],2)

def inv_mix_columns(state):
    for c in range(4):
        a = [state[r][c] for r in range(4)]

        state[0][c] = gmul(a[0],14) ^ gmul(a[1],11) ^ gmul(a[2],13) ^ gmul(a[3],9)
        state[1][c] = gmul(a[0],9) ^ gmul(a[1],14) ^ gmul(a[2],11) ^ gmul(a[3],13)
        state[2][c] = gmul(a[0],13) ^ gmul(a[1],9) ^ gmul(a[2],14) ^ gmul(a[3],11)
        state[3][c] = gmul(a[0],11) ^ gmul(a[1],13) ^ gmul(a[2],9) ^ gmul(a[3],14)

def aes_encrypt_block(block, round_keys):
    state = bytes_to_state(block)

    add_round_key(state, round_keys[0])

    for r in range(1, 10):
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        add_round_key(state, round_keys[r])

    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, round_keys[10])

    return state_to_bytes(state)

def aes_decrypt_block(block, round_keys):
    state = bytes_to_state(block)

    add_round_key(state, round_keys[10])
    inv_shift_rows(state)
    inv_sub_bytes(state)

    for r in range(9, 0, -1):
        add_round_key(state, round_keys[r])
        inv_mix_columns(state)
        inv_shift_rows(state)
        inv_sub_bytes(state)

    add_round_key(state, round_keys[0])

    return state_to_bytes(state)

def pkcs7_pad(data):
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len]) * pad_len

def pkcs7_unpad(data):
    pad_len = data[-1]

    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding")

    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding")

    return data[:-pad_len]

def aes_cbc_encrypt(plaintext, key):
    round_keys = key_expansion(key)
    iv = os.urandom(16)

    plaintext = pkcs7_pad(plaintext)

    prev = iv
    ciphertext = b""

    for i in range(0, len(plaintext), 16):
        block = plaintext[i:i+16]
        block = xor_bytes(block, prev)
        encrypted = aes_encrypt_block(block, round_keys)
        ciphertext += encrypted
        prev = encrypted

    return iv + ciphertext

def aes_cbc_decrypt(data, key):
    round_keys = key_expansion(key)

    iv = data[:16]
    ciphertext = data[16:]

    if len(ciphertext) % 16 != 0:
        raise ValueError("Ciphertext length ต้องหาร 16 ลงตัว")

    prev = iv
    plaintext = b""

    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        decrypted = aes_decrypt_block(block, round_keys)
        plaintext += xor_bytes(decrypted, prev)
        prev = block

    return pkcs7_unpad(plaintext)

# -------------------------
# TEST
# -------------------------

key = os.urandom(16)  # AES-128 = 16 bytes
message = "hello AES สวัสดีครับ".encode("utf-8")

encrypted = aes_cbc_encrypt(message, key)
decrypted = aes_cbc_decrypt(encrypted, key)

print("Key:", key.hex())
print("Encrypted:", encrypted.hex())
print("Decrypted:", decrypted.decode("utf-8"))
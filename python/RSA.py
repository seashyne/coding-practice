import math
import random


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def mod_inverse(e, phi):
    # Extended Euclidean Algorithm
    old_r, r = e, phi
    old_s, s = 1, 0

    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s

    return old_s % phi


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2

    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2

    return True


def generate_prime(start=100, end=500):
    while True:
        n = random.randint(start, end)
        if is_prime(n):
            return n


def generate_keys():
    p = generate_prime()
    q = generate_prime()

    while p == q:
        q = generate_prime()

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if gcd(e, phi) != 1:
        e = 3
        while gcd(e, phi) != 1:
            e += 2

    d = mod_inverse(e, phi)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key, p, q


def encrypt_text(text, public_key):
    e, n = public_key
    encrypted = []

    for char in text:
        m = ord(char)
        c = pow(m, e, n)
        encrypted.append(c)

    return encrypted


def decrypt_text(encrypted, private_key):
    d, n = private_key
    text = ""

    for c in encrypted:
        m = pow(c, d, n)
        text += chr(m)

    return text


public_key, private_key, p, q = generate_keys()

message = "hello"

encrypted = encrypt_text(message, public_key)
decrypted = decrypt_text(encrypted, private_key)

print("p:", p)
print("q:", q)
print("Public key:", public_key)
print("Private key:", private_key)
print("Original:", message)
print("Encrypted:", encrypted)
print("Decrypted:", decrypted)
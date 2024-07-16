import random 
import math

def mod_inverse(e, phi):
    for d in range(3, phi):
        if (d * e) % phi == 1:
            return d
    raise ValueError("mod_inverse doesn't exist")

prime1 = 97
prime2 = 23

p = prime1
q = prime2

n = p * q
phi_n = (p - 1) * (q - 1)


e = random.randint(3, phi_n - 1)
while math.gcd(e, phi_n) != 1:
    e = random.randint(3, phi_n - 1)

d = mod_inverse(e, phi_n)

print("public key: ", e)
print("private key: ", d)
print("n: ", n)
print("phi of n: ", phi_n)
print("p: ", p)
print("q: ", q)

message = "Hello World"

message_encoded = [ord(c) for c in message]

ciphertext = [pow(ch, e, n) for ch in message_encoded]

print("Ciphertext: ", ciphertext)

message_decoded = [pow(ch, d, n) for ch in ciphertext]
message_decrypted = "".join(chr(ch) for ch in message_decoded)

print("Decrypted Message: ", message_decrypted)

message_to_sign = "Sign this message"

message_to_sign_encoded = [ord(c) for c in message_to_sign]
signature = [pow(ch, d, n) for ch in message_to_sign_encoded]

print("Signature: ", signature)

verified_message_encoded = [pow(ch, e, n) for ch in signature]
verified_message = "".join(chr(ch) for ch in verified_message_encoded)

print("Verified Message: ", verified_message)

if message_to_sign == verified_message:
    print("The signature is valid.")
else:
    print("The signature is invalid.")


from util import *
import os
from hashlib import sha256, sha512
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def pack_point(P):
    x, y = P
    return (int(x) << 256) | int(y)


def unpack_point(n):
    x = n >> 256
    y = n & ((1 << 256) - 1)
    return (x, y)


def get_curve25519_base():
    p = 2**255 - 19
    x = 9
    y2 = (x**3 + 486662*x**2 + x) % p
    y = pow(y2, (p + 3) // 8, p)
    if (y * y) % p != y2:
        y = (y * pow(2, (p - 1) // 4, p)) % p
    return (x, y)


def vec2key(v, q, N):
    x = 0
    for i in range(N):
        x += int(v[i]) * (q ** i)
    return int.from_bytes(sha256(str(x).encode()).digest(), 'little')


MAX_MSG = 100


if __name__ == '__main__':
    ecc = ECC(486662, 1, 2**255 - 19)
    G = (9, 14781619447589544791020593568409986887264606134616475288964881837755586237401)
    
    master_sec = int.from_bytes(os.urandom(30))
    master_pub = ecc.mul(G, master_sec)

    print(f"[+] The Celestial Master's Seal: {pack_point(master_pub)}")
    
    flag = os.environ.get("GZCTF_FLAG",'')
    aes_key = sha256(str(master_sec).encode()).digest()
    enc_flag = AES.new(aes_key, AES.MODE_ECB).encrypt(pad(flag.encode(), 32))
    print(f"[+] Heavenly Cipher: {enc_flag.hex()}")
    
    round_num = 0
    
    while True:
        round_num += 1
        lwe = LWE()
        msg_count = 0
        print(f"[+] Crystal domain's modulus for today: {lwe.q}")

        while True:
            print(f"\n[+] Round {round_num} | Spiritual trials: {msg_count}/{MAX_MSG}")

            choice = input("[-] Channel your intent (m=message, e=exchange):").strip()
            
            if choice == 'm':
                if msg_count >= MAX_MSG:
                    print("[!] Your spiritual energy is depleted this round.")
                    continue
                
                try:
                    msg = int(input("[-] Offer your spiritual essence (int):").strip())
                except ValueError:
                    print("[!] Invalid essence format")
                    continue
                
                msg_bytes = str(msg).encode()
                m_hash = int(sha512(msg_bytes).hexdigest(), 16)
                m_trunc = m_hash & ((1 << 128) - 1)
                
                ct = lwe.encrypt(m_trunc)
                print(f"[+] Resonance echoes: {ct}")
                msg_count += 1
            
            elif choice == 'e':
                try:
                    point_int = int(input("[-] Forge your spirit formation (int):").strip())
                except ValueError:
                    print("[!] Invalid formation")
                    continue
                
                point_int &= (1 << 512) - 1
                x, y = unpack_point(point_int)
                
                priv = lwe.export_priv_key()
                x ^= priv
                y ^= priv
                
                result = ecc.mul((x, y), master_sec)
                if result is None:
                    print("[+] Domain resonance: 0")
                else:
                    print(f"[+] Domain resonance: {pack_point(result)}")
                break
            
            else:
                print("[!] Invalid input")
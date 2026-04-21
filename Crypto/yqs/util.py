from hashlib import sha256
from random import randint


qbits = 77
ebits = 2
N = 77


def get_prime(n):
    def is_prime(num):
        if num < 2:
            return False
        if num in (2, 3):
            return True
        if num % 2 == 0:
            return False
        d = num - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1
        for _ in range(10):
            a = randint(2, num - 2)
            x = pow(a, d, num)
            if x == 1 or x == num - 1:
                continue
            for _ in range(s - 1):
                x = pow(x, 2, num)
                if x == num - 1:
                    break
            else:
                return False
        return True
    
    while True:
        num = randint(2 ** (n - 1), 2 ** n - 1)
        if num % 2 == 0:
            num += 1
        if is_prime(num):
            return num


def vec_dot(a, b, mod):
    result = 0
    for i in range(len(a)):
        result = (result + a[i] * b[i]) % mod
    return result


def vec_add(a, b, mod):
    return [(a[i] + b[i]) % mod for i in range(len(a))]


def vec_scalar_mul(v, scalar, mod):
    return [(v[i] * scalar) % mod for i in range(len(v))]


class LWE:
    def __init__(self):
        self.q = get_prime(qbits)
        self.e = (1 << ebits) - 1

        self.s = [randint(0, self.q - 1) for _ in range(N)]
    
    def _int_to_vec(self, m):
        coeffs = []
        for i in range(N):
            coeffs.append(m % self.q)
            m //= self.q
        return coeffs
    
    def _vec_to_int(self, v):
        result = 0
        for i in range(N):
            result += v[i] * (self.q ** i)
        return result
    
    def encrypt(self, m):
        m = m & ((1 << 8) - 1)
        
        m_encoded = m << ebits
        
        a = [randint(0, self.q - 1) for _ in range(N)]
        
        error = randint(0, self.e)
        
        b = (vec_dot(a, self.s, self.q) + m_encoded + error) % self.q
        
        return (self._vec_to_int(a), int(b))
    
    def decrypt(self, c):
        a_int, b = c
        a = self._int_to_vec(a_int)
        
        m_with_error = (b - vec_dot(a, self.s, self.q)) % self.q
        
        m_decoded = ((int(m_with_error) + (self.e // 2)) >> ebits) & ((1 << 8) - 1)
        
        return m_decoded
    
    def export_priv_key(self):
        return self._vec_to_int(self.s)


class ECC:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
    
    def add(self, A, B):
        if A is None:
            return B
        if B is None:
            return A
        
        x1, y1 = A
        x2, y2 = B
        
        if x1 == x2 and y1 == (-y2) % self.p:
            return None
        
        if A == B:
            m = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p) % self.p
        else:
            m = (y2 - y1) * pow(x2 - x1, -1, self.p) % self.p
        
        x3 = (m * m - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p
        
        return (x3, y3)
    
    def mul(self, A, x):
        result = None
        addend = A
        
        while x > 0:
            if x & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            x >>= 1
        
        return result
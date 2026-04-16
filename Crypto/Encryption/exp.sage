class AES():
    Rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

    def __init__(self, key: bytes, rounds: int = 10):
        self.rounds = rounds
        self.key = key
        self.S = [i for i in range(256)]
        self.S_inv = [i for i in range(256)]
        self.W = [list(key[i:i + 4]) for i in range(0, 16, 4)]
        self._key_expansion()

    def _xor(self, a, b=None):
        if b is None:
            assert len(a) > 0
            return a[0] ^^ self._xor(a[1:]) if len(a) > 1 else a[0]
        assert len(a) == len(b)
        return [x ^^ y for x, y in zip(a, b)]

    def _gmul(self, a, b):
        p = 0
        while b:
            if b & 1:
                p ^^= a
            a = a << 1
            if a >> 8:
                a ^^= 0b100011011
            b >>= 1
        return p

    def _multiply(self, a, b):
        return self._xor([self._gmul(x, y) for x, y in zip(a, b)])

    def _matrix_multiply(self, const, state):
        return [[self._multiply(const[i], [state[k][j] for k in range(4)]) for j in range(4)] for i in range(4)]

    def _permutation(self, lis, table):
        return [table[i] for i in lis]

    def _block_permutation(self, block, table):
        return [self._permutation(row, table) for row in block]

    def _left_shift(self, block, n):
        return block[n:] + block[:n]

    def _bytes_to_matrix(self, text: bytes) -> list[list[int]]:
        return [[text[j * 4 + i] for j in range(4)] for i in range(4)]

    def _matrix_to_bytes(self, block: list[list[int]]) -> bytes:
        return bytes([block[j][i] for i in range(4) for j in range(4)])

    def _T(self, w: list[int], n) -> list[int]:
        w = self._left_shift(w, 1)
        w = self._permutation(w, self.S)
        w[0] ^^= self.Rcon[n % 10]
        return w

    def _key_expansion(self):
        for i in range(4, (self.rounds + 1) * 4):
            if i % 4 == 0:
                self.W.append(self._xor(self.W[i - 4], self._T(self.W[i - 1], i // 4 - 1)))
            else:
                self.W.append(self._xor(self.W[i - 4], self.W[i - 1]))

    def _row_shift(self, block: list[list[int]]) -> list[list[int]]:
        return [self._left_shift(block[i], i) for i in range(4)]

    def _column_mix(self, block: list[list[int]]) -> list[list[int]]:
        return self._matrix_multiply([self._left_shift([2, 3, 1, 1], 4 - i) for i in range(4)], block)

    def _round_key_add(self, block: list[list[int]], key: list[list[int]]) -> list[list[int]]:
        return [self._xor(block[i], [key[j][i] for j in range(4)]) for i in range(4)]

    def _encrypt(self, block: list[list[int]]) -> list[list[int]]:
        block = self._round_key_add(block, self.W[:4])
        for i in range(1, self.rounds):
            block = self._block_permutation(block, self.S)
            block = self._row_shift(block)
            block = self._column_mix(block)
            block = self._round_key_add(block, self.W[i * 4:(i + 1) * 4])
        block = self._block_permutation(block, self.S)
        block = self._row_shift(block)
        block = self._round_key_add(block, self.W[-4:])
        return block

    def _inv_row_shift(self, block: list[list[int]]) -> list[list[int]]:
        return [self._left_shift(block[i], 4 - i) for i in range(4)]

    def _inv_column_mix(self, block: list[list[int]]) -> list[list[int]]:
        return self._matrix_multiply([self._left_shift([14, 11, 13, 0x9], 4 - i) for i in range(4)], block)

    def _decrypt(self, block: list[list[int]]) -> list[list[int]]:
        block = self._round_key_add(block, self.W[-4:])
        for i in range(self.rounds - 1, 0, -1):
            block = self._inv_row_shift(block)
            block = self._block_permutation(block, self.S_inv)
            block = self._round_key_add(block, self.W[i * 4:(i + 1) * 4])
            block = self._inv_column_mix(block)
        block = self._inv_row_shift(block)
        block = self._block_permutation(block, self.S_inv)
        block = self._round_key_add(block, self.W[:4])
        return block

    def encrypt(self, plaintext: bytes) -> bytes:
        assert len(plaintext) % 16 == 0, ValueError(f"Incorrect AES plaintext length ({len(plaintext)} bytes)")
        ciphertext = b''
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i + 16]
            block = self._bytes_to_matrix(block)
            block = self._encrypt(block)
            ciphertext += self._matrix_to_bytes(block)
        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
        assert len(ciphertext) % 16 == 0, ValueError(f"Incorrect AES ciphertext length ({len(ciphertext)} bytes)")
        plaintext = b''
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i + 16]
            block = self._bytes_to_matrix(block)
            block = self._decrypt(block)
            plaintext += self._matrix_to_bytes(block)
        return plaintext


def bytes2list(text: bytes) -> list[int]:
    return [int(b) for byte in text for b in f"{byte:08b}"]


def list2bytes(lis: list[int]) -> bytes:
    return bytes([int(''.join(str(b) for b in lis[i * 8:(i + 1) * 8]), 2) for i in range(len(lis) // 8)])


output_tmp = "ac7d094c73cec9b70d5bc43ebb7468908d5c286d52efe8962c7ae51f9a5549b1"
flag_tmp = "6b957921797a8a1169de6374e70cb95d"


cipher = AES(b"0" * 16, rounds=20)     # 变换矩阵T和key无关

# PT + b = C
# Calc T
zero_input = bytes(16)
zero_output = cipher.encrypt(zero_input)
b = bytes2list(zero_output[:16])

T = []

for i in range(128):
    tmp = [0] * 128
    tmp[i] = 1
    plaintext = list2bytes(tmp)
    ciphertext = cipher.encrypt(plaintext)
    ciphertext = bytes2list(ciphertext[:16])
    T_row = [(ciphertext[j] - b[j]) % 2 for j in range(128)]
    T.append(T_row)


F = GF(2)
T = Matrix(F, T)

# Calc b
inputs = b"1" * 16
outputs = bytes.fromhex(output_tmp)
inputs = vector(F, bytes2list(inputs))
outputs = vector(F, bytes2list(outputs[:16]))
b = outputs - inputs * T

# Verification
inputs = b"\x10" * 16
inputs = vector(F, bytes2list(inputs))
throry_outputs = inputs * T + b
outputs = bytes.fromhex(output_tmp)
outputs = vector(F, bytes2list(outputs[16:32]))
assert throry_outputs == outputs

# recover flag
for index in range(0, len(flag_tmp), 32):
    tmp = flag_tmp[index:index + 32]
    flag_ciphertext = bytes.fromhex(tmp)
    c = bytes2list(flag_ciphertext)
    c = vector(F, c)
    p = (c - b) * T^-1
    flag_blocks = list2bytes(p)
    print(flag_blocks, end="")

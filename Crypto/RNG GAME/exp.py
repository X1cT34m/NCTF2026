from pwn import *

# context(log_level = 'debug')

addr = "114.66.24.221:46749".split(':')
io = remote(addr[0], int(addr[1]), ssl=False)

io.recvuntil("Here is my seed: ")
seed = int(io.recvline().strip())
tmp = []
while seed:
    tmp.append(seed & 0xffffffff)
    seed >>= 32

for i in range(4):
    tmp.append(tmp[i] - 4)

seed2 = sum([tmp[i] << (32 * i) for i in range(8)])

io.recvuntil("Give me your seed: ")
io.sendline(str(seed2))

io.interactive()

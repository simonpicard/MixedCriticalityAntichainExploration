from TaskSet import *
from Task import *
import math
from functools import reduce

# Greatest common divisor of more than 2 numbers.  Am I terrible for doing it this way?


def gcd(numbers):
    """Return the greatest common divisor of the given integers"""
    from math import gcd

    return reduce(gcd, map(int, numbers))


# Least common multiple is not in standard libraries? It's in gmpy, but this is simple enough:


def lcm(numbers):
    """Return lowest common multiple."""

    def lcm(a, b):
        return (a * b) // gcd((a, b))

    return reduce(lcm, numbers, 1)


# Assuming numbers are positive integers...


class Greedy:
    def __init__(self, ts):
        self.ts = ts
        self.Dlo = [0] * ts.getSize()

    def test(self):
        return self.tuneDeadlines()

    def dbfLO(self, i, delta):
        res = delta - self.Dlo[i]
        res /= self.ts.getTask(i)["T"]
        res = math.floor(res)
        res += 1
        res *= self.ts.getTask(i)[1 - 1]
        return max(0, res)

    def full(self, i, delta):
        res = delta - (self.ts.getTask(i)["D"] - self.Dlo[i])
        res /= self.ts.getTask(i)["T"]
        res = math.floor(res)
        res += 1
        res *= self.ts.getTask(i)[2 - 1]
        return max(0, res)

    def done(self, i, delta):
        n = delta % self.ts.getTask(i)["T"]
        if self.ts.getTask(i)["D"] > n and n >= (self.ts.getTask(i)["D"] - self.Dlo[i]):
            res = self.ts.getTask(i)[1 - 1] - n + self.ts.getTask(i)["D"] - self.Dlo[i]
            return max(0, res)
        else:
            return 0

    def dbfHI(self, i, delta):
        return self.full(i, delta) - self.done(i, delta)

    def conditionA(self, delta):

        res = 0
        for i in range(self.ts.getSize()):
            res += self.dbfLO(i, delta)
        return res <= delta

    def conditionB(self, delta):
        res = 0
        for i in range(self.ts.getSize()):
            if self.ts.getTask(i)["X"] == 1:
                res += self.dbfHI(i, delta)
        return res <= delta

    def fLO(self, i):
        return (self.ts.getTask(i)[1 - 1], self.Dlo[i], self.ts.getTask(i)["T"])

    def fHI(self, i):
        return (
            self.ts.getTask(i)[2 - 1],
            self.ts.getTask(i)["D"] - self.Dlo[i],
            self.ts.getTask(i)["T"],
        )

    def getL(self, tasks):
        c = 0
        for t in tasks:
            c += t[0] / t[2]
        if c > 1:
            print("bizzare U", str(c), str(self.ts))
            return "échec"

        Ts = []
        Ds = []
        Cs = []
        for t in tasks:
            Ts.append(t[2])
            Ds.append(t[1])
            Cs.append(t[0])

        P = lcm(Ts)
        D = max(Ds)
        M = P + D
        if c == 1:
            T = M
        else:
            T = min(M, math.ceil(c / (1 - c)) * max(map(lambda x, y: x - y, Ts, Ds)))

        return T

    def nbToDlo(self, nb, Ds, base):

        res = list(base)
        for i in range(len(res) - 1):
            toDiv = reduce(lambda x, y: x * y, Ds[i + 1 :])
            div = nb // toDiv

            rem = nb % toDiv
            res[i] += div
            nb = rem

        res[-1] += nb
        return res

    def getLmax(self):
        res = 0
        Ds = self.ts.getD()
        Ds = list(map(lambda x, y: x + y, Ds, len(Ds) * [1]))
        base = len(Ds) * [0]
        size = len(Ds) * [0]

        for i in range(self.ts.getSize()):
            if self.ts.getTask(i)["X"] == 0:
                Ds[i] = 1
                base[i] = self.ts.getTask(i)["D"]
            else:
                Ds[i] -= self.ts.getTask(i)[1 - 1]
                base[i] = self.ts.getTask(i)[1 - 1]

        final = reduce(lambda x, y: x * y, Ds)
        current = 0

        while current < final:

            self.Dlo = self.nbToDlo(current, Ds, base)

            tLO = []
            for i in range(self.ts.getSize()):
                tLO.append(self.fLO(i))
            lLO = self.getL(tLO)

            tHI = []
            for i in range(self.ts.getSize()):
                if self.ts.getTask(i)["X"] == 1:
                    tHI.append(self.fHI(i))
            lHI = self.getL(tHI)

            if lHI == "échec" or lLO == "échec":
                return "échec"

            res = max(res, lHI, lLO)

            current += 1

        return res

    def tuneDeadlines(self):
        self.Dlo = self.ts.getD()

        candidates = []
        for i in range(self.ts.getSize()):
            if (
                self.ts.getTask(i)["X"] == 1
                and self.ts.getTask(i)["D"] > self.ts.getTask(i)[1 - 1]
            ):
                candidates.append(i)

        mod = "échec"

        Lmax = self.getLmax()

        if Lmax == "échec":
            return False
        assert Lmax == int(Lmax)
        Lmax = int(Lmax)

        while True:
            final = True
            for L in range(Lmax + 1):
                if not self.conditionA(L):
                    if mod == "échec":
                        return False
                    self.Dlo[mod] += 1
                    try:
                        candidates.remove(mod)
                    except:
                        pass
                    mod = "échec"
                    final = False
                elif not self.conditionB(L):
                    if len(candidates) == 0:
                        return False
                    argmax = 0
                    imax = None
                    for i in candidates:
                        current = self.dbfHI(i, L) - self.dbfHI(i, L - 1)
                        if current > argmax or imax == None:
                            argmax = current
                            imax = i
                    mod = imax

                    self.Dlo[mod] -= 1
                    if self.Dlo[mod] == self.ts[mod][1 - 1]:
                        candidates.remove(mod)
                    final = False
                    break
            if final:
                return True


# ts = TaskSet([Task(0, 36, 36, 2, [10, 20]), Task(0, 17, 17, 1, [9, 9]), Task(0, 28, 28, 2, [4, 8])])
# o = Greedy(ts)
# print(o.test())

import math
from TaskSet import *
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


class OCBP:
    def __init__(self, ts):
        self.tasks = ts

    def getLoad(self, X):
        pass

    def getDemandBound(self, task, t, X):
        return max(
            0,
            (math.floor((t - self.tasks[task]["D"]) / self.tasks[task]["T"]) + 1)
            * self.tasks[task][X],
        )

    def getSumDBF(self, t, X):
        res = 0
        for task in range(self.tasks.getSize()):
            if self.tasks[task]["X"] >= X:
                res += self.getDemandBound(task, t, X)
        res /= t
        return res

    def getHyperPeriod(self):
        return lcm(self.tasks.getT())

    def getNextLoadTry(self, counter):
        instant = 0
        task = None
        for i in range(self.tasks.getSize()):
            current = self.tasks[i]["D"] + counter[i] * self.tasks[i]["T"]
            if current < instant or task == None:
                instant = current
                task = i
        return instant, task

    def getExactLoad(self, X):
        HP = self.getHyperPeriod()
        counter = [0] * self.tasks.getSize()

        instant = 0

        load = 0

        while instant < HP:

            instant, task = self.getNextLoadTry(counter)
            counter[task] += 1
            currentLoad = self.getSumDBF(instant, X)
            if currentLoad > load:
                load = currentLoad

        return load

    def test(self):
        return self.getExactLoad(1) ** 2 + self.getExactLoad(0) <= 1


"""
ts = TaskSet([Task(0, 2, 2, 1, [1,1]), Task(0, 10, 10, 2, [1,2]), Task(0, 100, 100, 2, [20,20])])
o = OCBP(ts)
print(o.test())"""

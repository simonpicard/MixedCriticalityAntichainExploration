from Task import *
from TaskSet import *
from math import ceil


class Vestal:
    def __init__(self, ts):
        self.ts = ts
        self.prio = [0] * ts.getSize()

    def getWorstResponseTimeStep(self, i, r):
        res = 0
        for j in range(self.ts.getSize()):
            if True:
                if self.prio[j] <= self.prio[i]:
                    interference = (
                        ceil(r / self.ts.getTask(j)["T"])
                    ) * self.ts.getTask(j)[self.ts.getTask(i)["X"]]
                    res += interference
        return res

    def testPriority(self, i, p):
        initialPriority = self.prio[i]
        self.prio[i] = p
        current = self.ts.getWorstC(i)
        new = None

        while True:
            new = self.getWorstResponseTimeStep(i, current)
            if new > self.ts.getTask(i)["D"]:
                self.prio[i] = initialPriority
                # print(i, 'fail', new)
                return False
            if current == new:
                # print(i, 'success', new)
                return True
            current = new

    def assign(self):
        lowestPriority = self.ts.getSize() - 1
        notAssigned = list(range(self.ts.getSize()))

        while lowestPriority >= 0:
            # print("lel", lowestPriority)
            found = False
            assigned = None
            for i in notAssigned:
                isEligible = self.testPriority(i, lowestPriority)
                if isEligible:
                    # priority already assigned
                    assigned = i
                    found = True
                    break
            if found:
                notAssigned.remove(assigned)
                lowestPriority -= 1
            else:
                break

        if lowestPriority < 0:
            return True
        else:
            return False

    def test(self):
        return self.assign()


"""
ts = TaskSet([Task(0, 2, 2, 1, [1,1]), Task(0, 10, 10, 2, [1,3]), Task(0, 100, 100, 2, [20,20])])
v = Vestal(ts)
print(v.test())"""

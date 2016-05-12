
import math
from functools import reduce

# Greatest common divisor of more than 2 numbers.  Am I terrible for doing it this way?

def gcd(numbers):
    """Return the greatest common divisor of the given integers"""
    from fractions import gcd
    return reduce(gcd, numbers)

# Least common multiple is not in standard libraries? It's in gmpy, but this is simple enough:

def lcm(numbers):
    """Return lowest common multiple."""    
    def lcm(a, b):
        return (a * b) // gcd((a, b))
    return reduce(lcm, numbers, 1)

# Assuming numbers are positive integers...


class LPA:
    def __init__(self, ts):
        self.tasks = ts
        self.instance = []
        self.nbJobs =  [0]*ts.getSize()
        self.Ld = [0]*(ts.getK()+1)

    def getBusyPeriod(self):
        res = self.computeGamma(self.tasks.getK())
        #print(res)
        return res

    def testPriority(self, i, p):
        res = 0
        for j in range(self.tasks.getSize()):
            task = self.tasks[j]
            res += self.nbJobs[j]*task.C[self.tasks[self.instance[i]].X-1]

        rhs = (self.nbJobs[self.instance[i]]-1)*self.tasks[self.instance[i]].T+self.tasks[self.instance[i]].D
        return res <= rhs

    def assign(self):
        lowestPriority = len(self.instance)-1
        notAssigned = list(range(len(self.instance)))


        while lowestPriority >= 0:
            #print(self.nbJobs, lowestPriority)
            found = False
            assigned = None
            for i in notAssigned:
                isEligible = self.testPriority(i, lowestPriority)
                if isEligible:
                    #priority already assigned
                    self.nbJobs[self.instance[i]] -= 1
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

    def initAssign(self):
        BP = self.getBusyPeriod()
        if BP == "échec":
            return False
        for i in range(self.tasks.getSize()):
            task = self.tasks[i]
            nbjobsPerTask = task.generateJobForItv(BP)
            for j in range(nbjobsPerTask):
                self.instance.append(i)
            self.nbJobs[i] = nbjobsPerTask
        return(self.assign())


    def computeGamma(self, X):
        if X == 0:
            return 0.0
            
        ld = self.computeGamma(X-1)
        if ld == ("échec"):
            return "échec"

        sumCHigherX = 0.0
        sumConTHigherX = 0.0
        for i in range(self.tasks.getSize()):
            if self.tasks[i].X >= X:
                sumCHigherX += self.tasks[i].C[X-1]
                sumConTHigherX += (self.tasks[i].C[X-1]*1.0)/self.tasks[i].T

        gamma = (ld+sumCHigherX)
        if 1-sumConTHigherX <0.00000001:
            return ("échec")
        gamma /= (1.0-sumConTHigherX)

        returnSum = 0.0
        for i in range(self.tasks.getSize()):
            if self.tasks[i].X == X:
                returnSum += self.tasks[i].C[X-1]*(1+math.floor(gamma/self.tasks[i].T))
        res = self.Ld[X-1] + returnSum
        self.Ld[X] = res
        return res

    def test(self):
        return self.initAssign()

"""
ts = TaskSet([Task(0, 10, 10, 1, (1, 1)), Task(0, 10, 10, 2, (4, 8)), Task(0, 9, 9, 1, (3, 3)), Task(0, 6, 6, 1, (1, 1))])
o = LPA(ts)
print(o.test())
"""

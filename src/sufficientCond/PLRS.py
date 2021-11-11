
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


class PLRS:
    def __init__(self, ts):
        self.tasks = ts
        self.instance = []
        self.nbJobs =  [0]*ts.getSize()



    def getLoad(self, X):
        pass

    def getDemandBound(self, task, t, X):
        return max(0, (math.floor((t-self.tasks[task].D)/self.tasks[task].T)+1)*self.tasks[task].C[X-1])

    def getSumDBF(self, t, X):
        res = 0
        for task in range(self.tasks.getSize()):
            if self.tasks[task].X >= X:
                res += self.getDemandBound(task, t, X)
        res /= t
        return res



    def getHyperPeriod(self):
        return lcm(self.tasks.getT())

    def getNextLoadTry(self, counter):
        instant = 0
        task = None
        for i in range(self.tasks.getSize()):
            current = self.tasks[i].D + counter[i]*self.tasks[i].T
            if current < instant or task == None:
                instant = current
                task = i
        return instant, task


    def getExactLoad(self, X):
        HP = self.getHyperPeriod()
        counter = [0]*self.tasks.getSize()

        instant = 0

        load = 0

        while (instant < HP):

            instant, task = self.getNextLoadTry(counter)
            counter[task] += 1
            currentLoad = self.getSumDBF(instant, X)
            if currentLoad > load:
                load = currentLoad

        return load

    def getBusyPeriod(self):
        dmax = max(self.tasks.getD())

        exactLoad1 = self.getExactLoad(1)
        exactLoad2 = self.getExactLoad(2)
        
        if 1-exactLoad1 < 0.00000001 or 1-exactLoad2 < 0.00000001 :
            return "échec"

        x1 = (exactLoad1/(1-exactLoad1))*dmax
        x2 = (exactLoad2/((1-exactLoad1)*(1-exactLoad2)))*dmax
        return x1+x2

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
        #print(BP)
        for i in range(self.tasks.getSize()):
            task = self.tasks[i]
            nbjobsPerTask = task.generateJobForItv(BP)
            for j in range(nbjobsPerTask):
                self.instance.append(i)
            self.nbJobs[i] = nbjobsPerTask
        return(self.assign())

    def test(self):
        return self.initAssign()


"""
ts = TaskSet([Task(0, 15,15, 2, [8,14]), Task(0, 80, 80, 1, [9,9])])
o = PLRS(ts)
print(o.test())"""


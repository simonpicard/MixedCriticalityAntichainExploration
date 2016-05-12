from Task import *
from TaskSet import *
from math import ceil, floor

class AMCmax:
    def __init__(self, ts):
        self.ts = ts
        self.prio = [0 for i in range(ts.getSize())]

    def getWorstResponseTimeStep(self, i, r, l):
        res = self.ts.getTask(i).getWorstC()
        for j in range(self.ts.getSize()):
            if self.ts.getTask(j).X >= l:
                if self.prio[j] < self.prio[i]:
                    interference = (ceil(r/self.ts.getTask(j).T))*self.ts.getTask(j).C[l-1]
                    res += interference
        return res

    def getLoInterference(self, i, s):
        res = 0
        for j in range(self.ts.getSize()):
            if self.ts.getTask(j).X == 1:
                if self.prio[j] < self.prio[i]:
                    interference = ((floor(s/self.ts.getTask(j).T))+1)*self.ts.getTask(j).C[1-1]
                    res += interference
        return res

    def getMaxGeneration(self, k, t, s):
        res1 = ceil(t/self.ts.getTask(k).T)
        res2 = ceil((t-s-(self.ts.getTask(k).T - self.ts.getTask(k).D))/self.ts.getTask(k).T)+1
        return min(res1, res2)

    def getHiInterference(self, i, t, s):
        res = 0
        for j in range(self.ts.getSize()):
            if self.ts.getTask(j).X >= 2:
                if self.prio[j] < self.prio[i]:
                    Mstk = self.getMaxGeneration(j, t, s)

                    interference = Mstk*self.ts.getTask(j).C[2-1]
                    interference += (ceil(t/self.ts.getTask(j).T) - Mstk)*self.ts.getTask(j).C[1-1]

                    res += interference
        return res


    def getResponseTimeSwitchStep(self, i, r, s):
        res = self.ts.getTask(i).C[2-1]
        res += self.getLoInterference(i, s)
        res += self.getHiInterference(i, r, s)
        return res

    def isALoGenerationPoint(self, s):
        for i in range(self.ts.getSize()):
            task = self.ts.getTask(i)
            if task.X == 1:
                if s%task.T == 0:
                    return True
        return False

    def testPriority(self, i, p):
        initialPriority = self.prio[i]
        self.prio[i] = p
        current = 0
        new = None


        while (True):
            new = self.getWorstResponseTimeStep(i, current, 1)

            if new > self.ts.getTask(i).D:
                self.prio[i]=initialPriority
                return False
            if current == new:
                break
            current = new

        if self.ts.getTask(i).X == 1 :
            return True

        riLO = current

        

        current = 0
        new = None
        while (True):
            new = self.getWorstResponseTimeStep(i, current, 2)
            if new > self.ts.getTask(i).D:
                self.prio[i]=initialPriority
                return False
            if current == new:
                break
            current = new

        
        for s in range(riLO):
            if self.isALoGenerationPoint(s):
                current = 0
                new = None
                while (True):
                    new = self.getResponseTimeSwitchStep(i, current, s)
                    if new > self.ts.getTask(i).D:
                        self.prio[i]=initialPriority
                        return False
                    if current == new:
                        break
                    current = new
        return True


    def assign(self):
        lowestPriority = self.ts.getSize()-1
        notAssigned = list(range(self.ts.getSize()))

        while lowestPriority > 0:
            #print(lowestPriority)
            found = False
            assigned = None
            for i in notAssigned:
                isEligible = self.testPriority(i, lowestPriority)
                if isEligible:
                    #priority already assigned
                    assigned = i
                    found = True
                    break
            if found:
                notAssigned.remove(assigned)
                lowestPriority -= 1
            else:
                break

        if lowestPriority == 0:
            return True
        else:
            return False

    def test(self):
        return self.assign()


"""
ts = TaskSet([Task(0, 2, 2, 1, [1,1]), Task(0, 10, 10, 2, [1,7]), Task(0, 100, 100, 2, [20,20])])
v = AMCmax(ts, 2)
print(v.test())"""
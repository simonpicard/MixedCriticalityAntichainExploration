from SporadicSystemState import SystemState
from Task import *
from TaskSet import *
from Scheduler import *
from itertools import *
from SporadicMaxSet import MaxSet


IDLE = 0
IDLEandWC = 1
WC = 2
NONE = 3
LAX = 4
WCnat = 5

EDFVD = 0
LWLF = 1


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


class SporadicGraph:
    def __init__(self, taskSet, sim, sched = EDFVD):
        self.taskSet = taskSet
        self.maxO = taskSet.getMaxO()
        self.maxT = taskSet.getMaxT()
        self.maxC = taskSet.getMaxC()
        self.K = taskSet.getK()
        self.size = taskSet.getSize()
        self.nbVisitedInter = 0
        self.nbVisited = 0
        self.scheduler = Scheduler(taskSet, sched)
        self.SIM = sim

    def setSim(self, sim):
        self.SIM = sim

    def getInitialVertex(self):
        rct0 = tuple([0]*self.size)
        at0 = tuple(self.taskSet.getO())
        done0 = tuple([True]*self.size)
        crit0 = 1
        hashInfo = (self.taskSet.getD(), self.taskSet.getT(), self.taskSet.getMaxCs(), self.taskSet.getK())
        v0 = SystemState(at0, rct0, done0, crit0, self.SIM, hashInfo)
        return v0

    def isStateOK(self, ss):
        if ss.crit < 0 or ss.crit > self.K:
            print(ss.crit)
            return False
        for i in range(self.size):
            if ss.rct[i] < 0 or ss.rct[i] > self.taskSet.getTask(i).C[self.K-1]:
                print(ss.rct[i], i)
                return False
            if ss.nat[i] > self.taskSet.getTask(i).T:
                print(ss.nat[i], i)
                return False
        '''for t in ss.getLaxity(self.taskSet.getD):
            if t < -1:
                return False'''
        return True


    def getNeighbour(self, ss):
        neighbours = []
        run = self.scheduler.run(ss)

        ssP = ss.getExecutionTransition(run, self.taskSet.getX())
        self.nbVisitedInter+=1
        
        ssPPs = []
        for combination in powerset(run):
            current = ssP.getTerminationTransition(set(combination), self.taskSet.getX(), self.taskSet.getC())
            ssPPs.append(current)
            self.nbVisitedInter+=1

        ssPPPs = []
        for ssPP in ssPPs:
            ssPPP = ssPP.getCriticalTransition(self.taskSet.getX(), self.taskSet.getC())
            ssPPPs.append(ssPPP)
            self.nbVisitedInter+=1

        for ssPPP in ssPPPs:
            for combination in powerset(ssPPP.getEligible(self.taskSet.getX())):
                neighbours+= ssPPP.getRequestTransition(combination, self.taskSet.getC())
                self.nbVisitedInter+=1

        return neighbours

    def bfsMax(self):
        self.nbVisitedInter = 0
        queue = [self.getInitialVertex()]
        visited = MaxSet(self.SIM)
        while queue:
            vertex = queue.pop(0)

            isNotInSet = visited.add(vertex)
            
            if isNotInSet :
                self.nbVisited += 1
                if (vertex.isFail(self.taskSet.getC())):
                    #print(self.nbVisitedInter, len(visited), visited.size)
                    #print(vertex)
                    #print("FAIL")
                    return False, self.nbVisitedInter, self.nbVisited, visited.size, len(visited.set)
                queue.extend(self.getNeighbour(vertex))
        return True, self.nbVisitedInter, self.nbVisited, visited.size, len(visited.set)


    def test(self):
        return self.bfsMax()[0]

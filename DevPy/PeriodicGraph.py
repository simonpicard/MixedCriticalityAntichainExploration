from Task import *
from TaskSet import *
from Scheduler import *
from itertools import *
from PeriodicSystemState import SystemState


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


EDFVD = 0
LWLF = 1

class PeriodicGraph:
    def __init__(self, taskSet, sched = EDFVD):
        self.taskSet = taskSet
        self.maxO = taskSet.getMaxO()
        self.maxT = taskSet.getMaxT()
        self.maxC = taskSet.getMaxC()
        self.K = taskSet.getK()
        self.size = taskSet.getSize()
        self.nbVisited = 0
        self.nbInterVisited = 0
        self.scheduler = Scheduler(taskSet, sched)
        self.visited = set()

    def getInitialVertex(self):
        rct0 = []
        at0 = []
        crit0 = 1
        for i in range(self.size):
            at0.append(self.taskSet.getTask(i).O)
            rct0.append(self.taskSet.getTask(i).C[0])
        hashInfo = (self.taskSet.getD(), self.taskSet.getT(), self.taskSet.getMaxCs(), self.taskSet.getK())
        v0 = SystemState(at0, rct0, crit0, hashInfo)
        return v0

    def isStateOK(self, ss):
        if ss.crit < 0 or ss.crit > self.K:
            print(ss.crit)
            print("crit")
            return False

        for i in range(self.size):
            if ss.rct[i] < 0 or ss.rct[i] > self.taskSet.getTask(i).C[self.K-1]:
                print(ss.rct[i], i)
                print("rct")
                return False
            if ss.at[i] > self.taskSet.getTask(i).T:
                print(ss.at[i], i)
                print("at")
                return False
        '''for t in ss.getLaxity(self.taskSet.getD):
            if t < -1:
                return False'''
        return True


    def getNeighbour(self, ss):
        neighbours = []
        run = self.scheduler.run(ss)
        ssP = ss.getExecutionTransition(run, self.taskSet.getX())

        self.nbInterVisited += 1


        ssPPs = []
        for combination in powerset(run):
            current = ssP.getTerminationTransition(set(combination), self.taskSet.getX(), self.taskSet.getC(), self.taskSet.getT())
            ssPPs.append(current)
            self.nbInterVisited += 1

        for ssPP in ssPPs:
            ssPPP = ssPP.getCriticalTransition(self.taskSet.getX(), self.taskSet.getC())
            neighbours.append(ssPPP)
            self.nbInterVisited += 1

        return neighbours

    def bfs(self):
        queue = [self.getInitialVertex()]
        visited = set()
        while queue:
            vertex = queue.pop(0)

            if not vertex in visited:
                visited.add(vertex)
                self.nbVisited+=1
                if (vertex.isFail(self.taskSet.getD())):
                    #print(vertex)
                    #print("FAIL")
                    return False, self.nbInterVisited, self.nbVisited, self.nbVisited, self.nbVisited
                queue.extend(set(self.getNeighbour(vertex)))

        return True, self.nbInterVisited, self.nbVisited, self.nbVisited, self.nbVisited

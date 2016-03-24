import sys

sys.path.append("C:/Users/Simon/Desktop/Cours/MA2/Thesis/MixedCriticalityAntichainExploration/DevPy")

from SystemState import *
from Task import *
from TaskSet import *
from igraph import * 
from Scheduler import *
from itertools import *
import numpy as np


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


class GraphMC:
    def __init__(self, taskSet):
        self.taskSet = taskSet
        self.maxO = taskSet.getMaxO()
        self.maxT = taskSet.getMaxT()
        self.maxC = taskSet.getMaxC()
        self.K = taskSet.getK()
        self.size = taskSet.getSize()
        self.g = Graph()
        self.lol = 0
        self.scheduler = Scheduler(taskSet)
        self.visited = set()


    def generateVertices(self):
        #rct, at, crit

        start = [0, self.maxO+self.maxT, 0]
        end = [self.maxC+1, -99999999, self.K+1]
        step = [1,-1,1]
        nb = [self.size, self.size, 1]
        res = []
        i = 0
        self.generateRec(start, end, step, nb, res, i)



    def generateRec(self, start, end, step, nb, res, i):
        #rct, at, crit
        if nb[i] == 0:
            if i >= self.size -1:
                at, rct, crit = res[0*self.size:1*self.size], res[1*self.size:2*self.size], res[2*self.size:3*self.size]
                st = SystemState(at, rct, crit)
                self.g.add_vertex({"sytemState":st})
            else:
                self.generateRec(start, end, step, nb, res, i+1)
        else:
            nb[i]-=1

            for j in range(start[i], end[i], step[i]):
                if i == 1:
                    it = self.size-(nb[i]+1)
                    rcti = res[it]
                    ati = j
                    Di = self.taskSet.getTask(it).D
                    if  ati - rcti + Di < -1:
                        break
                self.generateRec(start, end, step, nb, res+[j], i)
                if i == 0 and nb[i] == self.size-2:
                    print (self.lol, )
                    self.lol += 1 

            nb[i]+=1

    def getInitialVertex(self):
        rct0 = tuple([0]*self.size)
        at0 = tuple([0]*self.size)
        done0 = tuple([True]*self.size)
        crit0 = 1
        hashInfo = (self.taskSet.getD(), self.taskSet.getT(), self.taskSet.getMaxCs(), self.taskSet.getK())
        v0 = SystemState(at0, rct0, done0, crit0, hashInfo)
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
        if not self.isStateOK(ssP):
            return neighbours
        ssPPs = []
        for combination in powerset(run):
            current = ssP.getTerminationTransition(set(combination), self.taskSet.getX(), self.taskSet.getC(), self.taskSet.getT())
            if self.isStateOK(current):
                ssPPs.append(current)
        ssPPPs = []
        for ssPP in ssPPs:
            ssPPP = ssPP.getCriticalTransition(self.taskSet.getX(), self.taskSet.getC())

            if self.isStateOK(ssPPP):
                ssPPPs.append(ssPPP)
        for ssPPP in ssPPPs:
            for combination in powerset(ssPPP.getEligible(self.taskSet.getX())):
                neighbours+= ssPPP.getRequestTransition(combination, self.taskSet.getC(), self.taskSet.getT())
        return neighbours

    def bfs(self, start):
        queue = [start]
        visited = set()
        while queue:
            self.lol+=1
            print(self.lol)
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                if (vertex.isFail(self.taskSet.getD(), self.taskSet.getT())):
                    print(vertex)
                    print("FAIL")
                    return False
                queue.extend(set(self.getNeighbour(vertex)) - visited)
        return True

    def bfsAC(self, start):
        queue = [start]
        visited = set()
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                self.lol+=1
                toRemove = set()
                for elem in visited:
                    if vertex.isIdleSimulation(elem):
                        toRemove.add(elem)
                visited = visited - toRemove
                #print(len(toRemove))
                visited.add(vertex)
                print(self.lol, len(visited), self.lol-len(visited))
                if (vertex.isFail(self.taskSet.getD(), self.taskSet.getT())):
                    print(vertex)
                    print("FAIL")
                    return False
                toAdd = set(self.getNeighbour(vertex)) - visited
                toRemove = set()
                removed = 0
                for ss1 in toAdd:
                    simulated = False
                    for ss2 in visited:
                        if ss2.isIdleSimulation(ss1):
                            toRemove.add(ss1)
                            removed+=1
                            simulated = True
                            break
                    if not simulated:
                        for ss2 in queue:
                            if ss2.isIdleSimulation(ss1):
                                toRemove.add(ss1)
                                removed+=1
                                #simulated = True
                                break
                toAdd = toAdd - toRemove
                toRemove = []
                for i in range(len(queue)):
                    for ss in toAdd:
                        if ss.isIdleSimulation(queue[i]):
                            toRemove.append(i)
                            removed+=1
                            break
                toRemove.sort(reverse=True)
                for i in toRemove:
                    queue.pop(i)
                queue.extend(toAdd)
                #print(removed)

        return True



t1a = Task(0,50,50,1,[30,30])
t2a = Task(0,100,100,2,[10,96])

t1 = Task(0,10,10,1,[1,1])
t2 = Task(0,20,20,2,[1,2])
t3 = Task(0,30,30,1,[15,15])
t4 = Task(0,50,50,2,[15,25])
ts = TaskSet([t1,t2, t3, t4])
ts = TaskSet([t1a,t2a])


gmc = GraphMC(ts)
gmc.bfs(gmc.getInitialVertex())
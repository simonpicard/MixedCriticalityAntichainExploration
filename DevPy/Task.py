from Job import *


class Task:
    def __init__(self, O, T, D, X, C):
        self.O = O
        self.T = T
        self.D = D
        self.X = X
        self.C = tuple(C)


    def getUtilisation(self, l):
        return self.C[l-1]/self.T

    def getWorstC(self):
        return self.C[self.X-1]

    def __repr__(self):
        return "Task("+str(self.O)+", "+str(self.T)+", "+str(self.D)+", "+str(self.X)+", "+str(self.C)+")"

    def generateJobForItv(self, itv):
        nb = 0
        while itv >= 0:
            itv -= self.T
            nb += 1
        return nb

    def __hash__(self):
        return hash((self.O, self.T, self.D, self.X, self.C))

    def __eq__(self, other):
        return self.O == other.O and self.T == other.T and self.D == other.D and self.X == other.X and self.C == other.C

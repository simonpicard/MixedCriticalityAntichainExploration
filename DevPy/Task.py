


class Task:
    def __init__(self, O, T, D, X, C):
        self.O = O
        self.T = T
        self.D = D
        self.X = X
        self.C = C


    def getUtilisation(self, l):
        return self.C[l-1]/self.T
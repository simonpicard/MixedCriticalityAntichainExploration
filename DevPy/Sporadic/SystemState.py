



class SystemState:
    def __init__(self, nat, rct, done, crit, hashInfo):
        self.nat = nat
        self.rct = rct
        self.done = done
        self.crit = crit
        self.hashInfo = hashInfo

    def getActive(self):
        res = []
        for i in range(len(self.nat)):
            if not self.done[i]:
                res.append(i)
        return res

    def getCrit(self):
        for it in self.getActive():
            if self.rct[it] == 0:
                return self.crit+1
        return self.crit

    def getLaxity(self, D, T):
        laxity = []
        for i in range(len(self.nat)):
           laxity.append(self.nat[i]-self.rct[i]+D[i]-T[i])
        return laxity

    def isFail(self, D, T):
        laxity = self.getLaxity(D, T)
        for t in laxity:
            if t < 0:
                return True
        return False

    def getImplicitelyDone(self, X):
        res = []
        for i in self.getActive():
            if self.rct[i] == 0 and self.crit == X[i]:
                res.append(i)
        return res

    def getEligible(self, X):
        res = []
        for i in range(len(self.nat)):
            if self.crit <= X[i] and self.done[i] and self.nat[i] <= 0:
                res.append(i)
        return res

    def getExecutionTransition(self, run, X):
        critP = self.crit
        doneP = list(self.done)
        rctP = list(self.rct)
        for i in run:
            rctP[i]-=1
        natP = list(self.nat)
        for i in range(len(self.nat)):
            if not self.done[i]:
                natP[i] -= 1
            else:
                natP[i] = max(0, self.nat[i]-1)


        return SystemState(natP, rctP, doneP, critP, self.hashInfo)

    def getTerminationTransition(self, toTerminate, X, C, T):
        critP = self.crit
        toTerminate = toTerminate.union(self.getImplicitelyDone(X))
        rctP = list(self.rct)
        natP = list(self.nat)
        doneP = list(self.done)
        for i in toTerminate:
            rctP[i] = 0
            doneP[i] = True
        return SystemState(natP, rctP, doneP, critP, self.hashInfo)

    def getCriticalTransition(self, X, C):
        critP = self.getCrit()
        rctP = list(self.rct)
        natP = list(self.nat)
        doneP = list(self.done)
        for i in range(len(self.nat)):
            if X[i] >= self.getCrit():
                if not self.done[i]:
                    rctP[i] += C[i][self.getCrit()-1]-C[i][self.crit-1]
            else:
                rctP[i] = 0
                natP[i] = 0
                doneP[i] = True
        return SystemState(natP, rctP, doneP, critP, self.hashInfo)

    def getRequestTransition(self, request, C, T):
        res = []
        critP = self.getCrit()
        rctP = list(self.rct)
        natP = list(self.nat)
        doneP = list(self.done)
        for it in request:
            rctP[it]=C[it][self.crit-1]
            doneP[it] = False
        size = []
        toCombinate = []
        nbCombinaison = 1
        for it in request:
            toCombinate.append(range(natP[it]+T[it], T[it]+1))
            size.append(len(toCombinate[-1]))
            nbCombinaison *= size[-1]
        for i in range(nbCombinaison):
            for j in range(len(request)):
                div = 1
                for k in range(j+1, len(request)):
                    div *=size[k]
                mod = size[j]
                natP[request[j]] = toCombinate[j][(i//div)%mod]
            res.append(SystemState(list(natP), list(rctP), list(doneP), critP, self.hashInfo))
        return res


    def getRelativeDeadline(self, D, T, i):
        return self.nat[i]-T+D

    def isIdleSimulation(self, ss):
        res = True
        if not (self.crit == ss.crit and self.done == ss.done and self.rct == ss.rct):
            return False
        for i in range(len(self.rct)):
            if self.done[i]:
                if not (self.nat[i] <= ss.nat[i]):
                    return False
            else:
                if not (self.nat[i] == ss.nat[i]):
                    return False
        return True



    def __repr__(self):
        return("SS#"+str(hash(self))+"\n nat :"+str(self.nat)+"\n rct :"+str(self.rct)+"\n done :"+str(self.done)+"\n crit :"+str(self.crit))

    def __eq__(self, other):
        return (self.nat == other.nat and self.rct == other.rct and self.crit == other.crit and self.done == self.done)
        #return not self.isIdleSimulation(other)

    def __hash__(self):
        #hashinfo = D, T, Cmax, K
        D = self.hashInfo[0]
        T = self.hashInfo[1]
        Cmax = self.hashInfo[2]
        K = self.hashInfo[3]
        #T-(D+1) <= nat <= T
        #0 <= nat+D+1-T <= D+1
        #0 <= rct <= Cmax
        #1 <= crit <= K
        #0 <= crit-1 <= K-1
        #0 <= done <= 1
        h = 0

        h = self.crit-1
        factor = K-1+1
        for i in range(len(self.nat)):
            h += self.rct[i]*factor
            factor*=(Cmax[i]+1)
            h += (self.nat[i]+D[i]+1-T[i])*factor
            factor*=((D[i]+1)+1)
            h+= int(self.done[i])*factor
            factor*=(2)
        return h



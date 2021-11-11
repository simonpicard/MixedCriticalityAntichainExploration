from functools import reduce


IDLE = 0
IDLEandWC = 1
WC = 2
NONE = 3
LAX = 4
WCnat = 5

class MaxSet:
    def __init__(self, sim):
        self.set = dict()
        self.size = 0
        self.SIM = sim

    def add(self, ss):
        if self.SIM == IDLE:
            return self.addIdle(ss)
        elif self.SIM == IDLEandWC:
            return  self.addIdleWC(ss)
        elif self.SIM == WC:
            return  self.addWC(ss)
        elif self.SIM == NONE:
            return  self.addNONE(ss)
        elif self.SIM == LAX:
            return self.addLax(ss)
        elif self.SIM == WCnat:
            return  self.addWCnat(ss)


    def addIdleWC(self, ss):
        h = hash(ss)
        new = ss.getRelevantAttributeIdleWC()
        try:
            currents = self.set[h]
        except KeyError:
            self.set[h] = set()
            self.set[h].add(new)
            self.size += 1
            return True
        else:
            toReplace = []
            for current in currents:
                resIdle = map(int.__le__, current[0], new[0])
                resWC = map(int.__ge__, current[1], new[1])
                CurrentSimuleNew = all(list(resIdle)+list(resWC))
                
                if CurrentSimuleNew:
                    return False

                resIdle = map(int.__le__, new[0], current[0])
                resWC = map(int.__ge__, new[1], current[1])
                newSimuleCurrent = all(list(resIdle)+list(resWC))

                if newSimuleCurrent:
                    toReplace.append(current)

            if len(toReplace) > 0:
                    for toRemove in toReplace:
                        self.set[h].discard(toRemove)
                        self.size -= 1
                    self.set[h].add(new)
                    self.size += 1
                    return True

            else:
                self.set[h].add(new)
                self.size += 1
                return True


    def addIdle(self, ss):
        h = hash(ss)
        new = ss.getRelevantAttributeIdle()
        try:
            currents = self.set[h]
        except KeyError:
            self.set[h] = set()
            self.set[h].add(new)
            self.size += 1
            return True
        else:
            toReplace = []
            for current in currents:
                resIdle = map(int.__le__, current, new)
                CurrentSimuleNew = all(resIdle)

                if CurrentSimuleNew:
                    return False

                resIdle = map(int.__le__, new, current)
                newSimuleCurrent = all(resIdle)

                if newSimuleCurrent:
                    toReplace.append(current)

            if len(toReplace) > 0:
                    for toRemove in toReplace:
                        self.set[h].discard(toRemove)
                        self.size -= 1
                    self.set[h].add(new)
                    self.size += 1
                    return True

            else:
                self.set[h].add(new)
                self.size += 1
                return True


    def addWCnat(self, ss):
        h = hash(ss)
        new = ss.getRelevantAttributeWCnatRun()
        try:
            currents = self.set[h]
        except KeyError:
            self.set[h] = set()
            self.set[h].add(new)
            self.size += 1
            return True
        else:
            toReplace = []
            for current in currents:
                resWCnat = map(int.__le__, current, new)
                CurrentSimuleNew = all(resWCnat)

                if CurrentSimuleNew:
                    return False

                resWCnat = map(int.__le__, new, current)
                newSimuleCurrent = all(resWCnat)

                if newSimuleCurrent:
                    toReplace.append(current)

            if len(toReplace) > 0:
                    for toRemove in toReplace:
                        self.set[h].discard(toRemove)
                        self.size -= 1
                    self.set[h].add(new)
                    self.size += 1
                    return True

            else:
                self.set[h].add(new)
                self.size += 1
                return True


    def addLax(self, ss):
        h = hash(ss)
        new = ss.getRelevantAttributeWC()
        print(ss)
        try:
            currents = self.set[h]
        except KeyError:
            self.set[h] = set()
            self.set[h].add(new)
            self.size += 1
            return True
        else:
            toReplace = []
            for current in currents:
                resIdle = map(int.__le__, current, new)
                CurrentSimuleNew = all(resIdle)

                if CurrentSimuleNew:
                    return False

                resIdle = map(int.__le__, new, current)
                newSimuleCurrent = all(resIdle)

                if newSimuleCurrent:
                    toReplace.append(current)

            if len(toReplace) > 0:
                    for toRemove in toReplace:
                        self.set[h].discard(toRemove)
                        self.size -= 1
                    self.set[h].add(new)
                    self.size += 1
                    return True

            else:
                self.set[h].add(new)
                self.size += 1
                return True


    def addWC(self, ss):
        h = hash(ss)
        new = ss.getRelevantAttributeWC()
        try:
            currents = self.set[h]
        except KeyError:
            self.set[h] = set()
            self.set[h].add(new)
            self.size += 1
            return True
        else:
            toReplace = []
            for current in currents:
                resWC = map(int.__ge__, current, new)
                CurrentSimuleNew = all(resWC)

                if CurrentSimuleNew:
                    return False

                resWC = map(int.__ge__, new, current)
                newSimuleCurrent = all(resWC)

                if newSimuleCurrent:
                    toReplace.append(current)

            if len(toReplace) > 0:
                    for toRemove in toReplace:
                        self.set[h].discard(toRemove)
                        self.size -= 1
                    self.set[h].add(new)
                    self.size += 1
                    if len(self.set[h]) > 1 :
                        print(self.set[h])
                    return True

            else:
                self.set[h].add(new)
                self.size += 1
                if len(self.set[h]) > 1 :
                    print(self.set[h])
                return True

    def addNONE(self, ss):
        try:
            t = self.set[ss]
        except KeyError:
            self.set[ss] = 0
            self.size += 1
            return True
        else:
            return False

    def __set__(self):
        return set(self.set.values())

    def __iter__(self):
        return self.set.values().__iter__()

    def __len__(self):
        return len(self.set)
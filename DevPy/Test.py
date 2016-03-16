from SystemState import *
from Task import *
from TaskSet import *
from igraph import * 
from Scheduler import *
from itertools import *
import numpy as np
from Graph import *


print("aaaaaaaaaaaaaaaaaaaaaaaaaaa")

t1 = Task(0,5,5,1,[3,3])
t2 = Task(0,10,10,2,[1,7])
ts = TaskSet([t1,t2])


gmc = GraphMC(ts)

v = gmc.getInitialVertex()
print(v)
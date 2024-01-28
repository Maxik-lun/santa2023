# import numpy as np
from tqdm import tqdm
import networkx as nx
from minkwitz import applyPerm



def ReduceFactor(PG,s,maxl = 15):
    l0 = len(s)
    l1 = l0+1
    while (l0!=l1):
        a= []
        print(l0)
        # Find shortcuts using fast factorization of permutations
        ls = len(s)
        for i in tqdm(range(ls)):
            for j in range(3, maxl):
                j1= i+j
                if j1 < ls:
                    subs = s[i:j1+1]
                    #subs.reverse()
                    target = applyPerm(subs,PG)
                    sol = PG.FactorPermutation(target)
                    if len(sol)<(j1-i):
                        a.append((i,j1+1,{'weight':len(sol)}))
        # Find shortest path
        
        G = nx.path_graph(ls+1,nx.DiGraph)
        G.add_edges_from(a)
        opt = nx.dijkstra_path(G, 0, ls)
        #opt = nx.shortest_path(G, 0, ls, method = 'bellman-ford')
        sopt =[]
        for i,j in zip(opt,opt[1:]):
            if j-i == 1:
                sopt.append(s[i])
            else:
                subs = s[i:j]
                #subs.reverse()
                target = applyPerm(subs,PG)
                sol= PG.FactorPermutation(target)
                #sol.reverse()
                sopt = sopt + sol
        l1=l0
        s = sopt
        l0 = len(s) 

        if applyPerm(s,PG) != applyPerm(sopt,PG):
            print('error',s,sopt)  
            break
    return sopt
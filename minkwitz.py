from tqdm import tqdm
# import pandas as pd
# import numpy as np
from itertools import chain, product, combinations
from sympy.combinatorics.perm_groups import Permutation,PermutationGroup
from sympy.combinatorics.perm_groups import _distribute_gens_by_base,_orbits_transversals_from_bsgs


# A class for maintainig permutations and factorization over a SGS
class PermWord:
    def __init__(self, perms=[], words=[]):
        self.words = words
        self.permutation = perms
        self.flag = True

    @staticmethod
    def is_identity(self):
        return (self.words.len()==0)

    def inverse(self, geninvs):
        inv_perm = ~self.permutation
        inv_word = invwords(self.words, geninvs)
        return PermWord(inv_perm, inv_word)

    def __mul__(self, other):
        result_perm = self.permutation * other.permutation
        result_words = simplify(self.words + other.words)
        return PermWord(result_perm, result_words)

# A class generating factorization of permutations over a Strong Generating Set (SGS)
# The SGS is obtained using the sympy implementation for Schreier–Sims algorith
# The Minkwith algorithm (https://www.sciencedirect.com/science/article/pii/S0747717198902024)
# is used for mantainig a short word representation 

class SGSPermutationGroup:
    def __init__(self, gensi=[], base = None, strong_gens = None, deterministic = False):
        N =max([max(gensi[g]) for g in gensi])+1
        gensi = {g:Permutation(gensi[g],size = N) for g in gensi}
        gens = gensi.copy()
        gen0= [gensi[p] for p in gens]
        
        geninvs={}
        sizes = []
        for s in list(gens):
            sizes.append(gens[s].size)
            if s[0] != '-': 
                s1 = ~gens[s]
                gens["-" + s] = s1
                geninvs[s] = '-' + s
                geninvs['-' + s] = s    
        self.gens = gens
        self.geninvs = geninvs
        self.N = max(sizes)
        # Create the permutation group
        #gen0= [gens[p] for p in gens]
        G = PermutationGroup(gen0)
        self.G = G
        # obtain the strong generating set
        if base is not None and strong_gens is not None:
            basic_orbits, transversals, _ = sgs_process(base, strong_gens)
            self.base = base
            self.bo = basic_orbits
            self.bt = transversals
        elif deterministic:
            G.schreier_sims()
            self.base = G.base
            self.bo = G.basic_orbits
            self.bt = G.basic_transversals
        else:
            base, trans, orbits = schreier_sims_random(G)
            self.base = base
            self.bo = orbits
            self.bt = trans
        
     
        self.lo = [len(x) for x in self.bo]
        self.so = sum(self.lo)
        self.nu = None
    
    #   n: max number of rounds
    #   s: reset each s rounds
    #   w: limit for word size
    
    def getShortWords(self,n=10000,s=2000,w=20):
        self.nu = buildShortWordsSGS(self.N, self.gens, self.geninvs, self.base, n, s, w, self.so)


    def FactorPermutation(self,target):
        if self.nu == None:
            print('Execute getShortWords')
            return None
        return  factorizeM(self.N, self.gens, self.geninvs, self.base, self.nu, target)

    def CheckQuality(self):
        test = test_SGS(self.N,self.nu,self.base)
        qual = quality(self.N, self.nu, self.base)
        return test,qual

def sgs_process(base, strong_gens):
    strong_gens_distr = _distribute_gens_by_base(base, strong_gens)
    basic_orbits, transversals, slps = _orbits_transversals_from_bsgs(base,strong_gens_distr, slp=True)
    # rewrite the indices stored in slps in terms of strong_gens
    for i, slp in enumerate(slps):
        gens = strong_gens_distr[i]
        for k in slp:
            slp[k] = [strong_gens.index(gens[s]) for s in slp[k]]
    basic_orbits = [sorted(x) for x in basic_orbits]
    return basic_orbits, transversals, slps 
        
def schreier_sims_random(G):
    base, strong_gens = G.schreier_sims_random(consec_succ=5)
    strong_gens_distr =_distribute_gens_by_base(base, strong_gens)
    basic_orbits, transversals, slps = _orbits_transversals_from_bsgs(base, strong_gens_distr, slp=True)
    # rewrite the indices stored in slps in terms of strong_gens
    for i, slp in enumerate(slps):
        gens = strong_gens_distr[i]
        for k in slp:
            slp[k] = [strong_gens.index(gens[s]) for s in slp[k]]
    transversals = transversals
    basic_orbits = [sorted(x) for x in basic_orbits]
    return base, transversals,basic_orbits
        
def applyPerm(sol,PG):
    if sol == []:
        return Permutation(size = PG.N)
    target = PG.gens[sol[0]]
    for m in sol[1:]:
        target = target*PG.gens[m]
    return target       


def oneStep(N, gens, geninvs, base, i, t, nu):
    j = t.permutation.array_form[base[i]]  # b_i ^ t
    t1 = t.inverse(geninvs)
    if nu[i][j] is not None:
        result = t * nu[i][j]
        result.words = simplify(result.words)
        if len(t.words) < len(nu[i][j].words):
            nu[i][j] = t1
            oneStep(N, gens, geninvs, base, i, t1, nu)
    else:
        nu[i][j] = t1
        oneStep(N, gens, geninvs, base, i, t1, nu)
        result =  PermWord(Permutation(N),[])
    return result

def oneRound(N, gens,geninvs, base, lim, c, nu, t):
    i = c
    while i < len(base) and len(t.words)>0 and len(t.words) < lim:
        t = oneStep(N, gens, geninvs, base, i, t, nu)
        i += 1

def oneImprove(N, gens, geninvs, base, lim, nu):
    for j in range(len(base)):
        for x in nu[j]:
            for y in nu[j]:
                if x != None and y != None  and (x.flag or y.flag):
                    t = x * y
                    oneRound(N, gens, geninvs, base, lim, j, nu, t)

        for x in nu[j]:
            if x is not None:
                pw = x
                x.flag = False

def fillOrbits(N, gens, geninvs, base, lim, nu):
    for i in range(len(base)):
        orbit = []  # partial orbit already found
        for y in nu[i]:
            if y is not None:
                j = y.permutation.array_form[base[i]]
                if j not in orbit:
                    orbit.append(j)
        for j in range(i + 1, len(base)):
            for x in nu[j]:
                if x is not None:
                    x1 = x.inverse(geninvs)
                    orbit_x = [x.permutation.array_form[it] for it in orbit]
                    new_pts = [p for p in orbit_x if p not in orbit]

                    for p in new_pts:
                        t1 = x1 * (nu[i][x1.permutation.array_form[p]])
                        t1.words = simplify(t1.words)
                        if len(t1.words) < lim:
                            nu[i][p] = t1

# Options:
#   n: max number of rounds
#   s: reset each s rounds
#   w: limit for word size
#   so: sum  orbits size

#
def buildShortWordsSGS(N, gens, geninvs, base, n, s, w, so):
    nu = [[None for _ in range(N)] for _ in range(len(base))]
    for i in range(len(base)):
        nu[i][base[i]] = PermWord(Permutation(N),[])
    nw = 0
    maximum = n
    lim = float(w)
    cnt = 0
    with tqdm(total= so) as pbar:   
        iter_gen = chain.from_iterable(product(list(gens), repeat=i) for i in range(1,12))
        for gen in iter_gen:
            cnt += 1
            if cnt >= maximum or nw == so :
                break

            perm = gen_perm_from_word(gens,gen)
            pw = PermWord(perm,list(gen))
            oneRound(N, gens, geninvs, base, lim, 0, nu, pw)
            nw0 =nw
            nw =  sum([sum([x!=None for x in nu_i]) for nu_i in nu])
            deltanw = nw-nw0
            pbar.update(deltanw)
            if cnt % s == 0:
                oneImprove(N, gens, geninvs, base, lim, nu)
                if nw < so:
                    fillOrbits(N, gens, geninvs, base, lim, nu)
                lim *= 5 / 4
                
    return nu

def factorizeM(N, gens, geninvs, base, nu, target):
    result_list = []
    perm = target
    for i in range(len(base)):
        omega = perm.array_form[base[i]]
        perm *= nu[i][omega].permutation
        result_list = result_list + nu[i][omega].words
    if not perm == Permutation(size = N+1):
        print("failed to reach identity, permutation not in group")
    return simplify(invwords(result_list, geninvs))

def gen_perm_from_word(gens,words):
    res = gens[words[0]]
    for w in words[1:]:
        res = res * gens[w]
    return res

def invwords(ws, geninvs):
    inv_ws = [geninvs[g] for g in ws]
    inv_ws.reverse() 
    return inv_ws


# #remove invers generators in concatenation
# def simplify(ff):
#     if not ff:
#         return ff
#     # find adjacent inverse generators
#     zero_sum_indices = [(i, i + 1) for i in range(len(ff) - 1) if ff[i] == geninvs[ff[i + 1]] ]
#     # If there is no more simplications
#     if not zero_sum_indices:
#         return ff
#     # remove inverse pairs
#     for start, end in zero_sum_indices:
#         return simplify(ff[:start] + ff[end + 1:])
#     return ff

def simplify(ff):
    return(ff)

# Test Minwictz algorithm
    
def test_SGS(N,nu,base):
    result = True
    for i in range(len(base)):
        # diagonal identities
        p = nu[i][base[i]].words
        if p != []:
            result = False
            print('fail identity')
            
        for j in range(N):
            if j in nu[i]:
                p =nu[i][j].permutation.array_form 
                # stabilizes points upto i
                for k in range(i):
                    p2 = p[base[k]]
                    if p2 != base[k]:
                        result = False
                        print('fail stabilizer',i,j,k)

                
                # correct transversal at i
                if p[j] != base[i]:
                    result = False  
                    print('fail traversal ',i,j)
    return result

def quality(N, nu, base):
    result = 0
    for i in range(len(base)):
        maxlen = 0
        for j in range(N):
            if nu[i][j] is not None:
                wordlen = len(nu[i][j].words)
                if wordlen > maxlen:
                    maxlen = wordlen
        result += maxlen
    return result

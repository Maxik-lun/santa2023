import pandas as pd
from minkwitz import SGSPermutationGroup,applyPerm
from reduce import ReduceFactor
from valid import val_score



p = '/kaggle/input/santa-2023/'
print('Reading data...')
path = pd.read_csv(p + 'puzzles.csv')
info = pd.read_csv(p + 'puzzle_info.csv')
path = pd.merge(path,info)




ltypes = [
'cube_4/4/4',
]
sub = pd.read_csv(p + 'sample_submission.csv')
nretry = 1


for type in ltypes:
    print(type)
   
    ids = sub[path.puzzle_type == type].id.values
    gens = eval(info[info.puzzle_type == type].allowed_moves.values[0])
    
    for _ in range(nretry):
        sols = sub[path.puzzle_type == type].moves.values
        istate = path[path.puzzle_type == type].initial_state.values
        fstate = path[path.puzzle_type == type].solution_state.values
        ll = sub.loc[path.puzzle_type == type,'moves'] .map(lambda x: len(x.split("."))).sum()
        print('Sum moves ', ll)
        PG = SGSPermutationGroup(gens,deterministic = True)
        print('Dim:',PG.N,'Lenght base;',len(PG.base),'Sum Orbits:',PG.so)
        geninvs = PG.geninvs
        PG.getShortWords(n=100000, s=100, w=500)
        print(PG.CheckQuality())
    

        for i,sol in enumerate(sols[:1]):
            sol = sol.split('.')
            print(istate[i])
            print(fstate[i])
            sol.reverse()
            target = applyPerm(sol,PG)
            print(target)
            ss = PG.FactorPermutation(target)
            if len(ss) > len(sol):
                ss = sol
            ss = ReduceFactor(PG,ss,500)
            if target != applyPerm(ss,PG):
                print('error',applyPerm(sol,PG),applyPerm(ss,PG)) 
                continue
            ss.reverse()
    
            flag,_ =val_score(ids[i],'.'.join(ss),path)
            #if len(ss)<len(sol):
            print(ids[i],len(sol),'->',len(ss),flag)
            if (len(ss)<len(sol) and flag):
                sub.loc[sub.id == ids[i],'moves'] = '.'.join(ss)
        ll = sub.loc[path.puzzle_type == type,'moves'] .map(lambda x: len(x.split("."))).sum()
        print( 'Sum moves', ll)

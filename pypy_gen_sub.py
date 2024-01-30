import pandas as pd
from minkwitz import SGSPermutationGroup,applyPerm
from process_utils import parse_gap_data
from reduce import ReduceFactor
from valid import val_score



# p = '/kaggle/input/santa-2023/'
p = './'
print('Reading data...')
path = pd.read_csv(p + 'puzzles.csv')
info = pd.read_csv(p + 'puzzle_info.csv')
path = pd.merge(path,info)
gap_dir = "./gap_data/"




ltypes = [
    'cube_2/2/2', 'cube_3/3/3', 'cube_4/4/4', 
    # 'cube_5/5/5', 'cube_6/6/6', 'cube_7/7/7', 
    # 'cube_8/8/8', 'cube_9/9/9', 'cube_10/10/10',
    # 'cube_19/19/19', 
    # 'cube_33/33/33', 
    # 'wreath_6/6', 'wreath_7/7', 'wreath_12/12', 'wreath_21/21', 'wreath_33/33', 'wreath_100/100',
    # 'globe_1/8', 'globe_1/16', 'globe_2/6', 'globe_3/4', 'globe_6/4', 
    # 'globe_6/8', 'globe_6/10', 'globe_3/33', 'globe_8/25'
    ]
sub = pd.read_csv('./sample_submission.csv')
nretry = 1


for type in ltypes:
    print(type)
   
    ids = sub[path.puzzle_type == type].id.values
    gens = eval(info[info.puzzle_type == type].allowed_moves.values[0])
    N = max([max(gens[g]) for g in gens])+1
    base, strong_gens = parse_gap_data(gap_dir, type, N, debug=False)
    for _ in range(nretry):
        sols = sub[path.puzzle_type == type].moves.values
        istate = path[path.puzzle_type == type].initial_state.values
        fstate = path[path.puzzle_type == type].solution_state.values
        ll = sub.loc[path.puzzle_type == type,'moves'] .map(lambda x: len(x.split("."))).sum()
        print('Sum moves ', ll)
        # PG = SGSPermutationGroup(gens,deterministic = False)
        PG = SGSPermutationGroup(gens, base, strong_gens)
        print('Dim:',PG.N,'Lenght base;',len(PG.base),'Sum Orbits:',PG.so)
        geninvs = PG.geninvs
        PG.getShortWords(n=100000, s=100, w=500)
        print(PG.CheckQuality())
    

        for i,sol in enumerate(sols):
            sol = sol.split('.')
            # print(istate[i])
            # print(fstate[i])
            sol.reverse()
            target = applyPerm(sol,PG)
            # print(target)
            ss = PG.FactorPermutation(target)
            if len(ss) > len(sol):
                ss = sol
            ss = ReduceFactor(PG,ss,500)
            if target != applyPerm(ss,PG):
                print('error',applyPerm(sol,PG),applyPerm(ss,PG)) 
                continue
            ss.reverse()
    
            flag,_ =val_score(ids[i],'.'.join(ss),path)

            print(ids[i],len(sol),'->',len(ss),flag)
            if (len(ss)<len(sol) and flag):
                sub.loc[sub.id == ids[i],'moves'] = '.'.join(ss)
        ll = sub.loc[path.puzzle_type == type,'moves'] .map(lambda x: len(x.split("."))).sum()
        print( 'Sum moves', ll)
        
lls = sub["moves"].map(lambda x: len(x.split(".")))
ll = lls.sum()
print(ll)
sub.to_csv("./submission.csv", index=False) 
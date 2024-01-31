import re
import os
# import pickle
from sympy.combinatorics.perm_groups import Permutation

def normalize_text(text):
    text = text.replace(" ", '').replace(")\n(", "$")
    text = text.replace("\n", '').replace("$", ")\n(")
    return text

def shift_perm(s):
    nums = map(int, re.findall(r'\d+', s))
    delims = re.split(r'\d+', s)
    ans = [delims[0]]
    for n, d in zip(nums, delims[1:]):
        ans.append(str(n - 1))
        ans.append(d)
    return ''.join(ans)

def parse_gap_data(dir, ptype, N, debug = False):
    """
    dir - folder with GAP SGSs and bases
    ptype - kaggle pazzle type
    N - permutation group's degree, number of elements (e.g. 54 for 3x3x3 rubik)
    return: base: array[int], SGS: array[Permutation]
    """
    perm_dict = {}
    bpath = os.path.join(dir, f"{ptype.replace('/', '-')}_base.txt")
    gpath = os.path.join(dir, f"{ptype.replace('/', '-')}_sgs.txt")
    if not(os.path.exists(bpath) and os.path.exists(gpath)):
        return [], []
    with open(gpath, "r") as f:
        raw_text = f.read()
        sgs = [x for x in normalize_text(raw_text).split('\n') if x!='']
        if debug:
            sgs = list(map(lambda x: shift_perm(x), sgs))
        else:
            sgs = list(map(lambda x: eval("Permutation" + shift_perm(x)), sgs))
            sgs = [Permutation(g.cyclic_form, size = N) for g in sgs]
    with open(bpath, "r") as f:
        base_text = f.read().replace(' ', '').replace('\n', '')
        base = [x-1 for x in eval(base_text)]
    return base, sgs

def load_sympy(sp_dir, ptype, N):
    group_dict = {}
    for ext in ['base', 'sgs', 'bo']:
        path = os.path.join(sp_dir, f"{ptype.replace('/', '-')}_{ext}.txt")
        with open(path, "r") as f:
            group_dict[ext] = eval(f.read())
        if ext == 'sgs':
            group_dict[ext] = [Permutation(g.cyclic_form, size = N) for g in group_dict[ext]]
    return group_dict['base'], group_dict['sgs'], group_dict['bo']

def dump_sympy(sp_dir, ptype, base, strong_gens, basic_orbits):
    for obj, ext in zip([base, strong_gens, basic_orbits], ['base', 'sgs', 'bo']):
        path = os.path.join(sp_dir, f"{ptype.replace('/', '-')}_{ext}.txt")
        with open(path, "w") as f:
            print(obj, file = f)

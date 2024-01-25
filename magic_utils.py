from math import sqrt
from termcolor import colored

tb = [['A','w','u'],
      ['B','g','f'],
      ['C','r','r'],
      ['D','b','b'],
      ['E','o','l'],
      ['F','y','d']]

def a2color(state):
    for c in tb:
        state = state.replace(c[0],c[1])
    return state.upper()

def a2face(state):   
    if type(state) == str:
        for c in tb:
            state = state.replace(c[0],c[2])
        c = state.split(";")
    else:
        c = state
    s = int(sqrt((len(c) / 6)))
    if len(c[0]) > 1:
        f = ['U']*s*s+['F']*s*s+['R']*s*s+['B']*s*s+['L']*s*s+['D']*s*s
        c = list(map(lambda t: f[eval(t[1:])], c))
    state = ';'.join(c)
    return state.upper()

def color2a(state):
    state = state.lower()
    for c in tb:
        state = state.replace(c[1],c[0])
    return state.upper()

def face2a(state):
    state = state.lower()
    for c in tb:
        state = state.replace(c[2],c[0])
    return state.upper()

def def_faces(s, f="ABCDEF",schar=";"):
    return f"{schar}".join([f'{f[0]}']*s*s+[f'{f[1]}']*s*s+[f'{f[2]}']*s*s+
                    [f'{f[3]}']*s*s+[f'{f[4]}']*s*s+[f'{f[5]}']*s*s)

def get_state(state):
    if type(state) == str:
        state = state.replace(";","")
    else:
        state = "".join(state)
    return "".join(ch for i, ch in enumerate(state) if ch not in state[:i])

def swap(state, schar=""): #UFRBLD => URFDLB
    s = list(state.replace(";", ""))
    n = int(len(s) / 6)
    return f"{schar}".join(s[:n]+s[n*2:n*3]+s[n:n*2]+s[n*5:]+s[n*4:n*5]+s[n*3:n*4])

def reversed_moves(sol, schar="."):
    rev = [("-" if '-' not in move else "") + move.lstrip('-') for move in reversed(sol.split(schar))]
    return schar.join(rev)

def conv_moves(sol,s,reverse=False):
    M = {}
    M["U"] = f'-d{s-1}'
    M["R"] = "r0"
    M["B"] = f"-f{s-1}"
    M["F"] = "f0"
    M["L"] = f"-r{s-1}"
    M["D"] = "d0"
    if s > 2:
        M["Uw"] = f'-d{s-2}.-d{s-1}'
        M["Rw"] = f"r0.r1"
        M["Bw"] = f'-f{s-2}.-f{s-1}'
        M["Fw"] = f"f0.f1"
        M["Lw"] = f'-r{s-2}.-r{s-1}'
        M["Dw"] = f"d0.d1"
        for i in range(2,s):
            M[f"{i}U"] = f'-d{s-2}'
            M[f"{i}R"] = f"r{i-1}"
            M[f"{i}B"] = f'-f{s-2}'
            M[f"{i}F"] = f"f{i-1}"
            M[f"{i}L"] = f'-r{s-2}'
            M[f"{i}D"] = f"d{i-1}"
    if s > 3:
        M["2Uw"] = f'-d{s-2}.-d{s-1}'
        M["2Rw"] = f"r0.r1"
        M["2Bw"] = f'-f{s-2}.-f{s-1}'
        M["2Fw"] = f"f0.f1"
        M["2Lw"] = f'-r{s-2}.-r{s-1}'
        M["2Dw"] = f"d0.d1"
        for i in range(3, s//2+1):
            M[f"{i}Uw"] = f'-d{s-i}.' + M[f"{i-1}Uw"]
            M[f"{i}Rw"] = M[f"{i-1}Rw"] + f'.r{i-1}'
            M[f"{i}Bw"] = f'-f{s-i}.' + M[f"{i-1}Bw"]
            M[f"{i}Fw"] = M[f"{i-1}Fw"] + f'.f{i-1}'
            M[f"{i}Lw"] = f'-r{s-i}.' + M[f"{i-1}Lw"]
            M[f"{i}Dw"] = M[f"{i-1}Dw"] + f'.d{i-1}'
    for m in list(M):
        M[m+"2"] = M[m] + '.' + M[m]
        if "-" in M[m]:
            M[m+"'"] = M[m].replace("-","")
        else:
            M[m+"'"] = '.'.join(["-"+i for i in M[m].split('.')])

    if (sum(1 for c in "".join(sol) if c.isupper())) > 0:
        schar = "."
        if type(sol) == str:
            sol = sol.split(" ")
        sol = [M[m] for m in sol]
        sol = f"{schar}".join(sol)
        sol = sol.replace(" ",".")
        sol = sol.replace("..",".")
    else:
        schar = " "
        sol = sol.split(".")
        inv_map = {v: k for k, v in M.items() if not (' ' in v)}
        sol = [inv_map[m] for m in sol]
        sol = f"{schar}".join(sol)
    if reverse:
        sol = reversed_moves(sol, schar)
    return sol

def move_state(state, allmoves, mv):
    power = 1
    if mv[0] == "-":
        mv = mv[1:]
        power = -1
    p = allmoves[mv]
    state = (p ** power)(state)
    return state

def run_moves(state, allmoves, moves):
    state = state.split(";")
    for m in moves.split("."):
        state = move_state(state, allmoves, m)
    state = ";".join(state)
    return state

def count_moves(mv):
    return mv.count('.')+mv.count(' ') + 1

def score(sub):
    return sub['moves'].apply(lambda moves: moves.count('.')+1).sum()

colors = {' Y ': colored(' Y ',color='black', on_color='on_yellow'),
          ' W ': colored(' W ',color='black', on_color='on_white'),
          ' G ': colored(' G ',color='black', on_color='on_green'),
          ' B ': colored(' B ',color='black', on_color='on_light_blue'),
          ' R ': colored(' R ',color='black', on_color='on_light_red'),
          ' O ': colored(' O ',color='black', on_color='on_red'),
          ' D ': colored(' D ',color='black', on_color='on_yellow'),
          ' U ': colored(' U ',color='black', on_color='on_white'),
          ' F ': colored(' F ',color='black', on_color='on_green'),
          ' L ': colored(' L ',color='black', on_color='on_red'),
         }

def set_colors(face):
    for key, value in colors.items():
        face = face.replace(key, value)
    return face

# U F R B L D
def cube2d(c=[],s=2):
    s = max(s,2)   
    if type(c) == str:
        c = a2face(c)
        c = c.split(";")
    if len(c) < 24:
        c = ['U']*s*s+['F']*s*s+['R']*s*s+['B']*s*s+['L']*s*s+['D']*s*s
    s = int(sqrt((len(c) / 6)))
    U = '\n'.join([f'{s*"   "}' + ''.join(f' {c[i+j]} ' for j in range(s)) for i in range(0, s*s, s)])
    M = '\n'.join([''.join(f' {c[s*s*4+i+j]} ' for j in range(s)) +
                   ''.join(f' {c[s*s*1+i+j]} ' for j in range(s)) +
                   ''.join(f' {c[s*s*2+i+j]} ' for j in range(s)) +
                   ''.join(f' {c[s*s*3+i+j]} ' for j in range(s)) for i in range(0, s*s, s)])
    D = '\n'.join([f'{s*"   "}' +''.join(f' {c[s*s*5+i+j]} ' for j in range(s)) for i in range(0, s*s, s)])
    D += '\n'
    print(set_colors(U))
    print(set_colors(M))
    print(set_colors(D))
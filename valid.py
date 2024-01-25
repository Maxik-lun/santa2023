#Check if a solution is valid

def apply_move(moves, move, state):
    m = move
    s = state.split(';')

    move_list = moves[m]
    new_state = []
    for i in move_list:
        new_state.append(s[i])
    s = new_state

    return ';'.join(s)
    
def init_reverse_moves(moves):
    new_moves = {}
    
    for m in moves.keys():
        new_moves[m] = moves[m]
        xform = moves[m]
        m_inv = '-' + m
        xform_inv = len(xform) * [0]
        for i in range(len(xform)):
            xform_inv[xform[i]] = i
        new_moves[m_inv] = xform_inv

    return new_moves


def validate(moves, initial_state, solution_state, solution, num_wildcards):
    sols = solution.split('.')
    cur_state = initial_state
    for s in sols:
        if s not in moves:
            return False
        cur_state = apply_move(moves, s, cur_state)
    err_cnt = sum(c!=e for c,e in zip(cur_state.split(';'), solution_state.split(';')))
    if err_cnt <= num_wildcards:
        return True,cur_state
    else:
        return False,cur_state

def val_score(i,sol,path):
    initial_state = path.initial_state.values[i]
    solution_state = path.solution_state.values[i]
    moves = eval(path.allowed_moves.values[i])
    moves = init_reverse_moves(moves)
    num_wildcards = path.num_wildcards.values[i]
    solution = sol

    return validate(moves, initial_state, solution_state, solution, num_wildcards)
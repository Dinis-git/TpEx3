from z3 import *

N = 10

def getN():
    N = input("digite o n")

    if not(isinstance(N , Int)):
        print("Input errado digite novamente")
        getN()


Vars = ['a' , 'b' , 'x' , 'y' , 'z']

#codigo feito por llm
def declare(i):
    s = {'pc': BitVec(f'pc{i}', 2)}
    for v in Vars:
        s[v] = BitVec(f'{v}{i}', N)
    return s


def keep(atual, prox, vars):
    return And([prox[v] == atual[v] for v in vars])


def init(atual):
    return And(atual['pc'] == 0 , atual['x'] == atual['a'] , atual['y'] == atual['b'] , atual['x'] >= 0 , atual['y'] >= 0 , atual['z'] == 0)

def trans(s, t):
    pc, pc1 = s['pc'], t['pc']
    # local 0: teste do ciclo
    e0a = And(pc == 0, s['y'] != 0, pc1 == 1, keep(s, t, Vars))
    e0b = And(pc == 0, s['y'] == 0, pc1 == 2, keep(s, t, Vars))
    # local 1: se y é par: x << 1 , y >> 1 , z se nao x , y-1 , z+x
    e1a = And(pc == 1, (s['y'] & 1) == 0 , pc1 == 0,
                t['x'] == s['x'] << 1, t['y'] == s['y'] >> 1 , keep(s, t, ['a','b','z']))
    e1b = And(pc == 1, (s['y'] & 1) == 1 , pc1 == 0, t['y'] == s['y'] -1 , t['z'] == s['z'] + s['x']  ,keep(s, t, ['a' , 'b' , 'x']))
    # local 3: estado final (ciclo sobre si próprio, para a animação)
    e2 = And(pc == 2, pc1 == 2, keep(s, t, Vars))
    return Or(e0a, e0b, e1a, e1b, e2)
    
def erro(s):
    return And(s['pc'] == 3 , s['z'] == s['a'] * s['b'])
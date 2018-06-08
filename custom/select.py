import gurobipy as grb
import sys
import json

data = json.load(sys.stdin)
# open("dump.txt", 'w').write(sys.stdin.read())

memory_budget = int(sys.argv[1]) if len(sys.argv) == 2 else 256

data_bak = {
    "edges": [
        "s1 s2", "s2 s3", "s1 s4", "s2 s4", "s2 s5", "s3 s4", "s3 s5", "s3 s6", "s4 s5", "s5 s6",
        "h1 s2", "h2 s3", "h3 s4", "h4 s5"
    ],
    "paths": {
        "h2 h4": [
            [ 0.25, "h2 s3", "s3 s2", "s2 s5", "s5 h4" ],
            [ 0.25, "h2 s3", "s3 s4", "s4 s5", "s5 h4" ],
            [ 0.25, "h2 s3", "s3 s5", "s5 h4" ],
            [ 0.25, "h2 s3", "s3 s6", "s6 s5", "s5 h4" ]
        ],
        "h3 h1": [
            [ 0.25, "h3 s4", "s4 s1", "s1 s2", "s2 h1" ],
            [ 0.25, "h3 s4", "s4 s2", "s2 h1" ],
            [ 0.25, "h3 s4", "s4 s3", "s3 s2", "s2 h1" ],
            [ 0.25, "h3 s4", "s4 s5", "s5 s2", "s2 h1" ]
        ]
    }
}

data["nodes"] = {n for edge in data["edges"] for n in edge.split(' ')}

# YATES have st pairs like h1 -> h1, which is undesirable in our algorithm
for n in data["nodes"]:
    if n[0] == 'h':
        del data["paths"]["{} {}".format(n, n)]

def rev(p):
    a, b = p.split(' ')
    return b + ' ' + a

def renormalize(scheme):
    for pair, paths in scheme.items():
        tw = sum(x[0] for x in paths)
        for path in paths:
            path[0] /= tw

def select_by_path_budget():
    pass

def select_greedy():
    pass

def select_program():
    pass

# model 1: find the max-min path per pair
m = grb.Model("K")

m.setParam('OutputFlag', False)

K = m.addVar(vtype=grb.GRB.INTEGER, name="K")

pathvar = {}

for pair, paths in data["paths"].items():
    p1, p2 = pair.split(' ')
    pathvar[pair] = [m.addVar(vtype=grb.GRB.BINARY, name="s_{}_{}_{}".format(p1, p2, i))
                     for i in range(len(paths))]
m.update()

# constraint 1: at least K paths
for pair, var in pathvar.items():
    m.addConstr(sum(var) >= K, name="d_{}_{}".format(*pair.split(' ')))
    
# constraint 2: flow table buget
for n in data["nodes"]:
    passed = []
    for pair, paths in data["paths"].items():
        for i, path in enumerate(paths):
            for edge in path[1:]:
                if n in edge.split(' '):
                    passed.append(pathvar[pair][i])
                    break
    if len(passed) > 0:
        m.addConstr(sum(passed) <= memory_budget, name="n_{}".format(n))

m.setObjective(K, sense=grb.GRB.MAXIMIZE)

m.write("dump1.lp")
m.write("dump1.mps")

m.optimize()

status = m.status
if status in (grb.GRB.Status.INF_OR_UNBD, grb.GRB.Status.INFEASIBLE, grb.GRB.Status.UNBOUNDED):
    print('The model cannot be solved because it is infeasible or unbounded')
    exit(1)

if status != grb.GRB.Status.OPTIMAL:
    print('Optimization was stopped with status %d' % status)
    exit(0)

K = K.X

# model 2: maximize total number of paths
m = grb.Model("totalnop")

m.setParam('OutputFlag', False)

pathvar = {}

for pair, paths in data["paths"].items():
    p1, p2 = pair.split(' ')
    pathvar[pair] = [m.addVar(vtype=grb.GRB.BINARY, name="s_{}_{}_{}".format(p1, p2, i))
                     for i in range(len(paths))]
m.update()

# constraint 1: at least K paths
for pair, var in pathvar.items():
    m.addConstr(sum(var) >= K, name="d_{}_{}".format(*pair.split(' ')))

# constraint 2: flow table buget
for n in data["nodes"]:
    passed = []
    for pair, paths in data["paths"].items():
        for i, path in enumerate(paths):
            for edge in path[1:]:
                if n in edge.split(' '):
                    passed.append(pathvar[pair][i])
                    break
    if len(passed) > 0:
        m.addConstr(sum(passed) <= memory_budget, name="n_{}".format(n))

m.setObjective(sum(v for l in pathvar.values() for v in l), sense=grb.GRB.MAXIMIZE)

m.write("dump2.lp")
m.write("dump2.mps")

m.optimize()

result = {}

for pair, paths in data["paths"].items():
    choices = pathvar[pair]
    result[pair] = [path for path, choice in zip(paths, choices) if choice.X > 0.5]

renormalize(result)

json.dump(result, open("out.txt", "w"), indent=2)
json.dump(result, sys.stderr)
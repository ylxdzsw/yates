import gurobipy as grb
import sys
import json

data = json.load(sys.stdin)
# open("dump.txt", 'w').write(sys.stdin.read())

memory_budget = int(sys.argv[1]) if len(sys.argv) == 2 else 1000

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

edges, paths = data["edges"], data["paths"]
nodes = {n for edge in data["edges"] for n in edge.split(' ')}

# YATES have st pairs like h1 -> h1, which is undesirable in our algorithm
for n in nodes:
    if n[0] == 'h'
        del paths["{} {}".format(n, n)]

def rev(p):
    a, b = p.split(' ')
    return b + ' ' + a

def delete_renormalize():
    pass

def select_by_path_budget():
    pass

def select_greedy():
    pass

def select_program():
    pass


# model 1: find the max-min path per pair
m = grb.Model("K")

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
for n in nodes:
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

print m.optimize()
exit(0)


# objective: minimum overall congestion
terms = []
for edge in data["edges"]:
    if 'h' in edge:
        continue
    
    flow = []
    
    for st, paths in data["paths"].items():
        for i, path in enumerate(paths):
            if edge in path or rev(edge) in path:
                flow.append(pathvar[st][i][1])
                break
    
    terms.append(sum(flow))

status = m.status
if status in (grb.GRB.Status.INF_OR_UNBD, grb.GRB.Status.INFEASIBLE, grb.GRB.Status.UNBOUNDED):
    print('The model cannot be solved because it is infeasible or unbounded')
    exit(1)

if status != grb.GRB.Status.OPTIMAL:
    print('Optimization was stopped with status %d' % status)
    exit(0)


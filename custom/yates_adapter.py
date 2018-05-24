#!/usr/bin/env python2

from dinic import get_edge_disjoint_paths
from path_numbug import calc_path_num

import sys

read_topo = True
node_list = []
node_dict = {}
topo = set()
demands = []

# requires switches and hosts numbers to be a 1 to 1 map
for line in sys.stdin:
    line = line.strip()
    
    if line == "***":
        read_topo = False
        continue
    
    src, dst = line.split(' ')
    src, dst = src[1:], dst[1:]
    if src == dst:
        continue
        
    if read_topo:
        for n in (src, dst):
            if n not in node_dict:
                node_list.append(n)
                node_dict[n] = len(node_list) - 1
        topo.add((node_dict[src], node_dict[dst]))
    else:
        demands.append((node_dict[src], node_dict[dst]))
        
matrix = [[+((i,j) in topo) for i in range(len(node_list))] for j in range(len(node_list))]

# print matrix, demands

all_paths = []
max_num=0
for (s, t) in demands:
    disjoint_paths = get_edge_disjoint_paths(matrix, s, t)
    all_paths.append(disjoint_paths)
    max_num+=len(disjoint_paths)

optinum, optipaths=calc_path_num(matrix, max_num, 3, all_paths)

# print optipaths

import json

def to_pair(x):
    return node_list[x[0][0]], node_list[x[0][-1]]

def to_path(x):
    path = ["s{} s{}".format(node_list[x[i]], node_list[x[i+1]]) for i in range(len(x)-1)]
    hsrc = "h{} s{}".format(node_list[x[0]], node_list[x[0]])
    hdst = "s{} h{}".format(node_list[x[-1]], node_list[x[-1]])
    return [hsrc] + path + [hdst]

print json.dumps({ "h{} h{}".format(*to_pair(paths)): map(to_path, paths) for paths in optipaths })

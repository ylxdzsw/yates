#!/usr/bin/env julia

using OhMyJulia
using Fire

function parse_path(file)
    
end

function parse_topo(file)
    nodes = Set{String}()
    edges = Set{Pair{String, String}}()
    for line in eachline(file)
        m = match(r"([hs]\d+)\s*->\s*([hs]\d+)", line)
        m == nothing && continue
        
        src, dst = car(m), cadr(m)
        push!(nodes, src, dst)
        push!(edges, src => dst)
    end
    collect(nodes), collect(edges)
end

@main function main(data="abilene")
    nodes, edges = parse_topo(rel"../data/topologies/$data.dot")
    algoes = all_files(rel"../data/result/$data/paths")
    paths = map(parse_path, algoes)
    algonames = map(basename, algoes)
    
    
end
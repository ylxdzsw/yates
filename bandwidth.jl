#!/usr/bin/env julia

using OhMyJulia
using Fire

@main function main(data="abilene")
    host_list = readlines("data/hosts/$data.hosts")
    demand_list = map(readlines("data/demands/$data.txt")) do line
        line = map(parse, split(line, ' '))
        reshape(line, length(host_list), length(host_list))'
    end
    
    for file in all_files("data/results/$data/paths")
        demand_matrix = try
            demand_list[parse(Int, split(file, '_')[end]) + 1]
        catch
            continue
        end
        
        open(file * "_bandwidth", "w") do fout
            current_demand = 0.
            
            for line in eachline(file)
                m = match(r"(h\d+)\s*->\s*(h\d+)", line)
                if m != nothing
                    src = findfirst(host_list, car(m))
                    dst = findfirst(host_list, cadr(m))
                    current_demand = demand_matrix[src, dst]
                end
                
                s = split(line, '@')
                if length(s) == 2
                    w = split(cadr(s))
                    if length(w) == 1
                        bandwidth = parse(f64, w[]) * current_demand
                        line *= " $bandwidth"
                    end
                end

                println(fout, line)
            end
        end
    end
end

open Core

open Yates_types.Types
open Yojson
open Yojson.Basic.Util

module VertMap = Map.Make(String)

let vname topo v = let Some x =
  let dotstr = Topology.Vertex.to_dot (Topology.vertex_to_label topo v) in
  let substrs = String.split dotstr ~on:' ' in
    (List.nth substrs 0) in
  x

let edge_to_str topo edge =
  let src, _ = Topology.edge_src edge in
  let dst, _ = Topology.edge_dst edge in
  Printf.sprintf "%s %s" (vname topo src) (vname topo dst)

let str_to_vert_pair dict pair_str =
  let (Some a, Some b) =
    let substrs = String.split pair_str ~on:' ' in
      ((List.nth substrs 0), (List.nth substrs 1)) in
  let (Some src, Some dst) =
    ((VertMap.find dict a), (VertMap.find dict b)) in
  (src, dst)

let select_path topo scheme = 
  let vert_dict = Topology.fold_vertexes
    (fun v acc -> VertMap.set acc ~key:(vname topo v) ~data:v)
    topo VertMap.empty in

  let json = `Assoc [
    ("edges", `List (Topology.fold_edges (fun e acc -> `String (edge_to_str topo e)::acc) topo []));
    ("paths", `Assoc (SrcDstMap.fold scheme ~init:[] ~f:(fun ~key:(src, dst) ~data:pathmap acc -> 
      let k = Printf.sprintf "%s %s" (vname topo src) (vname topo dst) in
      let v = `List (PathMap.fold pathmap ~init:[] ~f:(fun ~key:p ~data:w acc ->
        `List ((`Float w)::(List.map p (fun e -> `String (edge_to_str topo e))))::acc
      )) in
      (k, v)::acc
    )))
  ] in
  
  (*because gurobi prints some shits into stdout, we have to swap stdout and stderr*)
  let (cout, cin) = Unix.open_process "python2 custom/select.py 3>&2 2>&1 1>&3" in
  
  Yojson.Basic.pretty_to_channel cin json;
  Out_channel.close cin;
  
  let json = Yojson.Basic.from_channel cout in
  
  List.fold_left (to_assoc json) ~init:SrcDstMap.empty
    ~f:(fun acc (k, v) ->
      let path_map =
        List.fold_left (to_list v) ~init:PathMap.empty
          ~f:(fun acc path ->
            let head::tail = (to_list path) in
            let prob = (to_float head) in
            let p = List.map tail (fun x ->
              let (src, dst) = str_to_vert_pair vert_dict (to_string x) in
                Topology.find_edge topo src dst) in
            PathMap.set acc ~key:p ~data:prob
          ) in
      SrcDstMap.set acc ~key:(str_to_vert_pair vert_dict k) ~data:path_map
    )
  
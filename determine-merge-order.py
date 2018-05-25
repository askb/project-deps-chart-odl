# @License EPL-1.0 <http://spdx.org/licenses/EPL-1.0>
##############################################################################
# Copyright (c) 2015 The Linux Foundation.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
##############################################################################

""" This python script is used for determine the order of module dependencies
to be followed while performing merge operation during version bumping process
for a new release. It creates an file merge_order.log which lists the order to
be followed.

The merge order is computed be building a directed graph (dependency tree) from
the jobs and performing a topological sort on the graph starting from the root,
This returns a ordered list of jobs which is output to file `merge-order.log`.

Usage: ./determine-merge-order.py [input-file] [output-file] [png-file] [dot-file]

Args:
    input-file:     Path to input file (default: dependency.log)
    output-file:    Path to output file (default: merge-order.log)
    png-file:       Path to output png file (default: merge-order.png)
    dot-file:       Path to output dot file (default: merge-order.dot)

@Author : Anil Shashikumar Belur aka abelur
@Email  : askb23@gmail.com
"""

import matplotlib.pyplot as plt
import networkx as nx
import re
import sys

if __name__ == '__main__':

    try:
        input_file = sys.argv[1]
        if not sys.argv[1]:
            input_file = "dependencies.log"
    except IndexError:
        print('Input file with dependencies unavailable')
        sys.exit(1)

    try:
        with open(input_file, 'r') as rhandle:
            raw = rhandle.read()
    except IOError:
        print("Error on opening file: {0}".format(input_file))
        sys.exit(1)

    try:
        output_png_file = sys.argv[3]
        if not output_png_file:
            output_png_file = "merge-order.png"
    except IndexError:
        print('Output file with png unavailable')
        sys.exit(1)

    try:
        output_dot_file = sys.argv[4]
        if not output_dot_file:
            output_dot_file = "merge-order.dot"
    except IndexError:
        print('Output file with dot unavailable')
        sys.exit(1)

    try:
        output_file = sys.argv[2]
        if not output_file:
            output_file = "merge-order.log"
    except IndexError:
        print('Output file with dependencies unavailable')
        sys.exit(1)

    regex_node = re.compile(r':')
    regex_deps = re.compile(r',')

    # build a directed graph from the list of jobs
    G = nx.DiGraph()
    for l in raw.splitlines():
        if len(l):
            node, prereq = regex_node.split(l)
            deps = tuple(regex_deps.split(prereq))
            if not prereq:
                if target.strip == 'integration/distribution' or target.strip == 'integration':
                    continue
                G.add_node(node)
            else:
                tups = [ (a,node) for a in deps if (a != "odlparent" or node == "federation" or node == "yangtools" or node == "next") ]
                print("Add node:{1} ---> edge:{0}".format(a, node))
                print(tups)
                print(",")
                G.add_edges_from(tups)
                # tups = [(a, node) for a in deps]
                # G.add_edges_from(tups)

    deps_order = nx.topological_sort(G)
    ### this order is incorrect, maybe useful for merging patches in sequence
    print("Topological sort order:")
    for i, item in enumerate(deps_order):
        print("{0}:{1}".format(i, item))

    print("Compute how to parallel merge of projects:")
    G1 = nx.DiGraph()
    for n in deps_order:
        if n == 'yangtools': # skip n0
            continue
        if not nx.has_path(G, 'mdsal', n): #n1 and n2 are disconnected from n0
            lpath=max(list(nx.all_simple_paths(G, n, 'integration/distribution')), key=len)
            G1.add_path(lpath)
            print("{0}".format(lpath))
            continue
        lpath=max(list(nx.all_simple_paths(G, 'yangtools', n)), key=len)
        G1.add_path(lpath)

    print("Print order of parallel merging of projects:")
    # levels
    from operator import itemgetter
    sorted_dict=sorted(nx.shortest_path_length(G1, 'yangtools').items(), key=itemgetter(1)) # omits n1, n2
    for k,v in sorted_dict:
        print("{1} ---> {0}".format(k,v))

    print("Create a .dot of the graph generated:")
    plt.figure(figsize=(35,25))
    pos=nx.drawing.nx_pydot.graphviz_layout(G1, prog='dot', root='n0')
    nx.draw(G1, pos=pos, with_labels=True, node_size=1600, font_size=20, node_shape='h')  #so^>v<dph8
    plt.savefig('/tmp/merge-order.png')
    nx.drawing.nx_pydot.write_dot(G1, "/tmp/merge-order.dot")

    # If you want to view the plot disable the below line or view it through eog|feh
    # plt.show()

    try:
        with open(output_file, 'w+') as whandle:
            for d in deps_order:
                if d == "honeycomb" or d == "integration":
                    continue
                whandle.write(d + "\n")
    except IOError:
        print("Error on opening file: {0}".format(output_file))
        sys.exit(1)

    rhandle.close()
    whandle.close()

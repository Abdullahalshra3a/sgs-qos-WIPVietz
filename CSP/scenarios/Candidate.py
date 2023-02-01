#- * - coding: utf - 8
# Created By: Frauke Oest

import networkx as nx
'''Objects of this class hold the information necessary for one solution candidate'''

class Candidate():


    def __init__(self, server, ot_device):
        self.server = server
        self.ot_device = ot_device
        self.multipaths = []
        self.bitrate_sc = None
        self.latency_sc = []
        self.bitrate_factor = None
        self.num_connections = None
        self.overlay_topology = None
        self.overlay_connection = None

    '''ad a single bitrate_graph or a list of bitrate graphs'''
    def add_bitrate_graph(self, bitrate_graph):
        if isinstance(bitrate_graph, nx.Graph):
            self.bitrate_sc = bitrate_graph
        else:
            self.bitrate_sc = bitrate_graph[0].copy()
            for i in range(len(bitrate_graph) - 1):
                self.bitrate_sc.add_edges_from(
                    self.combine_graphs(self.bitrate_sc, bitrate_graph[i + 1]))

    def bitrate_graph_to_array(self):
        np_array = nx.to_numpy_array(self.bitrate_sc, weight='weight')
        int_array = np_array.astype(int)
        return int_array.tolist()

    def combine_graphs(self, G, H):
        """merges two graphs to create one larger graph from e.g., path graphs"""
        for u, v, d in H.edges(data=True):
            # self.bitrate_sc[u][v]["weight"] = bitrate_graph[i+1]
            attr = dict((key, value) for key, value in d.items())
            # get data from G or use empty dict if no edge in G
            gdata = G[u].get(v, {})
            # add data from g
            # sum shared items
            shared = set(gdata) & set(d)
            # update_attr = dict((key, attr[key] + gdata[key]) for key in shared)
            if len(shared) > 0:
                update_w = attr['weight'] + gdata['weight']
                update_attr_weight = {'weight': update_w,
                                      'lat': gdata['lat']}
                attr.update(update_attr_weight)
            # # non shared items
            non_shared = set(gdata) - set(d)
            attr.update(dict((key, gdata[key]) for key in non_shared))
            yield u, v, attr
        return

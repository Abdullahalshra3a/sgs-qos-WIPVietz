import networkx as nx
import itertools

import matplotlib

matplotlib.use('tkagg')
import matplotlib.pyplot as plt
from re import search
import util



class SgsGraph(nx.Graph):

    def __init__(self, data=None, servers=None, **attr):
        super(SgsGraph, self).__init__()
        self.servers = servers


    def compose_end_to_end_connection(self, list1, list2):
        all_list = []
        for node in itertools.product(list1, list2):
            if node[0] != node[1]:
                exists = False
                for item in all_list:
                    if node[0] == item[1] and node[1] == item[0]:
                        exists = True
                if not exists:
                    # print(node)
                    all_list.append(node)
        return all_list

    def calc_all_overlay_paths(self, list_hosts, list_hosts2):
        # phys_graph, array, servers = config_mini_FAU_graph_paper(edge_l=30, sub_l=25, core_l=20, edge_br=25)
        # list_devices = ['F11', 'F12', 'F13', 'F14', 'F15', 'F16', 'F21', 'F22', 'F23', 'F24', 'F25', 'F26', 'F31',
        #                 'F32',
        #                 'F33', 'F34', 'F35']
        # list_devices2 = ['F11', 'F12', 'F34', 'F35']
        # list_servers = ['S1', 'S2']
        # full_nodes = list_servers + list_devices
        #
        # example_overlay_topology = ['F13', 'F14', 'F25', 'F31']
        all_list = self.compose_end_to_end_connection(list_hosts, list_hosts2)
        print(f'all combinations: {len(all_list)}')

        count_all_paths = 0

        for node1, node2 in all_list:
            paths = list(nx.all_simple_paths(self, node1, node2, cutoff=None))
            print(f'pair {node1}, {node2} has {len(paths)} paths')
            # print(paths[0])
            count_all_paths += len(paths)
        print(f'all_paths: {count_all_paths}')

    def get_adj_matrix(self, edge_attr='weight'):
        G_array = nx.to_numpy_array(self, weight='weight')
        int_array = G_array.astype(int)
        return int_array

    def show_PhysGraph(G):
        pos = nx.get_node_attributes(G, 'pos')
        color_map = []
        figure_size_p = (16, 6)
        figure = plt.figure(num="Physical Graph", figsize=figure_size_p)
        for node in G:
            if search("R\d+", node):
                color_map.append('lightgray')
            elif search("^S\d+", node):
                color_map.append('lightblue')
            else:
                color_map.append('lightgreen')

        nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=800, font_size=12,
                node_color=color_map)
        weight_labels = nx.get_edge_attributes(G, 'weight')
        latency_labels = nx.get_edge_attributes(G, 'lat')
        mixed_label = weight_labels.copy()
        for key, value in mixed_label.items():
            mixed_label[key] = (weight_labels[key] / 1000, latency_labels[key])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=mixed_label, font_size=12)

        plt.show()


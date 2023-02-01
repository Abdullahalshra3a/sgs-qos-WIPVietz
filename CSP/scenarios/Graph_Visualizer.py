#- * - coding: utf - 8
# Created By: Frauke Oest

'''This class provides functionality for multiple result visualization functions'''

import networkx as nx
import matplotlib

matplotlib.use('tkagg')
import matplotlib.pyplot as plt
from re import search
import numpy as np
from Config import RESULT_PATH


class GraphVisualizer:

    def __init__(self, phys_graph):
        self.phys_graph = phys_graph
       # self.picture_path = "result_figures/"
        self.picture_path = RESULT_PATH

    def show_solution_with_substracted_physical_graph(self, sgs_results,
                                                      show_individual_windows=False, scenario={}):
        '''visualizes the feasibility of the bitrate constraint by substracting the edge weights of the solutions from
        the physical graph'''
        num_of_results = len(sgs_results)

        for key, value in sgs_results.items():
            visible_graph = self.subtract_subgraphs_from_physgraph(value.bitrate_sc,
                                                                   value.bitrate_factor)

        if show_individual_windows:
            figures = []
            figure_size_p = (10, 8)
            figure_size_sgs = (10, 6)
            figures.append(plt.figure(num="Physical Graph", figsize=figure_size_p))
            filesuffix = "_" + scenario['mode'] + "_" + scenario['degragation']
            self.draw_graph(visible_graph, ax=None, title="Physical Graph", is_subgraph=False)
            plt.savefig(self.picture_path + "Physical_Graph" + filesuffix + ".png")
            for key, value in sgs_results.items():
                figures.append(plt.figure(num=key, figsize=figure_size_sgs))
                self.draw_graph(value.bitrate_sc, ax=None, title=key, is_subgraph=True,
                                bitrate_factor=value.bitrate_factor, multipaths=value.multipaths,
                                show_edge_weights=True, edge_color='k')
                plt.savefig(self.picture_path + key + filesuffix + ".png")
        else:
            fig, ax = plt.subplots(nrows=1, ncols=num_of_results + 1)
            self.draw_graph(visible_graph, ax[0], "Physical Graph", is_subgraph=False)
            ax_ids = 1
            for key, value in sgs_results.items():
                print(f'selected server: {value.server} for SGS: {key}')
                self.draw_graph(value.bitrate_sc, ax[ax_ids], key, is_subgraph=True,
                                # @TODO Doppelter Aufruf vermeiden
                                bitrate_factor=value.bitrate_factor, multipaths=value.multipaths,
                                show_edge_weights=True, edge_color='k')
                ax_ids += 1
        plt.show()

    def show_aggregated_scenario_solutions(self, experiments, show_plots=True):
        '''Visualizes the topology of each experiment for each SGS. The experiment number is associated on the edges'''
        figures = []
        #  figure_size_p = (10, 8)
        # figure_size_sgs = (4, 6)

        transformed_results = dict()
        result_dict = dict()
        for e in experiments:
            if experiments[e]['result'] == None:
                print("failed at experiment: ", experiments[e])
            else:
                for tag, result in experiments[e]['result'].items():
                    # print(tag)
                    if tag in transformed_results.keys():
                        result_dict = transformed_results[tag].copy()
                        result_dict[e] = result
                        transformed_results[tag] = result_dict
                    else:
                        transformed_results[tag] = {1: result}
            for sgs, value in transformed_results.items():
                self.aggregate_solutions(value, sgs)
        if show_plots:
            plt.show()

    def aggregate_solutions(self, results, tag):
        # edge_colors = ['r', 'b', 'g', 'k']
        figure_size_sgs = (12, 6)
        label_value = dict()
        F = nx.Graph()

        for e in results:
            G = results[e].bitrate_sc
            G.remove_nodes_from(list(nx.isolates(G)))
            F = nx.compose(F, G)
            weight = nx.get_edge_attributes(G, 'weight')

            for key, value in weight.items():
                if not label_value or key not in label_value:
                    label_value[key] = [e]
                else:
                    # print("edge key: ", key)
                    # print("edge label: ", value)
                    value_ = label_value[key]
                    value_.append(e)
                    label_value[key] = value_

        pos = nx.get_node_attributes(F, 'pos')
        label_strings = label_value.copy()
        for key, value in label_value.items():
            label_strings[key] = ','.join(str(e) for e in value)
        # print("nodes of F:", F.nodes)
        # print("edges of F: ", F.edges)
        color_map = self.create_colormap(F)
        plt.figure(num=tag, figsize=figure_size_sgs)
        nx.draw(F, pos, with_labels=True, font_weight='bold', node_size=800, font_size=12,
                 node_color=color_map)

        nx.draw_networkx_edges(F, pos, width=3)
        nx.draw_networkx_edge_labels(F, pos, edge_labels=label_strings, font_size=12)
        plt.savefig(self.picture_path + tag + "_aggregated.png")
        print(tag)



    def subtract_subgraphs_from_physgraph(self, subgraph, bitrate_factor):
        visible_graph = self.phys_graph.copy()
        for source, sink, weight in subgraph.edges(data=True):
            #    print(source, sink, br)
            original_weight = visible_graph[source][sink]['weight']
            visible_graph[source][sink]['weight'] = original_weight - bitrate_factor * weight[
                'weight']
            # phys_graph[source][sink]['weight'] = original_weight - weight['weight']
        subgraph.remove_nodes_from(list(nx.isolates(subgraph)))
        return visible_graph

    def create_colormap(self, G):
        '''colors field nodes into green, server nodes into blue, and router nodes into gray '''
        color_map = []
        for node in G:
            if search("R\d+", node):
                color_map.append('lightgray')
            elif search("^S\d+", node):
                color_map.append('lightblue')
            else:
                color_map.append('lightgreen')
        return color_map

    def draw_graph(self, G, ax, title, is_subgraph=False, bitrate_factor=None, multipaths=None,
                   edge_color='k', show_edge_weights=True):
        pos = nx.get_node_attributes(G, 'pos')
        paths = multipaths
        color_map = self.create_colormap(G)
        # print("nodes", G.nodes)
        # nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=800, font_size=8,
        #         node_color=color_map)
        nx.draw(G, pos, with_labels=True, font_weight='bold', ax=ax, node_size=300, font_size=8,
                node_color=color_map, edge_color=edge_color)

        H = G.copy()

        if is_subgraph:
            # @TODO colorieren von overlay topologien
            for path in paths:
                source = path[0]
                sink = path[len(path) - 1]
                # print(f'source: {source} and sink: {sink}')
                # print(f'complete path {path}')
            #     H.add_edges_from([(source, sink, color='blue', {"weight": 1, "lat": 1})])
            #     #H.add_edge(source, sink, color='b')

            weight_labels = nx.get_edge_attributes(H, 'weight')
            latency_labels = nx.get_edge_attributes(H, 'lat')
            mixed_label = weight_labels.copy()
            for key, value in mixed_label.items():
                mixed_label[key] = (weight_labels[key] * bitrate_factor, latency_labels[key])
                # mixed_label[key] = (weight_labels[key], latency_labels[key])

        else:
            weight_labels = nx.get_edge_attributes(H, 'weight')
            latency_labels = nx.get_edge_attributes(H, 'lat')
            mixed_label = weight_labels.copy()
            for key, value in mixed_label.items():
                mixed_label[key] = (weight_labels[key], latency_labels[key])
        if not show_edge_weights:
            mixed_label = {}
        if ax is not None:
            ax.title.set_text(title)
            nx.draw_networkx_edge_labels(H, pos, edge_labels=mixed_label, ax=ax, font_size=6)

        else:
            nx.draw_networkx_edge_labels(H, pos, edge_labels=mixed_label)

# def MG_example():
#     G = nx.Graph()
#     G.add_edge(1, 2, color='r')
#     G.add_edge(2, 3, color='b')
#     G.add_edge(3, 4, color='g')
#     G.add_edge(1, 2, color='k')
#
#     pos = nx.circular_layout(G)
#
#     H = G.copy()
#     posH = dict()
#     for i in pos:
#         posH[i] =  [pos[i][0] , pos[i][1] - 0.03]
#     pass
#     colors = []
#     for (u, v, attrib_dict) in list(G.edges.data()):
#         colors.append(attrib_dict['color'])
#
#     nx.draw(G, pos, edge_color=colors, node_shape="s", connectionstyle='arc3, rad = 0.1')
#    # nx.draw(G, pos, edge_color=colors, node_shape="s", with_labels=True)
#  #   nx.draw(H, posH, node_shape="s")
#  #   nx.draw_networkx_nodes(H, posH, node_shape="s", alpha=0)
#     nx.draw_networkx_edges(H, posH)
#     plt.show()
#
# MG_example()
#

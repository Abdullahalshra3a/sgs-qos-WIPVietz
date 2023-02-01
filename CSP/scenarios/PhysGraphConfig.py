# - * - coding: utf - 8
# Created By: Frauke Oest
import math

import networkx as nx
import numpy as np
import matplotlib

matplotlib.use('tkagg')
import matplotlib.pyplot as plt
from re import search
import util


def config_micrograph(bitrate_factor=10):
    G = nx.Graph()
    G.add_node('S1', pos=(2, 0))
    G.add_node('B', pos=(1, 3))
    G.add_node('C', pos=(0, 1))
    G.add_node('R1', pos=(2, 2))
    G.add_node('R2', pos=(1, 1))
    G.add_node('R3', pos=(1, 2))

    eth = bitrate_factor
    lat = 1
    G.add_edges_from(
        [('S1', 'R1', {"weight": eth * 10, "lat": 5 * lat}), ('R1', 'R2', {"weight": eth * 3, "lat": 4 * lat})
            , ('R1', 'R3', {"weight": eth * 10, "lat": 3 * lat}), ('B', 'R3', {'weight': eth * 10, "lat": 5 * lat}),
         ('C', 'R2', {'weight': eth * 10, 'lat': 4 * lat}), ('R3', 'R2', {'weight': eth * 10, 'lat': 6 * lat})])

    G_array = nx.to_numpy_array(G, weight='weight')
    # print(G_array)
    int_array = G_array.astype(int)
    # print(int_array)
    servers = ["S1", "S2"]
    return G, int_array, servers


def config_basic_graph(bitrate_factor=10, latency_factor=5):
    G = nx.Graph()
    G.add_node('R10', pos=(6, 6))
    G.add_node('R11', pos=(5, 7))
    G.add_node('R12', pos=(3.5, 8))
    G.add_node('R13', pos=(3.5, 6))
    G.add_node('S1', pos=(3.5, 10))

    G.add_node('PDA11', pos=(2.5, 9))
    G.add_node('RTU11', pos=(2.5, 7))
    G.add_node('CLS11', pos=(2.5, 5))
    G.add_node('RTU12', pos=(3, 4))
    G.add_node('RTU13', pos=(6, 8.5))
    G.add_node('CLS12', pos=(7, 7))

    G.add_node('R30', pos=(7, 4.5))
    #  G.add_node('R31', pos=(5, 4))
    G.add_node('R31', pos=(8, 3))
    # G.add_node('R32', pos=(8, 2))
    G.add_node('R32', pos=(6, 3))
    # G.add_node('S3', pos=(9, 3))

    G.add_node('RTU31', pos=(4.5, 4))
    G.add_node('RTU32', pos=(4.5, 2))
    G.add_node('RTU33', pos=(9, 4))
    G.add_node('RTU34', pos=(10, 3))
    G.add_node('CLS31', pos=(9, 2))

    G.add_node('R20', pos=(8, 6))
    G.add_node('R21', pos=(9, 7))
    G.add_node('R22', pos=(10, 8))
    G.add_node('R23', pos=(10, 6))
    G.add_node('R24', pos=(11, 7))
    G.add_node('S2', pos=(9, 9))

    G.add_node('CLS21', pos=(10, 10))
    G.add_node('RTU21', pos=(11, 9))
    G.add_node('RTU22', pos=(12, 8))
    G.add_node('CLS22', pos=(12, 6))
    G.add_node('RTU23', pos=(11, 5))
    G.add_node('PDA21', pos=(9, 5))

    # G_array = nx.to_numpy_array(G, weight='weight')
    servers = ["S1", "S2", "S3"]
    #  print(G_array)
    return G, [], servers


def config_mini_graph(bitrate_factor=10, latency_factor=5):
    eth = bitrate_factor * 10
    lat = 1 * latency_factor
    G, G_array, servers = config_basic_graph(bitrate_factor=bitrate_factor, latency_factor=latency_factor)

    G.add_edges_from(
        [('R10', 'R11', {"weight": eth * 1, "lat": lat}), ('R11', 'R12', {"weight": eth * 0.7, "lat": lat}),
         ('R11', 'R13', {"weight": eth * 1, "lat": lat}), ('R12', 'R13', {"weight": eth * 1, "lat": lat})
         ])
    G.add_edges_from(
        [('R12', 'S1', {"weight": eth * 1, "lat": lat}), ('R13', 'CLS11', {"weight": eth * 1, "lat": lat}),
         ('R11', 'CLS12', {"weight": eth * 1, "lat": lat}), ('R12', 'PDA11', {"weight": eth * 1, "lat": lat}),
         ('R13', 'RTU11', {"weight": eth * 1, "lat": lat}), ('R13', 'RTU12', {"weight": eth * 1, "lat": lat}),
         ('R11', 'RTU13', {"weight": eth * 1, "lat": lat})])

    G.add_edges_from(
        [('R20', 'R21', {"weight": eth * 1, "lat": lat}), ('R20', 'R22', {"weight": eth * 1, "lat": lat}),
         ('R20', 'R23', {"weight": eth * 1, "lat": lat}), ('R21', 'R22', {"weight": eth * 1, "lat": lat}),
         # ('R23', 'R24', {"weight": eth * 1, "lat": lat}),
         ('R10', 'R20', {"weight": eth * 1, "lat": lat}), ('R21', 'R23', {"weight": eth * 1, "lat": lat})])

    # G.add_edges_from(
    #     [('R30', 'R31', {"weight": eth * 1, "lat": lat}), ('R31', 'R32', {"weight": eth * 1, "lat": lat}),
    #      ('R31', 'R33', {"weight": eth * 1, "lat": lat}), ('R32', 'R34', {"weight": eth * 1, "lat": lat}),
    #      ('R33', 'R34', {"weight": eth * 1, "lat": lat}), ('R30', 'R20', {"weight": eth * 1, "lat": lat})])
    # #  ('R30', 'R33', {"weight": eth * 1, "lat":  lat})])

    G.add_edges_from(
        [('S2', 'R21', {"weight": eth * 1, "lat": lat}), ('R22', 'CLS21', {"weight": eth * 1, "lat": lat}),
         ('R22', 'RTU21', {"weight": eth * 1, "lat": lat}), ('R22', 'RTU22', {"weight": eth * 1, "lat": lat}),
         ('R23', 'CLS22', {"weight": eth * 1, "lat": lat}), ('R23', 'RTU23', {"weight": eth * 1, "lat": lat}),
         ('R23', 'PDA21', {"weight": eth * 1, "lat": lat})])

    G.remove_node('R30')
    G.remove_node('R32')
    G.remove_node('R31')
    G.remove_node('RTU31')
    G.remove_node('RTU32')
    G.remove_node('RTU33')
    G.remove_node('RTU34')
    G.remove_node('CLS31')
    G.remove_node('R24')
    G_array = nx.to_numpy_array(G, weight='weight')
    servers = ["S1", "S2"]
    int_array = G_array.astype(int)
    #  print(G_array)
    return G, int_array, servers


def config_Fau_graph(edge_lat, subnetwork_lat, core_lat, edge_br):
    H, H_array, servers = config_basic_graph(bitrate_factor=10, latency_factor=2)
    G = nx.Graph()
    h_nodes = H.copy().nodes(data=True)
    G.add_nodes_from(h_nodes)

    eth = 1000  # Byte
    lat = 10  # millisecons

    core_data_rate = 200e3  # [kByte/s]
    sub_data_rate = 100e3  # [kByte/s]
    edge_data_rate = edge_br * 1000  # [kByte/s]

    # # Those values are calculated such that the given link delays (20, 25, 30 ms) mirror the transmission delay
    # # formula to calculate link rate: max_packet_size/delay = 255*8 bit / [20, 25, 30]ms
    # core_data_rate = 12.75e3  # 102 kbit/s, 12.75 kByte/s
    # sub_data_rate = 10.2e3  # 81.6 kbit/s
    # edge_data_rate = 8.5e3  # 68 kbit/s

    max_p_size = 255  # [Byte]
    # Those values are calculated such that the given link delays (20, 25, 30 ms) mirror the transmission delay
    # formula to calculate link rate: max_packet_size/delay = 255*8 bit / [20, 25, 30]ms
    core_lat = math.ceil((max_p_size / core_data_rate) * 1000)  # [ms]
    subnetwork_lat = math.ceil((max_p_size / sub_data_rate) * 1000)  # [ms]
    edge_lat = math.ceil((max_p_size / edge_data_rate) * 1000)  # [ms]

    subnetwork_edges = {"weight": sub_data_rate, "lat": subnetwork_lat}
    edge_edges = {"weight": edge_data_rate, "lat": edge_lat}
    core_edges = {"weight": core_data_rate, "lat": core_lat}

    G.add_edges_from(
        [('R10', 'R11', subnetwork_edges), ('R11', 'R12', subnetwork_edges),
         ('R11', 'R13', subnetwork_edges), ('R12', 'R13', subnetwork_edges),
         ('R10', 'R20', core_edges)
         ])
    G.add_edges_from(
        [('R12', 'S1', edge_edges), ('R13', 'CLS11', edge_edges),
         ('R11', 'CLS12', edge_edges), ('R12', 'PDA11', edge_edges),
         ('R13', 'RTU11', edge_edges), ('R13', 'RTU12', edge_edges),
         ('R11', 'RTU13', edge_edges)])

    G.add_edges_from(
        [('R30', 'R31', subnetwork_edges),  # ('R21', 'R22', subnetwork_edges),
         ('R30', 'R32', subnetwork_edges),  # ('R31', 'R32', subnetwork_edges),
         ('R10', 'R30', core_edges), ('R31', 'R32', subnetwork_edges)])
    G.add_edges_from(
        [  # ('S3', 'R31', edge_edges),
            ('R31', 'CLS31', edge_edges),
            ('RTU31', 'R32', edge_edges), ('RTU32', 'R32', edge_edges),
            ('RTU33', 'R31', edge_edges), ('RTU34', 'R31', edge_edges)])

    G.add_edges_from(
        [('R20', 'R21', subnetwork_edges), ('R21', 'R22', subnetwork_edges),
         ('R21', 'R23', subnetwork_edges), ('R22', 'R24', subnetwork_edges),  # neu
         ('R23', 'R24', subnetwork_edges), ('R20', 'R30', core_edges)
         ])
    #  ('R30', 'R33', {"weight": eth * 1, "lat":  lat})])

    G.add_edges_from(
        [('S2', 'R21', edge_edges), ('R22', 'CLS21', edge_edges),
         ('R22', 'RTU21', edge_edges), ('R24', 'RTU22', edge_edges),
         ('R24', 'CLS22', edge_edges), ('R24', 'RTU23', edge_edges),
         ('R23', 'PDA21', edge_edges)])

    G_array = nx.to_numpy_array(G, weight='weight')

    return G, G_array, servers


def config_mini_FAU_graph():
    G = nx.Graph()
    G.add_node('R10', pos=(4, 4))
    G.add_node('S1', pos=(2, 7))

    G.add_node('PDA11', pos=(1, 5))
    G.add_node('RTU11', pos=(0, 4))
    G.add_node('CLS11', pos=(0, 3))
    G.add_node('RTU12', pos=(0, 2))
    G.add_node('RTU13', pos=(2, 2))
    G.add_node('CLS12', pos=(3, 3))

    G.add_node('R20', pos=(5, 3))
    G.add_node('S2', pos=(7, 1))

    G.add_node('RTU21', pos=(4, 2))
    G.add_node('RTU22', pos=(3, 1))
    G.add_node('RTU23', pos=(5, 1))
    G.add_node('RTU24', pos=(6, 1))
    G.add_node('CLS21', pos=(7, 1))

    G.add_node('R30', pos=(6, 6))
    G.add_node('S3', pos=(3, 7))

    G.add_node('CLS31', pos=(9, 8))
    G.add_node('RTU31', pos=(10, 7))
    G.add_node('RTU32', pos=(10, 6))
    G.add_node('CLS32', pos=(10, 5))
    G.add_node('RTU33', pos=(10, 4))
    G.add_node('PDA31', pos=(8, 4))

    eth = 10 * 1000  # Byte
    lat = 10  # millisecons
    G.add_edges_from(
        [('R10', 'S1', {"weight": eth * 3, "lat": lat}), ('R10', 'CLS11', {"weight": eth * 3, "lat": lat}),
         ('R10', 'CLS12', {"weight": eth * 3, "lat": lat}), ('R10', 'PDA11', {"weight": eth * 3, "lat": lat}),
         ('R10', 'RTU11', {"weight": eth * 3, "lat": lat}), ('R10', 'RTU12', {"weight": eth * 3, "lat": lat}),
         ('R10', 'RTU13', {"weight": eth * 3, "lat": lat}), ('R10', 'R20', {"weight": eth * 10, "lat": lat}),
         ('R10', 'R30', {"weight": eth * 10, "lat": lat})])
    G.add_edges_from(
        [('S2', 'R20', {"weight": eth * 3, "lat": lat}), ('R20', 'CLS21', {"weight": eth * 3, "lat": lat}),
         ('RTU21', 'R20', {"weight": eth * 3, "lat": lat}), ('RTU22', 'R20', {"weight": eth * 3, "lat": lat}),
         ('RTU23', 'R20', {"weight": eth * 3, "lat": lat}), ('RTU24', 'R20', {"weight": eth * 3, "lat": lat}),
         ('R20', 'R30', {"weight": eth * 10, "lat": lat})])

    G.add_edges_from(
        [('S3', 'R30', {"weight": eth * 3, "lat": lat}), ('R30', 'CLS31', {"weight": eth * 3, "lat": lat}),
         ('R30', 'RTU31', {"weight": eth * 3, "lat": lat}), ('R30', 'RTU32', {"weight": eth * 3, "lat": lat}),
         ('R30', 'CLS32', {"weight": eth * 3, "lat": lat}), ('R30', 'RTU33', {"weight": eth * 3, "lat": lat}),
         ('R30', 'PDA31', {"weight": eth * 3, "lat": lat})])

    G_array = nx.to_numpy_array(G, weight='weight')
    servers = ["S1", "S2", "S3"]
    return G, G_array, servers


def config_mini_FAU_graph_paper(edge_l, sub_l, core_l, edge_br):
    G, G_array, servers = config_Fau_graph(edge_l, sub_l, core_l, edge_br)
    eth = 10 * 1000  # Byte
    lat = 10  # millisecons
    # G.remove_node("S3")
    mapping = {'PDA11': 'F11',
               'RTU11': 'F12',
               'CLS11': 'F13',
               'RTU12': 'F14',
               'RTU13': 'F15',
               'CLS12': 'F16',

               'RTU31': 'F31',
               'RTU32': 'F32',
               'RTU33': 'F33',
               'RTU34': 'F34',
               'CLS31': 'F35',

               'CLS21': 'F21',
               'RTU21': 'F22',
               'RTU22': 'F23',
               'CLS22': 'F24',
               'RTU23': 'F25',
               'PDA21': 'F26',
               }
    G = nx.relabel_nodes(G, mapping)
    servers = ["S1", "S2"]
    int_graph = G_array.astype(int)
    return G, int_graph, servers


def config_mini_FAU_graph_mini():
    G = nx.Graph()
    G.add_node('R10', pos=(4, 4))
    G.add_node('S1', pos=(2, 7))

    G.add_node('PDA11', pos=(1, 5))
    G.add_node('CLS11', pos=(0, 3))
    G.add_node('CLS12', pos=(3, 3))

    # G.add_node('R20', pos=(5, 3))
    G.add_node('S2', pos=(7, 1))
    G.add_node('CLS21', pos=(7, 1))

    # G.add_node('R30', pos=(6, 6))
    G.add_node('S3', pos=(3, 7))

    G.add_node('CLS31', pos=(9, 8))
    G.add_node('CLS32', pos=(10, 5))
    G.add_node('PDA31', pos=(8, 4))

    eth = 100  # Byte
    lat = 10  # millisecons
    G.add_edges_from(
        [('R10', 'S1', {"weight": eth * 3, "lat": lat}), ('R10', 'CLS11', {"weight": eth * 3, "lat": lat}),
         ('R10', 'CLS12', {"weight": eth * 3, "lat": lat}), ('R10', 'PDA11', {"weight": eth * 3, "lat": lat})  # ,
         # ('R10', 'R20', {"weight": eth * 10, "lat":  lat})#,
         # ('R10', 'R30', {"weight": eth * 10, "lat": lat})
         ])
    G.add_edges_from(
        [('S2', 'R10', {"weight": eth * 3, "lat": lat}), ('R10', 'CLS21', {"weight": eth * 3, "lat": lat})  # ,
         # ('R20', 'R30', {"weight": eth * 10, "lat": lat})
         ])

    G.add_edges_from(
        [('S3', 'R10', {"weight": eth * 3, "lat": lat}), ('R10', 'CLS31', {"weight": eth * 3, "lat": lat}),
         ('R10', 'CLS32', {"weight": eth * 3, "lat": lat}), ('R10', 'PDA31', {"weight": eth * 3, "lat": lat})])

    G_array = nx.to_numpy_array(G, weight='weight')
    servers = ["S1", "S2", "S3"]

    return G, G_array, servers


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


def calc_all_overlay_paths():
    phys_graph, array, servers = config_mini_FAU_graph_paper(edge_l=30, sub_l=25, core_l=20, edge_br=25)
    list_devices = ['F11', 'F12', 'F13', 'F14', 'F15', 'F16', 'F21', 'F22', 'F23', 'F24', 'F25', 'F26', 'F31', 'F32',
                    'F33', 'F34', 'F35']
    list_devices2 = ['F11', 'F12', 'F34', 'F35']
    list_servers = ['S1', 'S2']
    full_nodes = list_servers + list_devices

    example_overlay_topology = ['F13', 'F14', 'F25', 'F31']
    all_list = util.compose_end_to_end_connection(example_overlay_topology, example_overlay_topology)
    print(f'all combinations: {len(all_list)}')

    count_all_paths = 0

    for node1, node2 in all_list:
        paths = list(nx.all_simple_paths(phys_graph, node1, node2, cutoff=None))
        print(f'pair {node1}, {node2} has {len(paths)} paths')
        # print(paths[0])
        count_all_paths += len(paths)
    print(f'all_paths: {count_all_paths}')


if __name__ == '__main__':
    # G, array, servers = config_mini_FAU_graph_paper(edge_l=30, sub_l=25, core_l=20, edge_br=25)
    # show_PhysGraph(G)
    # G, array, servers = config_mini_graph()
    # print(array)
    # show_PhysGraph(G)
    # calc_all_overlay_paths()

    # G, array, servers = config_Fau_graph(edge_lat=30, subnetwork_lat=25, core_lat=20, edge_br=25)
    G, phys_adj_array, servers = config_mini_FAU_graph_paper(edge_l=30, sub_l=25,
                                                             core_l=20, edge_br=25)
    # G, array, servers = config_micrograph()

    # list_field_devices = ['PDA11', 'PDA21', 'CLS11', 'CLS12', 'CLS21', 'CLS22', 'RTU12', 'RTU23']
    # connections = util.compose_end_to_end_connection(['S1'], list_field_devices)
    #
    # #print(array)
    #
    # edges = G.edges('PDA11')
    # print(edges)
    # #util.check_overlay_connections(G, connections)
    show_PhysGraph(G)

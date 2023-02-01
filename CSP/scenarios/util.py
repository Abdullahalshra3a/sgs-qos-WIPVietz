import itertools
from enum import Enum
from re import search
from Config import SolverConfig, IctConfig


class Topology(Enum):
    CENTRAL = 1
    DECENTRAL = 2


def get_adj_position(G, node):
    nodes = list(G.nodes(data=False))
    pos = nodes.index(node)
    return pos


def get_node_of_index(G, index):
    nodes = list(G.nodes(data=False))
    name = nodes[index]
    return name


def compose_end_to_end_connection(list1, list2):
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


def check_overlay_connections(G, conns):
    for n1, n2 in conns:
        pos1 = get_adj_position(G, n1)
        pos2 = get_adj_position(G, n2)
        print(f'overlay-connection ({n1},{n2}) is at position ({pos1},{pos2})')


def get_host_position_in_solution(G, node):
    pos = get_adj_position(G, node)
    edge = G.edges(node)
    edge_l = list(edge)
    if edge_l:
        pos2 = get_adj_position(G, edge_l[0][1])
        return pos, pos2
    else:
        return None, None

def map_to_server(single_path_solution, QoS, servers, server_name, num_ot_devices):
        """creates a matrice with for ressources used on servers."""
        if single_path_solution:
            computation = QoS.min_computation / num_ot_devices
            storage = QoS.min_storage / num_ot_devices
            memory = QoS.min_memory / num_ot_devices
        else:
            computation = QoS.min_computation
            storage = QoS.min_storage
            memory = QoS.min_memory
        server_list = []
        if len(server_name) == 0:
            server_id = len(servers) + 1
        else:
            server_id = int(server_name[1:])
        # @TODO vergleich nicht anhand des Server-Bezeichners
        for index, value in enumerate(servers):
            if server_id == index + 1:
                server_list.append([computation, memory, storage])
            else:
                server_list.append([0, 0, 0])

        if len(server_list) != len(servers):
            raise IndexError("server list length does not match number of physical servers")
        return server_list


def check_constraint_satisfiability(result, sgss, G, G_array, servers):
    # latency constraint
    # max_bitrate constraint
    # phys_graph constraint
    # end-geräte constraint
    ##server constraint
    phys_graph = G_array * 0
    list_all_fd_in_G = []
    sum_sgs_server_res = []
    for i in range(len(servers)):
        sum_sgs_server_res.append({"computation": 0,
                          "memory": 0,
                          "storage": 0})
    for node in G:
        if search("F\d+", node):
            list_all_fd_in_G.append(node)
    for sgs in sgss:
        for sgs_name, cand in result.items():
            if sgs.name_tag == sgs_name:
                if max(cand.latency_sc) > sgs.qos.max_latency:
                    raise ValueError(f'Latency Constraint not satisfied at SGS {sgs.name_tag}')
                if cand.bitrate_factor < sgs.qos.min_bitrate:
                    raise ValueError(f'Bitrate constraint not satisfied at SGS {sgs.name_tag}')

                for i, row in enumerate(phys_graph):
                    for j, el in enumerate(row):
                        el += cand.bitrate_graph_to_array()[i][j]

                num_ot_devices = len(sgs.config.field_devices)
                server_solution = map_to_server(False, sgs.qos, servers, cand.server, num_ot_devices)
                for ix in range(len(servers)):
                    sum_sgs_server_res[ix]['computation'] = sum_sgs_server_res[ix]['computation'] + server_solution[ix][0]
                    sum_sgs_server_res[ix]['memory'] = sum_sgs_server_res[ix]['memory'] + server_solution[ix][1]
                    sum_sgs_server_res[ix]['storage'] = sum_sgs_server_res[ix]['storage'] + server_solution[ix][2]
                # phys_graph += cand.bitrate_sc
                '''check if all field devices are in the solution candidate'''
                for fd in sgs.config.field_devices:
                    pos1, pos2 = get_host_position_in_solution(cand.bitrate_sc, fd)
                    if not pos1 or not pos2 or G_array[pos1, pos2] <= 0:
                        pos1, pos2 = get_host_position_in_solution(cand.bitrate_sc, fd)
                        raise ValueError(f'field device {fd} not in solution candidate for {sgs.name_tag}')
                '''check if all servers are in the solution candidate'''
                for s in sgs.config.servers:
                    pos1, pos2 = get_host_position_in_solution(cand.bitrate_sc, s)
                    if not pos1 or not pos2 or G_array[pos1][pos2] <= 0:
                        raise ValueError(f'server {s} not in solution candidate for {sgs.name_tag}')
                '''check if no other field device is in solution candidate'''
                other_fd = [x for x in list_all_fd_in_G if x not in sgs.config.field_devices]
                for not_fd in other_fd:
                    pos1, pos2 = get_host_position_in_solution(cand.bitrate_sc, not_fd)
                    if pos1 and pos2:
                        raise ValueError(f'field device {not_fd} not in {sgs.name_tag}')
                '''check if no other server is in solution candidate'''
                other_server = [x for x in servers if x not in sgs.config.servers]
                for not_server in other_server:
                    pos1, pos2 = get_host_position_in_solution(cand.bitrate_sc, not_server)
                    if pos1 and pos2:
                        raise ValueError(f'server {not_server} not in {sgs.name_tag}')

    for ix, server in enumerate(servers):
        if sum_sgs_server_res[ix]['computation'] > IctConfig.SERVER_RES[server]['cpu']:
            raise ValueError(f'computational constraint in server {server} failed')
        if sum_sgs_server_res[ix]['memory'] > IctConfig.SERVER_RES[server]['mem']:
            raise ValueError(f'memory constraint in server {server} failed')
        if sum_sgs_server_res[ix]['storage'] > IctConfig.SERVER_RES[server]['sto']:
            raise ValueError(f'storage constraint in server {server} failed')


    for i, row in enumerate(phys_graph):
        for j, el in enumerate(row):
            if el > G_array[i][j]:
                raise ValueError('physical bitrate constraint not satisfied')

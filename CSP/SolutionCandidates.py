#- * - coding: utf - 8
# Created By: Frauke Oest

import networkx as nx
import Config
import psutil
import itertools

import util
from util import Topology
from Candidate import Candidate
import logging


class SolutionCandidates():
    def __init__(self, physical_graph, servers, field_devices, bitrate, topology, connectivity, latency):
        self.phyisical_graph = physical_graph
        self.servers = servers
        self.field_devices = field_devices
        self.bitrate = bitrate
        self.topology = topology
        self.connectivity_phi = connectivity
        self.num_max_connections = None
        self.latency = latency
        self.overlay_connections = None
        self.solutions = self.create_all_solution_candidates()
       # self.log = logging.getLogger("my-logger")

    def get_fd_paths(self, server):  # fd = field device
        all_paths = []
        for n in self.field_devices:
            paths = list(
                nx.all_simple_paths(self.phyisical_graph, n, server, cutoff=None))  # cutoff=None
            print("number of paths for server", server, "and fd: ", len(paths))
            all_paths.append(paths)
        return all_paths

    def create_all_solution_candidates(self):
        list_all_candidates = []
        num_conn_central = 0
        num_conn_decentral = 0
        for t in self.topology:
            if t == Topology.CENTRAL:
                num_conn_central = len(self.field_devices)  # TODO in Candidate integrieren
                self.overlay_connections = util.compose_end_to_end_connection(self.servers, self.field_devices)
                for server in self.servers:
                    fd_multi_paths = self.get_fd_paths(server)
                    if Config.SolverConfig.single_path_solution_candidates:
                        fd_candidates = self.create_singlepath_candidates(fd_multi_paths, server)
                        pass
                    else:
                        fd_candidates = self.create_fd_multipath_candidates(fd_multi_paths, server)
                    if fd_candidates:
                        list_all_candidates.extend(fd_candidates)
                        print(f'SolutionCandidate: size of all_candidates: {len(list_all_candidates)}')
                    else:
                        raise ValueError(f'list of solution candidates is empty')
            # return list_all_candidates
            elif t == Topology.DECENTRAL:
                if Config.SolverConfig.single_path_solution_candidates:
                    paths, num_conn_decentral = self.create_overlay_multipaths()
                    dec_candidates = self.create_singlepath_candidates(paths, [])
                    #raise NotImplementedError('to be implemented for topology = decentral')
                else:
                    paths, num_conn_decentral = self.create_overlay_multipaths()
                    #if Config.single_path_solution_candidates:
                    #    pass
                    #else:
                    dec_candidates = self.create_fd_multipath_candidates(paths, [])
                if dec_candidates:
                    list_all_candidates.extend(dec_candidates)
                else:
                    raise ValueError(f'list of solution candidates is empty')

            # return list_all_candidates
            else:
                raise TypeError("Topology-Type not defined")
        self.num_max_connections = max(num_conn_central, num_conn_decentral)
        return list_all_candidates

    def create_overlay_multipaths(self):
        print('print field devices', self.field_devices)
        num_fd = len(self.field_devices)
        k = num_fd
        ring_connections = set()
        # create small world ring
        for i in range(num_fd - 1):
            conn = frozenset([self.field_devices[i], self.field_devices[i + 1]])
            ring_connections.update([conn])
        # close to ring
        conn = frozenset([self.field_devices[num_fd - 1], self.field_devices[0]])
        ring_connections.update([conn])
        #  print(ring_connections)
        # create shortcuts
        direct_connections = set()
        ctr = 2
        for i in range(num_fd):
            for j in range(ctr, k):
                try:
                    conn = frozenset([self.field_devices[i], self.field_devices[j]])
                    print([self.field_devices[i], self.field_devices[j]])
                    direct_connections.update([conn])
                    ctr += 1
                except:
                    print("faulty index")
            ctr = i + 3

        try:
            d_con_copy = direct_connections.copy()
            for j, k in d_con_copy:
                conn = frozenset([j, k])
                ring_connections.update([conn])
                direct_connections.remove(conn)
        except ValueError:
            print(f'not enough values to unpack at {direct_connections}')
            pass
        # random.seed(18) #@TODO Seed entfer
        # for i in range(int(num_fd * self.connectivity_phi)):
        #     ctr = 0
        #     rnd_index = random.randint(0, len(direct_connections)-1)
        #     print("rnd index: ", rnd_index)
        #     for j, k in direct_connections.copy():
        #         print(j, k)
        #         if ctr == rnd_index:
        #             conn = frozenset([j, k])
        #             print(conn)
        #             ring_connections.update([conn])
        #             direct_connections.remove(conn)
        #         ctr += 1
        print(ring_connections)
        self.overlay_connections = [list(x) for x in ring_connections] #TODO die generierung der pfade kann zusammengefasst werden

        all_paths = self.create_overlay_paths(ring_connections)
        num_connections = len(ring_connections)
        return all_paths, num_connections

    def create_overlay_paths(self, overlay_topology):
        all_paths = []
        number_of_paths = 1
        try:
            for i, j in overlay_topology:
                #print("SolutionCandidate: current end-to-end-path", i, j)
                paths = list(nx.all_simple_paths(self.phyisical_graph, i, j, cutoff=None))  # cutoff=None
                all_paths.append(paths)
                number_of_paths *= len(paths)
                print(f'SolutionCandidate: paths per connection{i}, {j}: {len(paths)}')
            print('SolutionCandidate: number cartesian product of paths', number_of_paths)
        except ValueError:
            print(f'SolutionCandidate: ValueError {overlay_topology}')
        return all_paths

    def create_singlepath_candidates(self, multi_paths, server):
        latencies, adjusted_multipaths, adj_bitrate_graphs = self.restrict_paths_by_latency(multi_paths)
        lat = []
        for l in latencies:
            lat += l
        m_path = []
        for m in adjusted_multipaths:
            m_path += m
        br = []
        for b in adj_bitrate_graphs:
            br += b
        list_candidates = self.create_candidates(lat, m_path, br, server)
        return list_candidates

    def restrict_paths_by_latency(self, multi_paths):
        latencies = []
        adj_bitrate_graphs = []

        adjusted_multipaths = []
        for path_options in multi_paths:
            single_path_latency = []
            single_path_bitrate = []
            adjusted_paths = []
            for path in path_options:
                #lat = self.get_latency(path)
                single_path_bitrate.append(self.create_adj_graphs(path))
                single_path_latency.append(self.get_latency(path))

                # if Config.SolverConfig.restrict_search_space_by_latency:
                #     if lat <= self.latency:
                #         print(f'visited ones')
                #         single_path_bitrate.append(self.create_adj_graphs(path))
                #         single_path_latency.append(self.get_latency(path))
                #         adjusted_paths.append(path)
                #     else:
                #         print(f'latency exceeded')
                #
                # else:
                #     print(f'visited unrestricted')
                #     single_path_bitrate.append(self.create_adj_graphs(path))
                #     single_path_latency.append(self.get_latency(path))
                #     adjusted_paths.append(path)
                # adjusted_multipaths.append(adjusted_paths)

            adj_bitrate_graphs.append(single_path_bitrate)
            latencies.append(single_path_latency)
        return latencies, multi_paths, adj_bitrate_graphs


    def create_candidates(self, latencies, adjusted_multipaths, adj_bitrate_graphs, server):
        list_candidates = []
        ctr_list = 0
        stop_generation = Config.SolverConfig.MAX_NUMBER_SOLUTION_CANDIDATES
        prt_interval = Config.SolverConfig.NUMBER_PRINT_INTERVAL
        for element in latencies:
            if ctr_list <= stop_generation - 1:
                candidate = Candidate(server=server, ot_device=self.field_devices)
                candidate.latency_sc = element
                list_candidates.append(candidate)
                ctr_list += 1
                if ctr_list % prt_interval == 0:
                    print("SolutionCandidate: collected solution candidates latency: ", ctr_list)
                    mem1 = psutil.Process().memory_info().rss / (1024 * 1024 * 1024)  # GB
                    print("SolutionCandidate:  memory usage1 : ", mem1)
            else:
                break
        for i, element in enumerate(adjusted_multipaths):
            if i <= stop_generation - 1:
                list_candidates[i].multipaths = element
                list_candidates[i].overlay_connection = [element[0], element[-1]]
                if i % prt_interval == 0:
                    print("SolutionCandidate: collected solution candidates multipaths: ", i)
                    mem2 = psutil.Process().memory_info().rss / (1024 * 1024 * 1024)  # GB
                    print("SolutionCandidate: memory usage2 : ", mem2)
            else:
                break
        for i, element in enumerate(adj_bitrate_graphs):
            if i <= stop_generation -1:
                list_candidates[i].add_bitrate_graph(element)
                if i % prt_interval == 0:
                    print("SolutionCandidate: collected solution candidates bitrates: ", i)
                    mem3 = psutil.Process().memory_info().rss / (1024 * 1024 * 1024)  # GB
                    print("SolutionCandidate: memory usage3 : ", mem3)
            else:
                break
        print(len(list_candidates))
        return list_candidates


    def create_fd_multipath_candidates(self, multi_paths, server):
        latencies, adjusted_multipaths, adj_bitrate_graphs = self.restrict_paths_by_latency(multi_paths)
        print(f'SolutionCandidate: length of latencies {len(latencies)}')
        prod_latencies = itertools.product(*latencies)
        prod_multipaths = itertools.product(*adjusted_multipaths)
        prod_bitrates = itertools.product(*adj_bitrate_graphs)
        list_candidates = self.create_candidates(prod_latencies, prod_multipaths,
                                             prod_bitrates, server)  # itertools.product(*latencies)
        return list_candidates


    def get_latency(self, path):
        latency = 0
        for elem in range(len(path) - 1):
            latency += self.phyisical_graph[path[elem]][path[elem + 1]]['lat']
        return latency


    def create_adj_graphs(self, path):
        subgraph = nx.Graph()
        subgraph.add_nodes_from(self.phyisical_graph.copy().nodes(data=True))

        for elem in range(len(path) - 1):
            # get original latency
            edge_weights = self.phyisical_graph.get_edge_data(path[elem], path[elem + 1])
            # create bitrategraph
            edge = [(path[elem], path[elem + 1], {"weight": 1, "lat": edge_weights['lat']})]  # self.bitrate
            subgraph.add_edges_from(edge)
        return subgraph

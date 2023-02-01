# - * - coding: utf - 8
# Created By: Frauke Oest

'''This creates an interface for minizinc by either using the existing minizinc-python adapter or starting the process
by console. For both modes, an minizinc-model-file is generated based on the scenario configurations.
In CMD-mode the model-instance file is also generate, while in the other case an instance object is configured.'''
import json
import logging
import os
import re
import sys

import numpy as np
from minizinc import Instance, Model, Solver
from Candidate import Candidate
import Config
import util
from Config import IctConfig  # SERVER_RES, S1_RES, S3_RES


# logging.basicConfig(filename="minizinc-python.log", level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

class MinizincAdapter():
    def __init__(self, all_solutions=True, use_python_adapter=True,
                 existing_file="minizinc_data/network_model.mzn", use_preferences=False):
        self.instance = None
        self.all_solutions = all_solutions
        self.use_py_adapter = use_python_adapter
        self.instance_filename = "minizinc_data/model-instance.dzn"
        self.model_filename = "minizinc_data/network_model.mzn"
        self.existing_model_file = existing_file
        self.use_preferences = use_preferences

    def configure_model(self, physical, servers, sgss, degration, solver="gecode"):
        print("MinizincAdapter: enter configure model method")
        self.degration_mode = degration
        self.sgss = sgss
        physical_graph = physical
        self.solver = solver

        print(f'use solver:{solver}')
        self.instance_filename = f'minizinc_data/model-instance_{self.degration_mode.name}.dzn'
        gecode = Solver.lookup(self.solver)

        if not self.existing_model_file:
            self.create_minizinc_model_file(self.model_filename, sgss)
        else:
            print("MinizincAdapter: use existing model data")
            self.model_filename = self.existing_model_file
        # model = Model("optimize_network_model.mzn")

        server_ressources = []
        for server in servers:
            server_ressources.append([IctConfig.SERVER_RES[server]["cpu"], IctConfig.SERVER_RES[server]["mem"],
                                      IctConfig.SERVER_RES[server]["sto"]])
            pass
        if self.use_py_adapter:
            model = Model(self.model_filename)
            self.instance = Instance(gecode, model)
            self.instance["QoS"] = range(1, 3)
            self.instance["target"] = physical_graph.tolist()
            self.instance["adj_x"] = range(1, len(physical_graph) + 1)
            self.instance["num_servers"] = range(1, len(server_ressources) + 1)
            self.instance["dim_server_res"] = range(1, len(server_ressources[0]) + 1)
            self.instance["server_resources"] = server_ressources
            self.instance["adj_y"] = range(1, len(physical_graph[0]) + 1)

            for sgs in sgss:
                self.instantiate_model(sgs.name_tag, sgs, servers)
        else:
            instance = {"QoS": 2,
                        "target": physical_graph.tolist(),
                        "adj_x": len(physical_graph),
                        "num_servers": len(server_ressources),
                        "dim_server_res": len(server_ressources[0]),
                        "adj_y": len(physical_graph[0]),
                        "server_resources": server_ressources
                        }

            self.create_instance_file(instance, sgss, servers)

    def create_instance_file(self, instance, sgss, servers):
        f = open(self.instance_filename, "w")
        f.write("QoS = 1.." + str(instance["QoS"]) + "; \n")
        print(instance["QoS"])
        f.write("adj_x =  1.." + str(instance["adj_x"]) + "; \n")
        f.write("adj_y =   1.." + str(instance["adj_y"]) + "; \n")
        f.write("num_servers =  1.." + str(instance["num_servers"]) + "; \n")
        f.write("dim_server_res = 1.." + str(instance["dim_server_res"]) + "; \n")
        f.write("server_resources = array2d(num_servers, dim_server_res, " + self.list_to_string(
            instance["server_resources"]) + "); \n")
        f.write(
            "target = array2d(adj_x, adj_y, " + self.list_to_string(instance["target"]) + "); \n")

        for sgs in sgss:
            sgs_inst = self.instantiate_model(sgs.name_tag, sgs, servers)
            f.write(
                "num_options_" + sgs.name_tag + " =  1.." + str(
                    sgs_inst["num_options"]) + "; \n")
            if not Config.SolverConfig.single_path_solution_candidates:
                f.write(f'num_devices_{sgs.name_tag} = 1..{str(sgs_inst["num_devices"])}; \n')
            f.write(f'SC_{sgs.name_tag}_br_factor = 1..{str(sgs.qos.min_bitrate)}; \n')
            f.write(
                f'SC_{sgs.name_tag}_br = array3d(num_options_{sgs.name_tag}, adj_x, adj_y, {self.list_to_string(sgs_inst["bitrate"])}); \n')
            # del sgs_inst["bitrate"]
            if Config.SolverConfig.single_path_solution_candidates:
                f.write(
                    f'SC_{sgs.name_tag}_lat = {self.list_to_string(sgs_inst["latency"])}; \n')
            else:
                f.write(
                    f'SC_{sgs.name_tag}_lat = array2d(num_options_{sgs.name_tag}, num_devices_{sgs.name_tag}, {self.list_to_string(sgs_inst["latency"])}); \n')
            #  del sgs_inst["latency"]
            f.write(
                f'SC_{sgs.name_tag}_serv = array3d(num_options_{sgs.name_tag}, num_servers, dim_server_res, {self.list_to_string(sgs_inst["server"])} ); \n')
            f.write("QoS_" + sgs.name_tag + "= " + str(sgs_inst["QoS"]) + "; \n")

        # del sgs_inst
        f.close()

    def create_minizinc_model_file(self, filename, sgss):
        datatype = "int"  # float
        cwd = os.getcwd()
        # os.chdir("../")
        # files = os.listdir(cwd)
        # print(f'MinizincAdapter: get current files in directory {files}')
        print(f'MinizincAdapter: get cwd {cwd}')
        f = open(filename, "w")
        if self.use_preferences:
            #  f.write("include \"sgs_preferences_o.mzn\"; \n" +
            #          "include \"soft_constraints/minibrass.mzn\"; \n" )
            pass
        f.write("% This file is autogenerated by the class \"MinizincAdapter.py\"\n"
                "set of int: adj_x; \n"
                "set of int: adj_y; \n"
                "set of int: QoS; %bitrate, latency \n"
                "set of int: dim_server_res; \n"
                "set of int: num_servers; \n"
                "\n"
                f"array[adj_x, adj_y] of {datatype}: target; \n"
                "array[num_servers, dim_server_res] of int: server_resources; \n"
                "\n"
                )
        if Config.SolverConfig.single_path_solution_candidates:
            for sgs in sgss:  # ToDo
                tag = sgs.name_tag
                f.write(f"array[QoS] of float: QoS_{tag}; \n" +
                        f"set of int: num_options_{tag}; \n" +
                        f"set of int: SC_{tag}_br_factor; \n"
                        f"array[num_options_{tag}, adj_x, adj_y] of {datatype}: SC_{tag}_br; \n" +
                        f"array[num_options_{tag}] of {datatype}: SC_{tag}_lat; \n" +
                        f"array[num_options_{tag}, num_servers, dim_server_res] of float: SC_{tag}_serv; \n" +
                        "\n"
                        )
        else:
            for sgs in sgss:
                tag = sgs.name_tag
                f.write(f"array[QoS] of float: QoS_{tag}; \n" +
                        f"set of int: num_options_{tag}; \n" +
                        f"set of int: num_devices_{tag}; \n" +
                        f"set of int: SC_{tag}_br_factor; \n"
                        f"array[num_options_{tag}, adj_x, adj_y] of {datatype}: SC_{tag}_br; \n" +
                        f"array[num_options_{tag}, num_devices_{tag}] of {datatype}: SC_{tag}_lat; \n" +
                        f"array[num_options_{tag}, num_servers, dim_server_res] of float: SC_{tag}_serv; \n" +
                        "\n"
                        )

        """define decision variables"""
        f.write(
            "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
            "% Define decision variables.\n"
            "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        for sgs in sgss:
            tag = sgs.name_tag
            tag_l = tag.lower()
            if Config.SolverConfig.single_path_solution_candidates:
                try:
                    for node1, node2 in sgs.solution_candidates.overlay_connections:
                        f.write(f"var num_options_{tag}: x_{tag_l}_{node1}_{node2}; \n")
                except ValueError:
                    print(f'minizincadapter: not enough values to unpack')
                    pass
            else:
                f.write(f"var num_options_{tag}: x_{tag_l}; \n")

        """define QoS variables"""
        f.write(
            "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
            "% Define QoS variables.\n"
            "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        for sgs in sgss:
            tag = sgs.name_tag
            tag_l = tag.lower()
            f.write(f"var SC_{tag}_br_factor: x_{tag_l}_br_factor; \n")

        """define connection exist constraint"""
        f.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                "% Define connection exist constraint.\n"
                "% This constraint enforces that the final connection between the path and the field device or the "
                "server exists.\n"
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        if Config.SolverConfig.single_path_solution_candidates:
            for sgs in sgss:
                tag = sgs.name_tag
                tag_l = tag.lower()
                G = sgs.solution_candidates.phyisical_graph
                conns = sgs.solution_candidates.overlay_connections
                field_devices = sgs.solution_candidates.field_devices
                f_string = "\n"
                for node1, node2 in conns:
                    pos = util.get_adj_position(G, node1) + 1
                    edge = G.edges(node1)
                    edge_l = list(edge)
                    pos_r = util.get_adj_position(G, edge_l[0][1]) + 1
                    f_string += f'constraint (SC_{tag}_br[x_{tag_l}_{node1}_{node2}, {pos}, {pos_r}] > 0); \n'

                    pos = util.get_adj_position(G, node2) + 1
                    edge = G.edges(node2)
                    edge_l = list(edge)
                    pos_r = util.get_adj_position(G, edge_l[0][1]) + 1
                    f_string += f'constraint (SC_{tag}_br[x_{tag_l}_{node1}_{node2}, {pos}, {pos_r}] > 0); \n'
                    # if node1 in field_devices:
                    #     pos = util.get_adj_position(G, node1) +1
                    #     edge = G.edges(node1)
                    #     edge_l = list(edge)
                    #     pos2 = util.get_adj_position(G, edge_l[0][1]) +1
                    #     f_string += f'constraint (SC_{tag}_br[x_{tag_l}_{node1}_{node2}, {pos}, {pos2}] > 0); \n'
                    # elif node2 in field_devices:
                    #     pos = util.get_adj_position(G, node2) +1
                    #     edge = G.edges(node2)
                    #     edge_l = list(edge)
                    #     pos2 = util.get_adj_position(G, edge_l[0][1]) +1
                    #     f_string += f'constraint (SC_{tag}_br[x_{tag_l}_{node1}_{node2}, {pos}, {pos2}] > 0); \n'

                f.write(f_string)

        """define latency constraint"""
        f.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                "% Define latency constraints.\n"
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        if Config.SolverConfig.single_path_solution_candidates:
            for sgs in sgss:
                tag = sgs.name_tag
                tag_l = tag.lower()
                for node1, node2 in sgs.solution_candidates.overlay_connections:
                    f.write(f"constraint (SC_{tag}_lat[x_{tag_l}_{node1}_{node2}] <= QoS_" + tag + "[2]); \n")
        else:
            for sgs in sgss:
                tag = sgs.name_tag
                tag_l = tag.lower()
                f.write(
                    f"constraint forall(i in num_devices_{tag})(SC_{tag}_lat[x_{tag_l}, i] <= QoS_" + tag + "[2]); \n")

        if not self.use_preferences:
            """define hard SGS bitrate QoS constraint"""
            f.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                    "% Define hard SGS bitrate QoS constraint.\n"
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            for sgs in sgss:
                tag = sgs.name_tag
                tag_l = tag.lower()
                f.write(f"constraint (x_{tag_l}_br_factor >= QoS_{tag}[1]); \n")

        """define physical bitrate constraint"""
        f.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                "% Define physical bitrate constraint.\n"
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        f.write("constraint forall(i in adj_x, j in adj_y)(")
        f_string = ""
        for id, sgs in enumerate(sgss):
            tag = sgs.name_tag
            tag_l = tag.lower()
            end_of_constraint = len(sgss) - 1
            if Config.SolverConfig.single_path_solution_candidates:
                conns = sgs.solution_candidates.overlay_connections
                for node1, node2 in conns:
                    f_string += f"SC_{tag}_br[x_{tag_l}_{node1}_{node2}, i, j] * x_{tag_l}_br_factor "
                    f_string += " + "
            else:
                f_string += f"SC_{tag}_br[x_{tag_l}, i, j] * x_{tag_l}_br_factor"
                f_string += " + "
            # f.write(f"SC_{tag}_br[x_{tag_l}, i, j] * x_{tag_l}_br_factor ")
            # if id < end_of_constraint:
            #    f.write(" + ")
        size = len(f_string)
        print(f'MinizincAdapter: {f_string}')
        mod_string = f_string[:size - 2]
        f.write(mod_string)
        f.write(" <= target[i, j]); \n")

        """define server constraints"""
        f.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                "% Define server constraints.\n"
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        f.write("constraint forall(k in num_servers, j in dim_server_res)(")
        f_string = ""
        for id, sgs in enumerate(sgss):
            tag = sgs.name_tag
            tag_l = tag.lower()
            if Config.SolverConfig.single_path_solution_candidates:
                conns = sgs.solution_candidates.overlay_connections
                for node1, node2 in conns:
                    f_string = f_string + f'SC_{tag}_serv[x_{tag_l}_{node1}_{node2}, k, j]'
                    f_string = f_string + " + "

            else:
                f_string += f"SC_{tag}_serv[x_{tag_l}, k, j]"
                f_string = f_string + " + "
                # f.write(f"SC_{tag}_serv[x_{tag_l}, k, j]")
                # if id < end_of_constraint:
                #     f.write(" + ")
        size = len(f_string)
        mod_string = f_string[:size - 2]
        f.write(mod_string)
        f.write(" <= server_resources[k, j]); \n")

        """solve"""
        if self.use_preferences:
            # f.write("\n solve search miniBrass();")
            f.write("\n"
                    "solve satisfy;")
        else:
            f.write("\n"
                    "solve satisfy;")

        f.close()

    def instantiate_model(self, nametag, sgs, servers):
        '''instanciates models for each smart grid service for cmd and api-mode'''
        bitrate_candidates = [solutions.bitrate_graph_to_array() for solutions in
                              sgs.solution_candidates.solutions]

        #   print(f' chosen bitrate candiate {bitrate_candidates[0]}')
        latency_candidates = []
        for solutions in sgs.solution_candidates.solutions:
            if Config.SolverConfig.single_path_solution_candidates:
                latency_candidates = [solutions.latency_sc for solutions in sgs.solution_candidates.solutions]
            else:
                if isinstance(solutions.latency_sc, tuple):
                    if sgs.solution_candidates.num_max_connections > len(solutions.latency_sc):
                        diff = sgs.solution_candidates.num_max_connections - len(solutions.latency_sc)
                        zeros = [0] * diff
                        latency_candidates.append(list(solutions.latency_sc) + zeros)
                    else:
                        latency_candidates.append(list(solutions.latency_sc))
                    # print(f'MinizincAdapter: num_max_connections: {sgs.solution_candidates.num_max_connections}')
                    # latency_candidates.append(solutions.latency_sc)
                else:
                    raise TypeError(f'MinizincAdapter: type should be tuple, but is of {type(solutions.latency_sc)}')
                if len(np.array(latency_candidates).shape) != 2:
                    raise ValueError(
                        f'latency_candidates needs a 2-dim array, but instead a {len(np.array(latency_candidates).shape)} was given.')

        # latency_candidates = [solutions.latency_sc for solutions in
        #                      sgs.solution_candidates.solutions]

        num_ot_devices = len(sgs.config.field_devices)
        server_candidates = [
            util.map_to_server(Config.SolverConfig.single_path_solution_candidates, sgs.qos, servers, solutions.server,
                               num_ot_devices) for solutions in
            sgs.solution_candidates.solutions]

        if len(np.array(bitrate_candidates).shape) != 3:
            raise ValueError(
                f'bitrate_candidates needs a 3-dim array, but instead a {len(np.array(bitrate_candidates).shape)} was given.')
        # print(f'size {len(bitrate_candidates[0])}, {len(bitrate_candidates[0][0])}')
        if not isinstance(latency_candidates, list):
            raise TypeError(
                f'MinizincAdapter: format of latency_candidates must be list, but is of {type(latency_candidates)}')

        if self.use_py_adapter:
            print(f'SGS: {nametag} with num_options: {len(bitrate_candidates)} ')
            # and adjacency matrix {nx.to_numpy_array(bitrate_candidates)}
            self.instance["SC_" + nametag + "_br_factor"] = range(1, sgs.qos.min_bitrate + 5)
            # if config.SolverConfig.single_path_solution_candidates:
            #     for conn in sgs.solution_candidates.overlay_connections:
            #         prefix = f'SC_{nametag}_{conn[0]}_{conn[1]}_'
            #         self.instance[prefix+'br'] = bitrate_candidates
            #         self.instance[prefix+'lat'] = latency_candidates
            #         self.instance[prefix+'serv'] = server_candidates
            #         self.instance["num_devices_" + nametag] = range(1, len(bitrate_candidates) + 1)
            #         print("MinizincAdapter: using prefix ", prefix)
            #     pass
            # else:
            self.instance["SC_" + nametag + "_br"] = bitrate_candidates
            self.instance["SC_" + nametag + "_lat"] = latency_candidates
            self.instance['SC_' + nametag + '_serv'] = server_candidates
            self.instance["num_devices_" + nametag] = range(1, sgs.solution_candidates.num_max_connections + 1)

            self.instance["num_options_" + nametag] = range(1, len(bitrate_candidates) + 1)
            print(f'Minizinc: number of options for SGS {nametag}: {len(bitrate_candidates)}')

            self.instance['SC_' + nametag + '_serv'] = server_candidates
            self.instance['QoS_' + nametag] = sgs.qos.to_list()
        else:
            sgs_instance = dict()
            sgs_instance["bitrate"] = bitrate_candidates
            sgs_instance["num_options"] = len(bitrate_candidates)
            # del bitrate_candidates
            #  print("deleted bitrate candidates")
            sgs_instance["num_devices"] = sgs.solution_candidates.num_max_connections
            sgs_instance["latency"] = latency_candidates
            #  del latency_candidates
            #  print("deleted latency candidates")
            sgs_instance['server'] = server_candidates
            sgs_instance['QoS'] = sgs.qos.to_list()
            return sgs_instance

    def solve_model(self, termination_time=1):
        '''startes solving process in minizinc and chooses the correct solution candidate based on minizinc results'''
        if self.use_py_adapter:
            minizinc_result = self.instance.solve(all_solutions=self.all_solutions)
            if minizinc_result.status.name == "UNSATISFIABLE":
                print("no solution found")
                return None, None
            else:
                if not self.all_solutions:
                    print(minizinc_result)
                    results = {sgs.name_tag: sgs.solution_candidates.solutions[
                        minizinc_result['x_' + sgs.name_tag.lower()] - 1]
                               for sgs in self.sgss}
                    for sgs_sc in results:
                        results[sgs_sc].bitrate_factor = minizinc_result[
                            "x_" + sgs_sc.lower() + "_br_factor"]

                    return results, minizinc_result
                else:
                    print("found ", len(minizinc_result), "solutions; returning the first one")
                    print(minizinc_result[0])
                    results = {sgs.name_tag: sgs.solution_candidates.solutions[
                        minizinc_result[0, 'x_' + sgs.name_tag.lower()] - 1]
                               for sgs in self.sgss}
                    return results, minizinc_result
        else:
            if self.use_preferences:
                path_to_minisearch = "~/Programme/minisearch/build/minisearch"

                path_to_mzn = "~/Programme/minibrass-master/example-problems/nurse-example/nurseHelloWorld.mzn"  # moving.mzn
                path_to_dzn = "~/Programme/minibrass/moving.dzn"
                stream = os.popen(
                    path_to_minisearch + " " + self.model_filename + " " + self.instance_filename)
                output = stream.read()
                print(output)

            else:
                timeout = termination_time * 60
                print(
                    f'solver: {self.solver} with model_file: {self.model_filename} and instance_filename: {self.instance_filename}')
                if self.all_solutions:
                    stream = os.popen(
                        f'minizinc --solver {self.solver} -a -p 4 -t {timeout} {self.model_filename} {self.instance_filename}')
                    output = stream.read()
                    # print(f'print output from minizinc {output}')

                    if output is None or "UNSATISFIABLE" in output:
                        # Abort the further processing if the CSP is unsatisfiable
                        return None

                    # MiniZinc delivers the different CSP solutions separated by ----. Last split is empty and can be removed
                    solutions = output.split("----------\n")
                    del solutions[-1]
                    logging.info(f'number of all solutions: {len(solutions)}')

                    # IMPORTANT: This is an intermediate solution. For the future a more precise way should be used.
                    # One possibility would be to return an iterator over the solutions,
                    # which on the fly builds the networkx elements
                    return solutions

                    # m_results = []
                    # results = []
                    # ctr = 0
                    # # Minizinc solution is in another dataformat. Transform it now to one networkx element (or Config.BUILDING_LIMIT parallel solutions)
                    # for solution in solutions:
                    #     if ctr < Config.BUILDING_LIMIT:
                    #         result, m_result = self.buildNXfromMiniZinc(solution)
                    #         results.append(result)
                    #         m_results.append(m_result)
                    #         ctr += 1
                    # return results, m_results
                else:
                    stream = os.popen(
                        f'minizinc --solver {self.solver} -r 18 {self.model_filename} {self.instance_filename}')

                    output = stream.read()
                    print(f'print output from minizinc {output}')
                    m_result = self.parse_results(output)
                    if m_result:
                        if Config.SolverConfig.single_path_solution_candidates:
                            results = self.build_complete_solution(m_result)
                            # for sgs_sc in results:
                            #    results[sgs_sc].bitrate_factor = m_result["x_" + sgs_sc.lower() + "_br_factor"]
                        else:
                            results = {sgs.name_tag: sgs.solution_candidates.solutions[
                                m_result['x_' + sgs.name_tag.lower()] - 1]
                                       for sgs in self.sgss}
                            for sgs_sc in results:
                                results[sgs_sc].bitrate_factor = m_result["x_" + sgs_sc.lower() + "_br_factor"]
                        # print(results)
                        return results, m_result
                    else:
                        return None, None

    def buildNXfromMiniZinc(self, solution):
        """
        Transform a string list gathered from MiniZinc into a functional solution candidate

        :param solution: Minizinc solution
        :type solution: str
        :return: result, m_result
        :rtype: (dict, list)
        """
        minizinc_parse = self.parse_results(solution)
        m_result = [minizinc_parse]
        if Config.SolverConfig.single_path_solution_candidates:
            logging.debug(f'building complete solutions')
            result = self.build_complete_solution(minizinc_parse)
        else:
            result = {sgs.name_tag: sgs.solution_candidates.solutions[
                minizinc_parse['x_' + sgs.name_tag.lower()] - 1]
                      for sgs in self.sgss}
            # TODO @Frauke: Check those two lines, should be deprecated imo.
            # for sgs_sc in results:
            #     results[sgs_sc].bitrate_factor = minizinc_parse["x_" + sgs_sc.lower() + "_br_factor"]
        return result, m_result

    def build_complete_solution(self, m_results):
        result_dict = dict()
        for key, value in m_results.items():
            for sgs in self.sgss:
                for node1, node2 in sgs.solution_candidates.overlay_connections:
                    if sgs.name_tag.lower() in key and node1 in key and node2 in key:
                        if not sgs.name_tag in result_dict:
                            result_dict[sgs.name_tag] = {(node1, node2): value}
                        else:
                            result_dict[sgs.name_tag][(node1, node2)] = value

        # print(result_dict)
        results = dict()
        for key, elem in result_dict.items():
            for sgs in self.sgss:
                if sgs.name_tag == key:
                    complete_candidate = Candidate(server=None, ot_device=None)
                    for conn, value in elem.items():
                        try:
                            sub_res = sgs.solution_candidates.solutions[value - 1]
                        except IndexError:
                            print(f'MinizincAdapter: IndexError at SGS {sgs.name_tag} with connection {conn} and value {value}')
                        if not complete_candidate.server and not complete_candidate.ot_device:
                            complete_candidate.ot_device = sub_res.ot_device
                            complete_candidate.server = sub_res.server
                            complete_candidate.latency_sc = [sub_res.latency_sc]
                            complete_candidate.multipaths = [sub_res.multipaths]
                            complete_candidate.overlay_connection = [sub_res.overlay_connection]
                            complete_candidate.bitrate_factor = m_results[f'x_{sgs.name_tag.lower()}_br_factor']
                            bitrate_graphs = [sub_res.bitrate_sc]

                        else:
                            complete_candidate.latency_sc.append(sub_res.latency_sc)
                            complete_candidate.multipaths.append(sub_res.multipaths)
                            complete_candidate.overlay_connection.append(sub_res.overlay_connection)
                            complete_candidate.add_bitrate_graph(sub_res.bitrate_sc)
                            bitrate_graphs.append(sub_res.bitrate_sc)
                    complete_candidate.add_bitrate_graph(bitrate_graphs)
                    results[sgs.name_tag] = complete_candidate
                    # print(f'Resulting bitrate_graph: {complete_candidate.bitrate_graph_to_array()}')
        return results

    def parse_results(self, output):
        '''interpretes console output'''
        if "UNSATISFIABLE" in output:
            # This case should not be encountered, because the "solve_model" already checks for UNSATISFIABLE
            return None
        result = re.sub(r'(x_\w*) = (\d*)', r'"\1": \2', output)
        result = re.sub("-*", "", result)
        result = re.sub("\n", "", result)
        result = re.sub(";", ",", result)
        result = '{' + result[:-1] + '}'
        # print(result)
        y = json.loads(result)
        # results = {sgs.name_tag: sgs.solution_candidates.solutions[output.find("x_"+ sgs.name_tag.lower())
        #    result['x_' + sgs.name_tag.lower()] - 1] for sgs in self.sgss}
        return y

    def list_to_string(self, list):
        '''maps multi-dim arrays for minizinc-instance file'''
        ravelled = np.ravel(list)
        string = "["
        for el in ravelled:
            string += str(el) + ", "
        string = string[:-2]
        string += "]"
        return string


if __name__ == "__main__":
    adapter = MinizincAdapter()
    output = 'x_se = 1; \n x_vpp = 2; \n ----------'
    adapter.parse_results(output)

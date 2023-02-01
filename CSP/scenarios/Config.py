#- * - coding: utf - 8
# Created By: Frauke Oest

import PhysGraphConfig

RESULT_PATH = "../results/"  # "../../../Nextcloud2/Diss/Abbildungen/"

serialized_sgs_path = "data/"
BUILDING_LIMIT = 100

class SolverConfig:
    solvers = ['gecode'] #['gecode', 'chuffed', 'coinbc']
    use_python_adapter = False
    single_path_solution_candidates = True

    restrict_search_space_by_latency = True
    MAX_NUMBER_SOLUTION_CANDIDATES = 1000
    NUMBER_PRINT_INTERVAL = 1000
    termination_time = 1 * 10 * 1000 #ms


    SAVE_TO_DISK = True

class IctConfig:
    physical_Graph, phys_adj_array, servers = PhysGraphConfig.config_mini_FAU_graph_paper(edge_l=30, sub_l=25,
                                                                                          core_l=20, edge_br=25)
    CPU_RES = {0: 0,
               1: 500,
               2: 1000,
               3: 4000}
    MEM_RES = {0: 0,
               1: 200,
               2: 2000,
               3: 8000}
    STO_RES = {0: 0,
               1: 500,
               2: 4000,
               3: 16000}

    S1_RES = {"cpu": 6000,
              "mem": 16000,
              "sto": 50000
              }

    S3_RES = {"cpu": 4000,
              "mem": 8000,
              "sto": 20000}

    S2_RES = {"cpu": 4000,
              "mem": 8000,
              "sto": 20000}

    SERVER_RES = {"S1": S1_RES,
                  "S2": S2_RES,
                  "S3": S3_RES}

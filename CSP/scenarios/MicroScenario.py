#- * - coding: utf - 8
# Created By: Frauke Oest

import PhysGraphConfig
import Config
from SmartGridApplication import SmartGridApplication, QoS_Requirements, SGA_config, Topology
from MinizincAdapter import MinizincAdapter
from Graph_Visualizer import GraphVisualizer
import os
from enum import Enum
from Config import SolverConfig

class degregation_mode(Enum):
    TEST = 1

def run_micro_scenario(solver_config = SolverConfig):
    cwd = os.getcwd()  # Get the current working directory (cwd)
    os.chdir("../")
    #files = os.listdir(cwd)  # Get all the files in that directory
    #print("Files in %r: %s" % (cwd, files))
    print(f'MicroScenario: get cwd {cwd}')

    physical_Graph, phys_adj_array, servers = PhysGraphConfig.config_micrograph(bitrate_factor=10)

    se_QoS = QoS_Requirements(bit_rate=3, latency=50, computation=1, storage=1, memory=1)
    se_QoS.min_computation = 5
    se_QoS.min_storage = 5
    se_QoS.min_memory = 5
    se_config = SGA_config(servers=['S1'], field_devices=['B'])
    se_sgs = SmartGridApplication("SE", se_QoS, physical_graph=physical_Graph, config=se_config)

    vpp_QoS = QoS_Requirements(bit_rate=5, latency=50, computation=1, storage=1, memory=1)
    vpp_QoS.min_computation = 5
    vpp_QoS.min_storage = 3
    vpp_QoS.min_memory = 10
    vpp_config = SGA_config(servers=['S1'], field_devices=['C'])
    vpp_sgs = SmartGridApplication("VPP", vpp_QoS, physical_graph=physical_Graph, config=vpp_config)

    # ar_QoS = QoS_Requirements(bit_rate=2, latency=20, computation=1, storage=2, memory=2)
    # ar_QoS.min_computation = 10
    # ar_QoS.min_storage = 20
    # ar_QoS.min_memory = 2
    # ar_config = SGA_config(servers=['S2'], field_devices=['C'])
    # ar_sgs = SmartGridApplication("AR", ar_QoS, physical_graph=physical_Graph, config=ar_config)

    sgss = [se_sgs, vpp_sgs]

    mzn_model = MinizincAdapter(all_solutions=False, use_python_adapter=solver_config.use_python_adapter, existing_file=False)#minizinc_data/network_model.mzn" "minizinc_data/network_model_single.mzn"

    mzn_model.configure_model(phys_adj_array, servers, sgss, degration=degregation_mode.TEST, solver='chuffed')
    #LookupError: No solver id or tag 'findMUS' found, available options: ['api', 'cbc', 'chuffed', 'coin-bc', 'coinbc', 'cp', 'cplex', 'experimental', 'findmus', 'float', 'gecode', 'gist', 'globalizer', 'gurobi', 'int', 'lcg', 'mip', 'org.chuffed.chuffed', 'org.gecode.gecode', 'org.gecode.gist', 'org.minizinc.findmus', 'org.minizinc.globalizer', 'org.minizinc.mip.coin-bc', 'org.minizinc.mip.cplex', 'org.minizinc.mip.gurobi', 'org.minizinc.mip.scip', 'org.minizinc.mip.xpress', 'osicbc', 'restart', 'scip', 'set', 'tool', 'xpress']

    #mzn_model = MinizincAdapter(all_solutions=False, existing_file=None, use_python_adapter=True, use_preferences=False)

    result, m_result = mzn_model.solve_model()
    print(result)
    return result, m_result


run_micro_scenario()

# def run_and_visualize():
#     result, m_result = run_micro_scenario()
#     visualizer = GraphVisualizer(config.IctConfig.physical_Graph)
#     experiments = {
#         1: {"situation": "normal", "degregation": "none", "result": result, "stats": None}}
#     visualizer.show_aggregated_scenario_solutions(experiments, show_plots=True)
#
# if __name__ == '__main__':
#     run_and_visualize()
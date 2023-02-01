#- * - coding: utf - 8
# Created By: Frauke Oest

import PhysGraphConfig
from SmartGridApplication import SmartGridApplication, QoS_Requirements, SGA_config
from MinizincAdapter import MinizincAdapter
from Graph_Visualizer import GraphVisualizer
from SmartGridApplication import Topology
import time
from enum import Enum
import os
from Config import SolverConfig, IctConfig
import Config
import util

class degregation_mode(Enum):
    Mini_Scenario_Test = 1

def run_mini_scenario(solver_config = SolverConfig):
    cwd = os.getcwd()  # Get the current working directory (cwd)
    os.chdir("../")
    #files = os.listdir(cwd)  # Get all the files in that directory
    #print("Files in %r: %s" % (cwd, files))
    #print(f'MicroScenario: get cwd {cwd}')
    start_program = time.time()
    physical_Graph, phys_adj_array, servers = PhysGraphConfig.config_mini_graph(bitrate_factor=20,
                                                                                 latency_factor=2)
    start_create_searchspace = time.time()
    se_QoS = QoS_Requirements(bit_rate=3, latency=50, computation=2, storage=2, memory=2)
    se_conf = SGA_config(servers=['S1'], field_devices=['PDA11', 'PDA21'])
    se_sgs = SmartGridApplication("SE", se_QoS, physical_graph=physical_Graph, config=se_conf)
    start_SE_searchspace = time.time()
    #print("time to create SE search space: ", start_SE_searchspace - start_create_searchspace, 's')

    vpp_QoS = QoS_Requirements(bit_rate=5, latency=50, computation=2, storage=1, memory=3)
    vpp_conf = SGA_config(servers=['S1'],
                                   field_devices=['CLS11', 'CLS12', 'CLS21', 'CLS22'],
                                   topology=[Topology.DECENTRAL])
    vpp_sgs = SmartGridApplication("VPP", vpp_QoS, physical_graph=physical_Graph, config=vpp_conf)
    # vpp_sgs = SmartGridApplication("VPP", vpp_QoS, physical_graph=physical_Graph, servers=['S1', 'S2', 'S3'], field_devices=['CLS11', 'CLS12', 'CLS21'])
    start_VPP_searchspace = time.time()
    #print("time to create VPP search space: ", start_VPP_searchspace - start_SE_searchspace, 's')

    ar_QoS = QoS_Requirements(bit_rate=2, latency=20, computation=3, storage=3, memory=1)
    ar_conf = SGA_config( servers=['S2'], field_devices=['RTU12', 'RTU23'])
    # ar_sgs = SmartGridApplication("AR", ar_QoS, physical_graph=physical_Graph, servers=['S1', 'S2', 'S3'], field_devices=['RTU12', 'RTU13', 'RTU21', 'RTU23', 'RTU24', 'RTU31', 'RTU32', 'RTU33'])
    ar_sgs = SmartGridApplication("AR", ar_QoS, physical_graph=physical_Graph, config=ar_conf)
    start_AR_searchspace = time.time()
    #print("time to create AR search space: ", start_AR_searchspace - start_VPP_searchspace, 's')


    sgss = [se_sgs, vpp_sgs, ar_sgs] #[se_sgs, vpp_sgs, ar_sgs]
    mzn_model = MinizincAdapter(all_solutions=False, use_python_adapter=solver_config.use_python_adapter, existing_file=False)#"minizinc_data/network_model.mzn"


    mzn_model.configure_model(phys_adj_array, servers, sgss, degration=degregation_mode.Mini_Scenario_Test, solver='gecode')
    result, m_result = mzn_model.solve_model()
    util.check_constraint_satisfiability(result, sgss,  physical_Graph, phys_adj_array,
                                         servers)
    visualizer = GraphVisualizer(physical_Graph)
    experiments = {
             1: {"situation": "normal", "degregation": "none", "result": result, "stats": None}}
    visualizer.show_aggregated_scenario_solutions(experiments, show_plots=True)


run_mini_scenario()

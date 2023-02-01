import PhysGraphConfig
from SmartGridApplication import SmartGridApplication, QoS_Requirements, Topology, SGA_config
from MinizincAdapter import MinizincAdapter
from Graph_Visualizer import GraphVisualizer
from enum import Enum
import time
import os
import numpy as np
import pandas as pd
from Config import IctConfig, SolverConfig

RESULT_PATH = "../../../Nextcloud/Diss/Abbildungen/"


class scenario_mode(Enum):
    NORMAL = 1
    OVERVOLTAGE = 2


class degregation_mode(Enum):
    NONE = 1
    VIRTUALIZATION = 2
    REDUCTION = 3
    DISTRIBUTION = 4

def scenario(mode=scenario_mode.NORMAL, degregation=degregation_mode.NONE, solver_config=SolverConfig):

    result_comp_time = dict()
    start_process = time.time()
    physical_Graph, phys_adj_array, servers = PhysGraphConfig.config_mini_FAU_graph_paper(edge_l=30, sub_l=25,
                                                                                          core_l=20, edge_br=25)

    lm_QoS = QoS_Requirements(bit_rate=1000, latency=1000, computation=1, storage=1,
                              memory=1)
    lm_config = SGA_config(servers=['S2'], field_devices=['F12', 'F34', 'F22'])

    ar_QoS = QoS_Requirements(bit_rate=2500, latency=100, computation=2, storage=1,
                              memory=2)
    ar_config = SGA_config(servers=['S2'], field_devices=['F26'])

    se_QoS = QoS_Requirements(bit_rate=500, latency=1000, computation=2, storage=1, memory=2)
    se_config = SGA_config(servers=['S1'], field_devices=['F11', 'F15', 'F31', 'F33', 'F23', 'F24'])  #
    vpp_QoS = QoS_Requirements(bit_rate=2000, latency=800, computation=3, storage=2, memory=3)
    vpp_config = SGA_config(servers=['S1'], field_devices=['F13', 'F14', 'F25', 'F31', 'F34'])
    #vpp_config = SGA_config(servers=['S1'], field_devices=['F13', 'F14', 'F35', 'F21'])
    cvc_QoS = QoS_Requirements(bit_rate=3000, latency=500, computation=2, storage=2, memory=2)
    cvc_config = SGA_config(servers=['S1'], field_devices=['F16', 'F32', 'F25'])

    if mode == scenario_mode.OVERVOLTAGE:
        if degregation == degregation_mode.VIRTUALIZATION:
            cvc_QoS.max_latency = 200
            # vpp_config.servers = ['S1', 'S3']
            cvc_config.servers = ['S2']
        if degregation == degregation_mode.REDUCTION:
            cvc_QoS.min_bitrate = 5000
            se_QoS.min_bitrate = 100

        if degregation == degregation_mode.DISTRIBUTION:
            cvc_QoS.min_computation = IctConfig.CPU_RES[3]
            print("status distribution")
            # vpp_QoS.min_computation = config.CPU_RES[0]
            # vpp_QoS.min_memory = config.MEM_RES[0]
            # vpp_QoS.min_storage = config.STO_RES[0]
            vpp_config.topology = [Topology.DECENTRAL]

    se_sgs = SmartGridApplication("SE", se_QoS, physical_graph=physical_Graph, config=se_config)
    se_time = time.time()
    result_comp_time['SE'] = se_time - start_process
    print("time to generate SE ", se_time - start_process)
    cvc_sgs = SmartGridApplication("CVC", cvc_QoS, physical_graph=physical_Graph, config=cvc_config)
    cvc_time = time.time()
    result_comp_time['CVC'] = cvc_time - se_time
    print("time to generate cvc ", cvc_time - se_time)
    vpp_sgs = SmartGridApplication("VPP", vpp_QoS, physical_graph=physical_Graph, config=vpp_config)
    vpp_time = time.time()
    result_comp_time['VPP'] = vpp_time - cvc_time
    print("time to generate vpp ", vpp_time - cvc_time)
    lm_sgs = SmartGridApplication("LM", lm_QoS, physical_graph=physical_Graph, config=lm_config)
    lm_time = time.time()
    result_comp_time['LM'] = lm_time - vpp_time
    print("time to generate lm ", lm_time - vpp_time)
    ar_sgs = SmartGridApplication("AR", ar_QoS, physical_graph=physical_Graph, config=ar_config)
    ar_time = time.time()
    result_comp_time['AR'] = ar_time - lm_time
    print("time to generate ar ", ar_time - lm_time)

    sgss = [se_sgs, vpp_sgs, ar_sgs, lm_sgs, cvc_sgs]
    num_sc = dict()
    for sgs in sgss:
        num_sc[sgs.name_tag] = len(sgs.solution_candidates.solutions)
    start_instance_building = time.time()
    print("total generating solution candidates", start_instance_building - start_process)
    mzn_model = MinizincAdapter(all_solutions=False, use_python_adapter=False, existing_file=False)
    mzn_model.configure_model(phys_adj_array, servers, sgss, degregation)
    start_model_solving = time.time()
    result_comp_time['model_creation'] = start_model_solving - start_instance_building

    result = mzn_model.solve_model()
    end_solving = time.time()

    result_comp_time['minizinc_single_solving'] = end_solving - start_model_solving
    result_comp_time['total_process'] = end_solving - start_process

    print("solving duration: ", end_solving - start_instance_building)
    print("total computation duration:", end_solving - start_process)
    statistics = {"comp_time": result_comp_time,
                  "number_of_so": num_sc}
    return result, statistics


# Graph_Visualizer.display_graphs(physical_Graph, result, show_substracted_graph=True, individual_windows=True, scenario={"mode": mode.name, "degragation": degregation.name}, show_edge_weights=False, edge_color='r')

def dataframe_row_generator(experiment_nr, stat):
    row = {
        'experiment_nr': experiment_nr,
        'nr_sc_SE': stat['number_of_so']['SE'],
        'nr_sc_CVC': stat['number_of_so']['CVC'],
        'nr_sc_VPP': stat['number_of_so']['VPP'],
        'nr_sc_AR': stat['number_of_so']['AR'],
        'nr_sc_LM': stat['number_of_so']['LM'],
        'comp_time_SE': stat['comp_time']['SE'],
        'comp_time_CVC': stat['comp_time']['CVC'],
        'comp_time_VPP': stat['comp_time']['VPP'],
        'comp_time_LM': stat['comp_time']['LM'],
        'comp_time_AR': stat['comp_time']['AR'],
        'model_creation': stat['comp_time']['model_creation'],
        'model_solving': stat['comp_time']['minizinc_single_solving'],
        'total_duration': stat['comp_time']['total_process']}
    return row


if __name__ == '__main__':
    cwd = os.getcwd()  # Get the current working directory (cwd)
    os.chdir("../")
    files = os.listdir(cwd)  # Get all the files in that directory
    print("Files in %r: %s" % (cwd, files))

    # normal_res, normal_stat = scenario(scenario_mode.NORMAL, degregation_mode.NONE)
    # red_res, red_stat = scenario(scenario_mode.OVERVOLTAGE, degregation_mode.REDUCTION)
    # virt_res, virt_stat = scenario(scenario_mode.OVERVOLTAGE, degregation_mode.VIRTUALIZATION)
    dist_res, dist_stat = scenario(scenario_mode.OVERVOLTAGE, degregation_mode.DISTRIBUTION)

    df = pd.DataFrame(
        columns=['experiment_nr', 'nr_sc_SE', 'nr_sc_CVC', 'nr_sc_VPP', 'nr_sc_AR', 'nr_sc_LM',
                 'comp_time_SE', 'comp_time_CVC', 'comp_time_VPP', 'comp_time_AR', 'comp_time_LM',
                 'model_creation', 'model_solving', 'total_duration'])
    # normal_row = dataframe_row_generator(1, normal_stat)
    # df = df.append(normal_row, ignore_index=True)
    # red_row = dataframe_row_generator(2, red_stat)
    # df = df.append(red_row, ignore_index=True)
    # virt_row =dataframe_row_generator(3, virt_stat)
    # df = df.append(virt_row, ignore_index=True)
    # dist_row = dataframe_row_generator(4, dist_stat)
    # df = df.append(dist_row, ignore_index=True)
    df.to_csv(RESULT_PATH +"result.csv", encoding='utf-8', index=False)
    df.to_excel(RESULT_PATH +"result.xlsx", index=False)

    # TODO Statistiken herausbekommen
    experiments = {
                    #1: {"situation": "normal", "degregation": "none", "result": normal_res},
    #                2: {"situation": "overvoltage", "degregation": "reduction", "result": red_res},
    #                3: {"situation": "overvoltage", "degregation": "virtualization", "result": virt_res},
                    4: {"situation": "overvoltage", "degregation": "distribution", "result": dist_res}
                    }
    physical_Graph, phys_adj_array, servers = PhysGraphConfig.config_mini_FAU_graph_paper(edge_l=40, sub_l=20, core_l=20, edge_br=30)
    visualizer = GraphVisualizer(physical_Graph)
    # results = scenario(scenario_mode.NORMAL, degregation_mode.NONE)
    # visualizer.show_solution_with_substracted_physical_graph(results, show_individual_windows=True, scenario={"mode": scenario_mode.NORMAL.name, "degragation": degregation_mode.NONE.name})
    visualizer.show_aggregated_scenario_solutions(experiments, show_plots=False)

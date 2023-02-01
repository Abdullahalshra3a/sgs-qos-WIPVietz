#- * - coding: utf - 8
# Created By: Frauke Oest
import util
from Config import IctConfig, SolverConfig
from SmartGridApplication import SmartGridApplication, QoS_Requirements, Topology, SGA_config
from MinizincAdapter import MinizincAdapter
from Graph_Visualizer import GraphVisualizer
from enum import Enum
import time
import os
import ExperimentUtil
from py4j_adapter.DiscoDNC_adapter import javNC_validateNetwork


class scenario_mode(Enum):
    NORMAL = 1
    OVERVOLTAGE = 2


class degregation_mode(Enum):
    NONE = 1
    VIRTUALIZATION = 2
    REDUCTION = 3
    DISTRIBUTION = 4
    NO_LATENCY = 5
    NO_BANDWIDTH = 6
    NO_CPU = 7


def scenario(mode=scenario_mode.NORMAL, degregation=degregation_mode.NONE, solver_config=SolverConfig):
    print('FAU_Scneario: enter scenario method')
    result_comp_time = dict()
    start_process = time.time()
    result = None
    m_result = None
    lm_QoS = QoS_Requirements(bit_rate=1000, latency=1000, computation=1, storage=1, memory=1)
    lm_config = SGA_config(servers=['S2'], field_devices=['F12', 'F34', 'F22'])

    ar_QoS = QoS_Requirements(bit_rate=2500, latency=100, computation=2, storage=1,memory=2)
    ar_config = SGA_config(servers=['S2'], field_devices=['F26'])

    se_QoS = QoS_Requirements(bit_rate=500, latency=1000, computation=2, storage=1, memory=2)
    se_config = SGA_config(servers=['S1'], field_devices=['F11', 'F15', 'F31', 'F33', 'F23', 'F24'])  #
    vpp_QoS = QoS_Requirements(bit_rate=2000, latency=800, computation=3, storage=2, memory=3)
    # vpp_config = SGA_config(servers=['S1'], field_devices=['F13', 'F14', 'F25', 'F31', 'F34'])
    vpp_config = SGA_config(servers=['S1'], field_devices=['F13', 'F14', 'F35', 'F21'])
    cvc_QoS = QoS_Requirements(bit_rate=3000, latency=500, computation=2, storage=2, memory=2)
    cvc_config = SGA_config(servers=['S1'], field_devices=['F16', 'F32', 'F25'])

    if mode == scenario_mode.OVERVOLTAGE:

        # cvc_QoS = QoS_Requirements(bit_rate=5000, latency=200, computation=10, storage=20, memory=2)
        if degregation == degregation_mode.NO_LATENCY:
            cvc_QoS.max_latency = 200
        if degregation == degregation_mode.NO_BANDWIDTH:
            cvc_QoS.min_bitrate = 5000
        if degregation == degregation_mode.NO_CPU:
            cvc_QoS.min_computation = IctConfig.CPU_RES[3]

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
            # vpp_QoS.min_computation = IctConfig.CPU_RES[0]
            # vpp_QoS.min_memory = IctConfig.MEM_RES[0]
            # vpp_QoS.min_storage = IctConfig.STO_RES[0]
            vpp_config.topology = [Topology.DECENTRAL]
            vpp_config.servers = []

    se_sgs = SmartGridApplication("SE", se_QoS, physical_graph=IctConfig.physical_Graph, config=se_config)
    se_time = time.time()
    result_comp_time['SE'] = se_time - start_process
    print("time to generate SE ", se_time - start_process)
    cvc_sgs = SmartGridApplication("CVC", cvc_QoS, physical_graph=IctConfig.physical_Graph, config=cvc_config)
    cvc_time = time.time()
    result_comp_time['CVC'] = cvc_time - se_time
    print("time to generate cvc ", cvc_time - se_time)
    vpp_sgs = SmartGridApplication("VPP", vpp_QoS, physical_graph=IctConfig.physical_Graph, config=vpp_config)
    vpp_time = time.time()
    result_comp_time['VPP'] = vpp_time - cvc_time
    print("time to generate vpp ", vpp_time - cvc_time)
    lm_sgs = SmartGridApplication("LM", lm_QoS, physical_graph=IctConfig.physical_Graph, config=lm_config)
    lm_time = time.time()
    result_comp_time['LM'] = lm_time - vpp_time
    print("time to generate lm ", lm_time - vpp_time)
    ar_sgs = SmartGridApplication("AR", ar_QoS, physical_graph=IctConfig.physical_Graph, config=ar_config)
    ar_time = time.time()
    result_comp_time['AR'] = ar_time - lm_time
    print("time to generate ar ", ar_time - lm_time)

    sgss = [se_sgs, vpp_sgs, ar_sgs, lm_sgs, cvc_sgs]
    num_sc = dict()
    for sgs in sgss:
        num_sc[sgs.name_tag] = len(sgs.solution_candidates.solutions)
    #  sgss = [se_sgs, cvc_sgs]
    start_instance_building = time.time()
    print("total generating solution candidates", start_instance_building - start_process)
    mzn_model = MinizincAdapter(all_solutions=False, use_python_adapter=solver_config.use_python_adapter, existing_file=False)

    for solver in solver_config.solvers:
        mzn_model.configure_model(IctConfig.phys_adj_array, IctConfig.servers, sgss, degregation, solver=solver)# chuffed
        start_model_solving_gecode = time.time()
        result_comp_time[f'model_creation_{solver}'] = start_model_solving_gecode - start_instance_building

        use_all_solutions = True
        pickle_qos_dict = {'AR': 100.0, 'CVC': 500.0, 'LM': 1000.0, 'SE': 1000.0,
                           'VPP': 800.0}  # Has to be gathered from real program later

        if use_all_solutions:
            mzn_model.all_solutions = True
            solutions = mzn_model.solve_model()
            # Check that CSP is satisfiable, else skip
            if solutions is not None:
                # Iterate over every possible solution
                for solution in solutions:
                    # First: Generate the networkx element from the solution string list using the MiniZincAdapter
                    result, m_result = mzn_model.buildNXfromMiniZinc(solution)

                    # start_time = time.time()
                    eval_result = javNC_validateNetwork(IctConfig.physical_Graph, result, pickle_qos_dict)
                    print("Network calculus evaluation finished. Qos is met: " + str(not eval_result))
                    if not eval_result:
                        # Break the loop - we found our NC result
                        break
                    # end_time = time.time()
                    # diff = end_time - start_time
        else:
            # We just get and check one possible solution
            result, m_result = mzn_model.solve_model()

            if result is not None:
                eval_result = javNC_validateNetwork(IctConfig.physical_Graph, result, pickle_qos_dict)
                print("Network calculus evaluation finished. Qos is met: " + str(not eval_result))

        #
        # # Export the network + result as pickle object
        # import pickle
        #
        # with open('net_res.pkl', 'wb') as outp:
        #     pickle.dump(IctConfig.physical_Graph, outp, pickle.HIGHEST_PROTOCOL)
        #     pickle.dump(result, outp, pickle.HIGHEST_PROTOCOL)
        #
        end_solving_gecode = time.time()
        result_comp_time[f'minizinc_solving_{solver}'] = end_solving_gecode - start_model_solving_gecode

        #TODO: Make this part work again
        if result:
            util.check_constraint_satisfiability(result, sgss, IctConfig.physical_Graph, IctConfig.phys_adj_array, IctConfig.servers)


    statistics = {"comp_time": result_comp_time,
                  "number_of_so": num_sc}
    return result,  m_result, statistics,


# Graph_Visualizer.display_graphs(physical_Graph, result, show_substracted_graph=True, inchuffdividual_windows=True, scenario={"mode": mode.name, "degragation": degregation.name}, show_edge_weights=False, edge_color='r')




def conduct_experiments():
    normal_res, normal_m_result, normal_stat = scenario(scenario_mode.NORMAL, degregation_mode.NONE)
    no_bndwth_res, no_bndwth_m_result, no_bndwth_stat = scenario(scenario_mode.OVERVOLTAGE, degregation_mode.NO_BANDWIDTH)
    no_lat_res, no_lat_m_res, no_lat_stat = scenario(scenario_mode.OVERVOLTAGE, degregation_mode.NO_LATENCY)
    no_cpu_res, no_cpu_m_res, no_cpu_stat = scenario(scenario_mode.OVERVOLTAGE, degregation_mode.NO_CPU)
    # #
    red_res, red_m_res, red_stat = scenario(scenario_mode.OVERVOLTAGE, degregation_mode.REDUCTION)
    virt_res, virt_m_res, virt_stat = scenario(scenario_mode.OVERVOLTAGE, degregation_mode.VIRTUALIZATION)
    dist_res, dist_m_result, dist_stat = scenario(scenario_mode.OVERVOLTAGE, degregation_mode.DISTRIBUTION)



    # # TODO Statistiken herausbekommen
    experiments = {
        1: {"situation": "normal", "degregation": "none", "result": normal_res, "stats": normal_stat},
        2: {"situation": "overvoltage", "degregation": "no_bndwth", "result": no_bndwth_res, "stats": no_bndwth_stat},
        3: {"situation": "overvoltage", "degregation": "reduction", "result": red_res, "stats": red_stat},
        4: {"situation": "overvoltage", "degregation": "no_latency", "result": no_lat_res, "stats": no_lat_stat},
        5: {"situation": "overvoltage", "degregation": "virtualization", "result": virt_res, "stats": virt_stat},
        6: {"situation": "overvoltage", "degregation": "no_cpu", "result": no_cpu_res, "stats": no_cpu_stat},
        7: {"situation": "overvoltage", "degregation": "distribution", "result": dist_res, "stats": dist_stat}
    }
    sgss = ["SE", "CVC", "VPP", "AR", "LM"]

    df = ExperimentUtil.write_experiments(experiments, sgss, SolverConfig.solvers)
    visualizer = GraphVisualizer(IctConfig.physical_Graph)
    # results = scenario(scenario_mode.NORMAL, degregation_mode.NONE)
    # print(results)    # visualizer.show_solution_with_substracted_physical_graph(results, show_individual_windows=True, scenario={"mode": scenario_mode.NORMAL.name, "degragation": degregation_mode.NONE.name})
    visualizer.show_aggregated_scenario_solutions(experiments, show_plots=False)

    latex_df = df.copy()
    latex_df = latex_df.drop(columns=['paths_SE', 'paths_CVC', 'paths_VPP', 'paths_LM', 'paths_AR'])
    print(latex_df)
    latexForm = latex_df.style.to_latex()  # float_format="%.4f"
    #latexForm = latex_df.to_latex()
    print("Latex format:")
    print(latexForm)


if __name__ == '__main__':

    cwd = os.getcwd()  # Get the current working directory (cwd)
    os.chdir("../")
    files = os.listdir(cwd)  # Get all the files in that directory
    print("Files in %r: %s" % (cwd, files))

    #for i in range(1):
    conduct_experiments()
        # time.sleep(10)

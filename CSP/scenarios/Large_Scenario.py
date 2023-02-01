import util
from Config import IctConfig, SolverConfig
from SmartGridApplication import SmartGridApplication, QoS_Requirements, Topology, SGA_config
from MinizincAdapter import MinizincAdapter
from Graph_Visualizer import GraphVisualizer
from enum import Enum
import time
import os
import ExperimentUtil
import random



class configuration_mode(Enum):
    NONE = 1
    VIRTUALIZATION = 2
    REDUCTION = 3
    DISTRIBUTION = 4
    NO_LATENCY = 5
    NO_BANDWIDTH = 6
    NO_CPU = 7
    ONE_SOLUTION = 8
    ALL_SOLUTIONS_1MIN = 9
    ALL_SOLUTIONS_5MIN = 10
    ALL_SOLUTIONS_10MIN = 11


def sgs_generator(list_fd, amount, ctr, no_fd):
    list_sgs = [0] * amount
    list_fds_ = list_fd.copy()
    SGS_prefix = "GEN_"

    for ix in range(amount):

        sgs_QoS = QoS_Requirements(bit_rate=2000, latency=800, computation=1, storage=1, memory=3)
        try:
            fds = random.sample(list_fds_, k=no_fd)
        except ValueError:
            print(f"Large_Scenario: ValueError: Cannot draw sample of size {no_fd} from list {list_fds_} from original list {list_fd}")
        for fd in fds:
            try:
                list_fds_.remove(fd)
            except:
                print(fd)
                raise KeyError(f'field device {fd} not in list')
        sgs_config = SGA_config(servers=[], field_devices=fds, topology=[Topology.DECENTRAL])
        if fds:
            name_tag = SGS_prefix + str(ctr)
            sgs = SmartGridApplication(name_tag, sgs_QoS, physical_graph=IctConfig.physical_Graph, config=sgs_config)
            list_sgs[ix] = sgs
            ctr += 1
    return list_sgs

def scenario(degregation=configuration_mode.NONE, all_solutions=False, termination_time=1):
    print('FAU_Scneario: enter scenario method')
    result_comp_time = dict()
    start_process = time.time()

    all_fd = ['F11', 'F12', 'F13', 'F14', 'F15', 'F16',
              'F21', 'F22', 'F23', 'F24', 'F25', 'F26',
              'F31', 'F32', 'F33', 'F24', 'F35']


    lm_QoS = QoS_Requirements(bit_rate=1000, latency=1000, computation=1, storage=1,
                              memory=1)
    lm_config = SGA_config(servers=['S2'], field_devices=['F12', 'F34', 'F22'])

    ar_QoS = QoS_Requirements(bit_rate=2500, latency=100, computation=2, storage=1,
                              memory=2)
    ar_config = SGA_config(servers=['S2'], field_devices=['F26'])

    se_QoS = QoS_Requirements(bit_rate=500, latency=1000, computation=2, storage=1, memory=2)
    se_config = SGA_config(servers=['S1'], field_devices=['F11', 'F15', 'F31', 'F33', 'F23', 'F24'])  #
    vpp_QoS = QoS_Requirements(bit_rate=2000, latency=800, computation=3, storage=2, memory=3)
    # vpp_config = SGA_config(servers=['S1'], field_devices=['F13', 'F14', 'F25', 'F31', 'F34'])
    vpp_config = SGA_config(servers=['S1'], field_devices=['F13', 'F14', 'F35', 'F21'])
    cvc_QoS = QoS_Requirements(bit_rate=3000, latency=500, computation=2, storage=2, memory=2)
    cvc_config = SGA_config(servers=['S1'], field_devices=['F16', 'F32', 'F25'])

    se_sgs = SmartGridApplication("SE", se_QoS, physical_graph=IctConfig.physical_Graph, config=se_config)
    se_time = time.time()
    result_comp_time['SE'] = se_time - start_process
    cvc_sgs = SmartGridApplication("CVC", cvc_QoS, physical_graph=IctConfig.physical_Graph, config=cvc_config)
    cvc_time = time.time()
    result_comp_time['CVC'] = cvc_time - se_time
    vpp_sgs = SmartGridApplication("VPP", vpp_QoS, physical_graph=IctConfig.physical_Graph, config=vpp_config)
    vpp_time = time.time()
    result_comp_time['VPP'] = vpp_time - cvc_time
    lm_sgs = SmartGridApplication("LM", lm_QoS, physical_graph=IctConfig.physical_Graph, config=lm_config)
    lm_time = time.time()
    result_comp_time['LM'] = lm_time - vpp_time
    ar_sgs = SmartGridApplication("AR", ar_QoS, physical_graph=IctConfig.physical_Graph, config=ar_config)
    ar_time = time.time()
    result_comp_time['AR'] = ar_time - lm_time


    core_sgs = [se_sgs, cvc_sgs, vpp_sgs, lm_sgs, ar_sgs]

    other_sgs = sgs_generator(all_fd.copy(), 5, 0, 3)
    other_sgs_time = time.time()
    result_comp_time['generic_SGS'] = other_sgs_time- ar_time

    other_sgs_ = sgs_generator(all_fd.copy(), 2, 5, 5)
    other_sgs_time_ = time.time()
    result_comp_time['generic_SGS_2'] =  other_sgs_time_ - other_sgs_time
    #other_sgs_2 = sgs_generator(all_fd.copy(), 2, 10, 5)
    all_sgs = core_sgs + other_sgs + other_sgs_# + other_sgs_2


    num_sc = dict()
    for sgs in all_sgs:
        num_sc[sgs.name_tag] = len(sgs.solution_candidates.solutions)

    mzn_model = MinizincAdapter(all_solutions=all_solutions, use_python_adapter=False,
                                existing_file=False)

    mzn_model.configure_model(IctConfig.phys_adj_array, IctConfig.servers, all_sgs, degregation, solver='gecode')
    start_model_solving_gecode = time.time()
    result, m_result = mzn_model.solve_model(termination_time=termination_time)
    end_solving_gecode = time.time()

    result_comp_time[f'minizinc_solving'] = end_solving_gecode - start_model_solving_gecode

    if result:
        util.check_constraint_satisfiability(result, all_sgs, IctConfig.physical_Graph, IctConfig.phys_adj_array,
                                             IctConfig.servers)

    statistics = {"comp_time": result_comp_time,
                      "number_of_so": num_sc}

    print(statistics)

    return result, m_result, statistics

def run_experiments():
    #normal_res, normal_m_result, normal_stat = scenario(configuration_mode.ONE_SOLUTION, all_solutions=False)
    #one_min_res, one_min_m_result, one_minute_stat = scenario(configuration_mode.ALL_SOLUTIONS_1MIN, all_solutions=True, termination_time=1)
    #five_min_res, five_min_m_result, five_minute_stat = scenario(configuration_mode.ALL_SOLUTIONS_5MIN, all_solutions=True, termination_time=5)
    ten_min_res, ten_min_m_result, ten_minute_stat = scenario(configuration_mode.ALL_SOLUTIONS_10MIN, all_solutions=True,
                                                              termination_time=15)

    # experiments = {
    #     1: {"situation": "normal", "degradation": "one_solution", "result": normal_res, "stats": normal_stat},
    #     2: {"situation": "overvoltage", "degredation": "one_min", "result":  one_min_res, "stats": one_minute_stat},
    #     3: {"situation": "overvoltage", "degredation": "five_min", "result": five_min_res, "stats": five_minute_stat},
    #     4: {"situation": "overvoltage", "degredation": "ten::min", "result": ten_min_res, "stats": ten_minute_stat}
    # }
    # sgss = ["SE", "CVC", "VPP", "AR", "LM"]
    #
    # df = ExperimentUtil.write_experiments(experiments, sgss, SolverConfig.solvers, file_name='large_experiments')
    # visualizer = GraphVisualizer(IctConfig.physical_Graph)
    # # results = scenario(scenario_mode.NORMAL, degregation_mode.NONE)
    # # print(results)    # visualizer.show_solution_with_substracted_physical_graph(results, show_individual_windows=True, scenario={"mode": scenario_mode.NORMAL.name, "degragation": degregation_mode.NONE.name})
    # visualizer.show_aggregated_scenario_solutions(experiments, show_plots=False)
    #
    # latex_df = df.copy()
    # latex_df = latex_df.drop(columns=['paths_SE', 'paths_CVC', 'paths_VPP', 'paths_LM', 'paths_AR'])
    # print(latex_df)
    # latexForm = latex_df.to_latex()  # float_format="%.4f"
    #
    # print("Latex format:")
    # print(latexForm)


if __name__ == '__main__':

    cwd = os.getcwd()  # Get the current working directory (cwd)
    os.chdir("../")
    files = os.listdir(cwd)  # Get all the files in that directory
    print("Files in %r: %s" % (cwd, files))

    run_experiments()

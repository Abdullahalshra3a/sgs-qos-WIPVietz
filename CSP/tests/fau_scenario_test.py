#- * - coding: utf - 8
# Created By: Frauke Oest

from scenarios.FauScenario import scenario_mode, degregation_mode
import scenarios.FauScenario as fauscenario
from Candidate import Candidate
import os
import networkx as nx
from Config import SolverConfig

import random

expect_normal_result = dict()
expect_normal_result['SE'] = Candidate(server='S1', ot_device=['F11', 'F15', 'F31', 'F33', 'F23', 'F24'])
expect_normal_result['SE'].latency_sc = (60, 110, 225, 225, 250, 250)  # (60, 110, 205, 180, 230, 230)
expect_normal_result['SE'].overlay_topology = None
expect_normal_result['SE'].bitrate_sc = nx.Graph()
expect_normal_result['SE'].bitrate_sc.add_edges_from(
    [('R10', 'R20'), ('R10', 'R11'), ('R10', 'R30'), ('R11', 'F15'), ('R11', 'R13'), ('R12', 'F11'), ('R12', 'S1'),
     ('R12', 'R13'), ('R30', 'R31'), ('R30', 'R20'), ('R30', 'R32'), ('R31', 'R32'), ('R31', 'F33'), ('R32', 'F31'),
     ('R20', 'R21'), ('R21', 'R23'), ('R23', 'R24'), ('R24', 'F23'), ('R24', 'F24')])

expect_normal_result['VPP'] = Candidate(server='S1', ot_device=['F13', 'F14', 'F35', 'F21'])
expect_normal_result['VPP'].latency_sc = (85, 85, 225, 275)
expect_normal_result['VPP'].overlay_topology = None
expect_normal_result['VPP'].bitrate_sc = nx.Graph()
expect_normal_result['VPP'].bitrate_sc.add_edges_from(
    [('R10', 'R20'), ('R10', 'R11'), ('R10', 'R30'), ('R11', 'R13'), ('R12', 'R13'), ('R12', 'S1'), ('R13', 'F13'),
     ('R13', 'F14'), ('R30', 'R32'), ('R30', 'R20'), ('R31', 'F35'), ('R31', 'R32'), ('R20', 'R21'), ('R21', 'R23'),
     ('R22', 'F21'), ('R22', 'R24'), ('R23', 'R24')])

expect_normal_result['AR'] = Candidate(server='S2', ot_device=['F26'])
expect_normal_result['AR'].latency_sc = (85,)
expect_normal_result['AR'].overlay_topology = None
expect_normal_result['AR'].bitrate_sc = nx.Graph()
expect_normal_result['AR'].bitrate_sc.add_edges_from(
    [('R21', 'R23'), ('R21', 'S2'), ('R23', 'F26')])

expect_normal_result['LM'] = Candidate(server='S2', ot_device=['F12', 'F34', 'F22'])
expect_normal_result['LM'].latency_sc = (175, 155, 135)
expect_normal_result['LM'].overlay_topology = None
expect_normal_result['LM'].bitrate_sc = nx.Graph()
expect_normal_result['LM'].bitrate_sc.add_edges_from(
    [('R10', 'R11'), ('R10', 'R30'), ('R11', 'R13'), ('R13', 'F12'), ('R30', 'R20'), ('R30', 'R32'), ('R31', 'F34'),
     ('R31', 'R32'), ('R20', 'R21'), ('R21', 'S2'), ('R21', 'R23'), ('R22', 'F22'), ('R22', 'R24'), ('R23', 'R24')])

expect_normal_result['CVC'] = Candidate(server='S1', ot_device=['F16', 'F32', 'F25'])
expect_normal_result['CVC'].latency_sc = (110, 200, 250)
expect_normal_result['CVC'].overlay_topology = None
expect_normal_result['CVC'].bitrate_sc = nx.Graph()
expect_normal_result['CVC'].bitrate_sc.add_edges_from(
    [('R10', 'R20'), ('R10', 'R11'), ('R10', 'R30'), ('R11', 'F16'), ('R11', 'R13'), ('R12', 'R13'), ('R12', 'S1'),
     ('R30', 'R32'), ('R30', 'R20'), ('R32', 'F32'), ('R20', 'R21'), ('R21', 'R23'), ('R23', 'R24'), ('R24', 'F25')])


def test_normal_FAU_wo_python_adapter():
    random.seed(10)
    SolverConfig.use_python_adapter = False
    SolverConfig.solvers = ['chuffed']
    SolverConfig.MAX_NUMBER_SOLUTION_CANDIDATES = 10000000
    SolverConfig.NUMBER_PRINT_INTERVAL = 1000
    # cwd = os.getcwd()  # Get the current working directory (cwd)
    os.chdir("../")
    cwd = os.getcwd()
    print(f'micro_scenario_test: get cwd {cwd}')
    res, m_res, stat = fauscenario.scenario(scenario_mode.NORMAL, degregation_mode.NONE, solver_config=SolverConfig)
    expected_m_res = {"x_se": 8192,
                      "x_vpp": 256,
                      "x_ar": 1,
                      "x_lm": 16,
                      "x_cvc": 96,
                      "x_se_br_factor": 500,
                      "x_vpp_br_factor": 2000,
                      "x_ar_br_factor": 2500,
                      "x_lm_br_factor": 1000, "x_cvc_br_factor": 3000}
    expected_stat = {'SE': 8192, 'VPP': 256, 'AR': 2, 'LM': 32, 'CVC': 128}
    assert m_res == expected_m_res
    assert stat['number_of_so'] == expected_stat

    expect_normal_result['VPP'].server = ['S2']
    # #
    for key, elem in res.items():
        assert expect_normal_result[key].latency_sc == res[key].latency_sc
        assert expect_normal_result[key].overlay_topology == res[key].overlay_topology
        assert expect_normal_result[key].bitrate_sc.edges == res[key].bitrate_sc.edges


def test_fau_scenario_virtualized_wo_python_adapter():
    random.seed(10)
    SolverConfig.use_python_adapter = False
    SolverConfig.solvers = ['chuffed']
    SolverConfig.MAX_NUMBER_SOLUTION_CANDIDATES = 10000000
    SolverConfig.NUMBER_PRINT_INTERVAL = 1000
    cwd = os.getcwd()  # Get the current working directory (cwd)
    if "CSP" in cwd and "tests" not in cwd:
        cwd.split("CSP", 1)[1]
        print(cwd)
    else:
        os.chdir("../")
        # os.chdir(cwd + "/scenarios")
        cwd = os.getcwd()
    print(f'micro_scenario_test: get cwd {cwd}')
    res, m_res, stat = fauscenario.scenario(scenario_mode.OVERVOLTAGE, degregation_mode.VIRTUALIZATION,
                                            solver_config=SolverConfig)
    expected_m_res = {"x_se": 8192,
                      "x_vpp": 256,
                      "x_ar": 1,
                      "x_lm": 16,
                      "x_cvc": 12,
                      "x_se_br_factor": 500,
                      "x_vpp_br_factor": 2000,
                      "x_ar_br_factor": 2500,
                      "x_lm_br_factor": 1000, "x_cvc_br_factor": 3000}
    expected_stat = {'SE': 8192, 'VPP': 256, 'AR': 2, 'LM': 32, 'CVC': 16}
    assert m_res == expected_m_res
    assert stat['number_of_so'] == expected_stat

    expect_normal_result['CVC'].latency_sc = (150, 130, 110)
    expect_normal_result['CVC'].bitrate_sc = nx.Graph()
    expect_normal_result['CVC'].bitrate_sc.add_edges_from(
        [('R10', 'R11'), ('R10', 'R30'), ('R11', 'F16'), ('R30', 'R20'), ('R30', 'R32'), ('R32', 'F32'), ('R20', 'R21'),
         ('R21', 'S2'), ('R21', 'R23'), ('R23', 'R24'), ('R24', 'F25')])

    for key, elem in res.items():
        assert expect_normal_result[key].latency_sc == res[key].latency_sc
        assert expect_normal_result[key].overlay_topology == res[key].overlay_topology
        assert expect_normal_result[key].bitrate_sc.edges == res[key].bitrate_sc.edges


def test_fau_scenario_distributed_wo_python_adapter_short():
    random.seed(10)
    SolverConfig.use_python_adapter = False
    SolverConfig.solvers = ['gecode']
    SolverConfig.MAX_NUMBER_SOLUTION_CANDIDATES = 10000
    SolverConfig.NUMBER_PRINT_INTERVAL = 100

    cwd = os.getcwd()  # Get the current working directory (cwd)
    if "CSP" in cwd and "tests" not in cwd and "scenarios" not in cwd:
        cwd.split("CSP", 1)[1]
        print(cwd)
    else:
        os.chdir("../")
        # os.chdir(cwd + "/scenarios")
        cwd = os.getcwd()
    print(f'micro_scenario_test: get cwd {cwd}')
    res, m_res, stat = fauscenario.scenario(scenario_mode.OVERVOLTAGE, degregation_mode.DISTRIBUTION,
                                            solver_config=SolverConfig)
    expected_m_res = {'x_se': 1, 'x_vpp': 1, 'x_ar': 1, 'x_lm': 1, 'x_cvc': 1, 'x_se_br_factor': 500,
                      'x_vpp_br_factor': 2000, 'x_ar_br_factor': 2500, 'x_lm_br_factor': 1000, 'x_cvc_br_factor': 3000}
    expected_stat = {'SE': 8192, 'VPP': 10000, 'AR': 2, 'LM': 32, 'CVC': 128}
    assert m_res == expected_m_res
    assert stat['number_of_so'] == expected_stat
    #ToDo hier ist nichtdeterminismus, den selbst der Seed nihct behebt
    # for key, elem in res.items():
    #     assert expect_normal_result[key].latency_sc == res[key].latency_sc
    #     assert expect_normal_result[key].overlay_topology == res[key].overlay_topology
    #     assert expect_normal_result[key].bitrate_sc.edges == res[key].bitrate_sc.edges

#- * - coding: utf - 8
# Created By: Frauke Oest

import pytest_check as check
import scenarios.MicroScenario as microscenario
from scenarios.FauScenario import scenario_mode, degregation_mode
import scenarios.FauScenario as fauscenario
from Candidate import Candidate
import os
import networkx as nx
from Config import SolverConfig

def test_micro_scenario():
    SolverConfig.use_python_adapter = False
    SolverConfig.solvers = ['chuffed']
    SolverConfig.single_path_solution_candidates = False
    cwd = os.getcwd()  # Get the current working directory (cwd)
    os.chdir(cwd + "/scenarios")
    #files = os.listdir(cwd)
    print(f'micro_scenario_test: get cwd {cwd}')
    result, m_result = microscenario.run_micro_scenario(SolverConfig)
    expected_m_result = {"x_se": 1, "x_vpp": 2, "x_se_br_factor": 3, "x_vpp_br_factor": 5}
    expected_result_SE = Candidate(server='S1', ot_device=['B'])
    expected_result_SE.latency_sc = (13,)
    expected_result_SE.multipaths = (['B', 'R3', 'R1', 'S1'],)
    expected_result_SE.overlay_topology = None
    expected_result_SE.bitrate_sc = nx.Graph()
    expected_result_SE.bitrate_sc.add_edges_from([('S1', 'R1'), ('B', 'R3'), ('R1', 'R3')])

    assert m_result == expected_m_result

    assert result['SE'].latency_sc == expected_result_SE.latency_sc
    assert result['SE'].multipaths == expected_result_SE.multipaths
    assert result['SE'].overlay_topology == expected_result_SE.overlay_topology
    assert result['SE'].bitrate_sc.edges == expected_result_SE.bitrate_sc.edges

    expected_result_VPP = Candidate(server='S1', ot_device=['C'])
    expected_result_VPP.latency_sc = (18,)
    expected_result_VPP.multipaths = (['C', 'R2', 'R3', 'R1', 'S1'],)
    expected_result_VPP.overlay_topology = None
    expected_result_VPP.bitrate_sc = nx.Graph()
    expected_result_VPP.bitrate_sc.add_edges_from([('S1', 'R1'), ('C', 'R2'), ('R1', 'R3'), ('R2', 'R3')])
    assert result['VPP'].latency_sc == expected_result_VPP.latency_sc
    assert result['VPP'].multipaths == expected_result_VPP.multipaths
    assert result['VPP'].overlay_topology == expected_result_VPP.overlay_topology
    assert result['VPP'].bitrate_sc.edges == expected_result_VPP.bitrate_sc.edges





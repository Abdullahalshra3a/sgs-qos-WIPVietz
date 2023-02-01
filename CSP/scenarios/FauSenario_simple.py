#- * - coding: utf - 8
# Created By: Frauke Oest

import PhysGraphConfig
from SmartGridApplication import SmartGridApplication, QoS_Requirements
from MinizincAdapter import MinizincAdapter
import Graph_Visualizer
from enum import Enum
import time


def scenario():
    physical_Graph, phys_adj_array, servers = PhysGraphConfig.config_Fau_graph()


    vpp_QoS = QoS_Requirements(bit_rate=2000, latency=100, computation=5, storage=3, memory=10)
    vpp_sgs = SmartGridApplication("VPP", vpp_QoS, physical_graph=physical_Graph, servers=['S3'],
        field_devices = ['CLS11', 'CLS12', 'CLS21', 'CLS31', 'CLS32'])

    #   lm_QoS = QoS_Requirements(bit_rate=1000, latency=900, computation=10, storage=20, memory=2)
    #    lm_sgs = SmartGridApplication("LM", lm_QoS, physical_graph=physical_Graph, servers=['S3'],
    #field_devices = ['RTU11', 'RTU24', 'RTU32'])
    #    ar_QoS = QoS_Requirements(bit_rate=2500, latency=100, computation=10, storage=20, memory=2)
    #    ar_sgs = SmartGridApplication("AR", ar_QoS, physical_graph=physical_Graph, servers=['S1'],
   # field_devices = ['RTU13', 'RTU21', 'RTU23', 'RTU32'])
    se_QoS = QoS_Requirements(bit_rate=5000, latency=1000, computation=5, storage=5, memory=5)

    #    cvc_QoS = QoS_Requirements(bit_rate=3000, latency=500, computation=10, storage=20, memory=2)
    se_sgs = SmartGridApplication("SE", se_QoS, physical_graph=physical_Graph, servers=['S1'],
                                  field_devices=['PDA11', 'PDA31'])
    #    cvc_sgs = SmartGridApplication("CVC", cvc_QoS, physical_graph=physical_Graph, servers=['S1'],
    #field_devices = ['RTU12', 'RTU22', 'RTU33'])

    #sgss = [se_sgs, vpp_sgs, ar_sgs, lm_sgs, cvc_sgs]
    sgss = [se_sgs, vpp_sgs]
    mzn_model = MinizincAdapter(all_solutions=True)
    mzn_model.configure_model(phys_adj_array, servers, sgss)
    result = mzn_model.solve_model()
    Graph_Visualizer.display_graphs(physical_Graph, result, show_substracted_graph=True)

scenario()

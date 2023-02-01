#- * - coding: utf - 8
# Created By: Frauke Oest

from util import Topology
from SolutionCandidates import SolutionCandidates
from Config import IctConfig

class SmartGridApplication():

    def __init__(self, name_tag, qos_Requirements, physical_graph, config):
        self.name_tag = name_tag
        self.qos = qos_Requirements
        self.config = config
        self.phsys_graph = physical_graph
        self.solution_candidates = SolutionCandidates(physical_graph, self.config.servers, self.config.field_devices,
                                                       self.qos.min_bitrate, topology=self.config.topology,
                                                       connectivity=self.config.connectivity_phi,latency=self.qos.max_latency)
        pass


class SGA_config():
    def __init__(self, servers, field_devices, topology=[Topology.CENTRAL]):
        self.servers = servers
        self.field_devices = field_devices
        self.topology = topology
        self.connectivity_phi = 0.5


class QoS_Requirements():
    def __init__(self, bit_rate, latency, computation, storage, memory):
        self.min_bitrate = bit_rate
        self.max_latency = latency
        self.min_computation = IctConfig.CPU_RES[computation]
        self.min_storage = IctConfig.STO_RES[storage]
        self.min_memory = IctConfig.MEM_RES[memory]

    def to_list(self):
        return [self.min_bitrate, self.max_latency]







if __name__ == "__main__":
    import PhysGraphConfig as pgc

    phys_graph, phys_adj_array, servers = pgc.config_micrograph()

    candidates = SolutionCandidates(physical_graph=phys_graph, servers='A', bitrate=5,
                                     field_devices=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                                     topology=Topology.DECENTRAL, connectivity=1)

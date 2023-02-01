from py4j.java_collections import ListConverter
from py4j.java_gateway import JavaGateway


def javNC_validateNetwork(network, result, qos_dict):
    """
    Function used to validate the given CSP solution with network calculus using a JVM (running in parallel)

    :param network: Networkx graph of the physical network
    :type network: networkx.Graph
    :param result: CSP result containing the resulting paths of the services
    :type result: dict[str, Candidate.Candidate]
    :param qos_dict: Dictionary containing the QoS requirements for the different SGS
    :type qos_dict: dict[str, float]
    :return: Boolean if one of the delay constraints is exceeded
    :rtype: bool
    """
    # Instantiate java gateway
    gateway = JavaGateway()
    entryPnt = gateway.entry_point

    # Reset the edge list in the network (jvm might be running longer already
    entryPnt.resetAll()

    # Iterate over every network edge and add it to the jvm
    jav_addEdges(entryPnt, network)

    # Iterate over every Smart grid service (SGS) and add it to the jvm
    jav_addSGS(gateway, qos_dict, result)

    # Create the Servergraph (aka network) on the java side
    entryPnt.createNCNetwork()
    # Conduct the experiment
    maxDelayExceeded = entryPnt.calculateNCDelays()
    return maxDelayExceeded


def jav_addSGS(gateway, qos_dict, result):
    """
    Helper function to add all specified Smart grid services (SGS) to the JVM.

    :param gateway: Py4j gateway to the JVM
    :type gateway: py4j.java_gateway.JavaGateway
    :param qos_dict: Dictionary containing the QoS requirements for the different SGS
    :type qos_dict: dict[str, float]
    :param result: CSP result containing the resulting paths of the services
    :type result: dict[str, Candidate.Candidate]
    """
    # Iterate over every Smart grid service (SGS) and add it to the jvm
    for sgs_name, sgs in result.items():
        #print('sgs.multipaths', sgs.multipaths)
        bucket_size = 255  # max packet size of the 104 protocol TODO: subject of
        # Create a new java list as a container
        javPathList = gateway.jvm.java.util.ArrayList()
        # Iterate over every path, convert it to a java list and add it to javPathList
        for path in sgs.multipaths:
            javList = ListConverter().convert(path, gateway._gateway_client)
            javPathList.append(javList)

        # Send the SGS details to the jvm
        # Attention: QoS requirement is in ms, program expects s
        server = sgs.server
        if isinstance(server, list):
            server = None
        gateway.entry_point.addSGService(sgs_name, server, bucket_size, sgs.bitrate_factor,
                                         qos_dict[sgs_name] / 1000.0, javPathList)


def jav_addEdges(entryPnt, network):
    """
    Helper function to add all edges to the JVM

    :param entryPnt: Py4J entrypoint to access the JVM
    :type entryPnt:
    :param network: Networkx graph of the physical network
    :type network: networkx.Graph
    """
    # Iterate over every network edge and add it to the jvm
    for edge in list(network.edges.data()):
        # Add the edges in both directions to account for bidirectional, but independent channels
        # ASSUMPTION: We have a medium which has two independent channels (no shared medium) - e.g. switched Ethernet
        srcNode = edge[0]
        dstNode = edge[1]
        bitrate = float(edge[2]["weight"])
        latency = float(edge[2]["lat"]) / 1000.0  # Latency is defined in ms, program expects it to be in seconds
        entryPnt.addEdge(srcNode, dstNode, bitrate, latency)
        entryPnt.addEdge(dstNode, srcNode, bitrate, latency)


def testCases():
    """
    Manual test cases used to validate the correctness of the java path.
    """
    # Instantiate java gateway
    gateway = JavaGateway()
    entryPnt = gateway.entry_point
    # Test case one server
    bitrate = 25e3
    latency = 30e-3
    entryPnt.addEdge("F10", "S1", bitrate, latency)

    bucket_size = 255
    bitrate_flow = int(0.5e3)
    javPathListInner = gateway.jvm.java.util.ArrayList()
    javPathListInner.append("F10")
    javPathListInner.append("S1")
    javPathList = gateway.jvm.java.util.ArrayList()
    javPathList.append(javPathListInner)

    # According to manual calculations the result should be 40.2ms
    entryPnt.addSGService("SE", "S1", bucket_size, bitrate_flow, 40.2e-3, javPathList)

    # Test case two server
    bitrate = 25e3
    latency = 30e-3
    entryPnt.addEdge("F10", "R1", bitrate, latency)
    entryPnt.addEdge("R1", "S1", bitrate, latency)

    bucket_size = 255
    bitrate_flow = int(0.5e3)
    javPathListInner = gateway.jvm.java.util.ArrayList()
    javPathListInner.append("F10")
    javPathListInner.append("R1")
    javPathListInner.append("S1")
    javPathList = gateway.jvm.java.util.ArrayList()
    javPathList.append(javPathListInner)

    # According to manual calculations the result should be 70.2ms (using PBOO, otherwise 81ms)
    entryPnt.addSGService("SE", "S1", bucket_size, bitrate_flow, 70.2e-3, javPathList)


if __name__ == '__main__':
    import pickle

    # Read network from file
    with open('../net_res.pkl', 'rb') as inp:
        pickle_network = pickle.load(inp)
        pickle_result = pickle.load(inp)

    pickle_qos_dict = {'AR': 100.0, 'CVC': 500.0, 'LM': 1000.0, 'SE': 1000.0,
                       'VPP': 800.0}  # Has to be gathered from real program later
    javNC_validateNetwork(pickle_network, pickle_result, pickle_qos_dict)

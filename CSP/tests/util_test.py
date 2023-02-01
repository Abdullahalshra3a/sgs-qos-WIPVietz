import pytest_check as check
import util
import PhysGraphConfig


def test_adj_positioning_w_micrograph():
    G, array, servers = PhysGraphConfig.config_micrograph()
    #for e in G.edges.data("weight"):
    #    print(e)
    #print(G.has_edge('S1','R2'))
    for j in range(array.shape[0]):
        for i in range(array.shape[1]):
            node1 = util.get_node_of_index(G, j)
            node2 = util.get_node_of_index(G, i)
            weight = array[i][j]
            if weight != 0 and G.has_edge(node1, node2) or weight == 0 and not G.has_edge(node1, node2):
                assert True
            else:
                assert False



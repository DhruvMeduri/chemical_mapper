import itertools
from collections import defaultdict
from joblib import Parallel,delayed 
import multiprocessing
import time
__all__ = ["GraphNerve"]


class Nerve:
    """Base class for implementations of a nerve finder to build a Mapper complex.

    """

    def __init__(self):
        pass

    def compute(self, nodes, links):
        raise NotImplementedError()


class GraphNerve(Nerve):
    """ Creates the 1-skeleton of the Mapper complex.

    Parameters
    -----------

    min_intersection: int, default is 1
        Minimum intersection considered when computing the nerve. An edge will be created only when the intersection between two nodes is greater than or equal to `min_intersection`
    """

    def __init__(self, min_intersection=1):
        self.min_intersection = min_intersection

    def __repr__(self):
        return "GraphNerve(min_intersection={})".format(self.min_intersection)

    def compute(self, nodes):
        """Helper function to find edges of the overlapping clusters.

        Parameters
        ----------
        nodes:
            A dictionary with entires `{node id}:{list of ids in node}`

        Returns
        -------
        edges:
            A 1-skeleton of the nerve (intersecting  nodes)

        simplicies: 
            Complete list of simplices

        """

        result = defaultdict(list)


             
        # Create links when clusters from different hypercubes have members with the same sample id.
        candidates = nodes.keys()
        print("COMPUTING CUBE MARKERS")
        cube_markers = {-1:0}
        cube = 0
        count = 0
        for candidate in candidates:
            print(candidate)
            temp = int(candidate.split('_')[0].replace('cube',''))
            if temp>cube:
                cube_markers[cube] = count
                cube = cube + 1 
            
            count = count + 1
        cube_markers[cube] = count

        print(len(candidates))
        print("DONE")    
        print(cube_markers)
        candidates = list(candidates)
 
        print("COMPUTING LINKS")
        for i in range(len(cube_markers)-2):
            # if there are non-unique members in the union
            if i == 0:
                for r in range(cube_markers[0]):
                    for c in range(cube_markers[0],cube_markers[1]):
                        if (
                        len(set(nodes[candidates[r]]).intersection(set(nodes[candidates[c]])))
                        >= self.min_intersection
                ):
                            result[candidates[r]].append(candidates[c])
                            print([candidates[r],candidates[c]])
            else:
                for r in range(cube_markers[i-1],cube_markers[i]):
                    for c in range(cube_markers[i],cube_markers[i+1]):
                        if (
                        len(set(nodes[candidates[r]]).intersection(set(nodes[candidates[c]])))
                        >= self.min_intersection
                ):
                            result[candidates[r]].append(candidates[c])
                
                for r in range(cube_markers[i-2],cube_markers[i-1]):
                    for c in range(cube_markers[i-1],cube_markers[i]):
                        if (
                        len(set(nodes[candidates[r]]).intersection(set(nodes[candidates[c]])))
                        >= self.min_intersection
                ):
                            result[candidates[r]].append(candidates[c])
                            print([candidates[r],candidates[c]])

            #cube1 = int(candidate[0].split('_')[0].replace('cube',''))
            #cube2 = int(candidate[1].split('_')[0].replace('cube',''))
            #if cube1 - cube2 == 1 or cube2-cube1 == 1:
            #    start = time.time()
            #    if (
            #        len(set(nodes[candidate[0]]).intersection(set(nodes[candidate[1]])))
            #        >= self.min_intersection
            #    ):
            #        result[candidate[0]].append(candidate[1])
            #    end = time.time()
            #    print(end - start)
            #    print(candidate)
        print("DONE")
        edges = [[x, end] for x in result for end in result[x]]
        simplices = [[n] for n in nodes] + edges
        return result, simplices


class SimplicialNerve(Nerve):
    """ Creates the entire Cech complex of the covering defined by the nodes.

    Warning: Not implemented yet.
    """

    def compute(self, nodes, links=None):
        pass

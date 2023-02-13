import random
import sys
from collections import defaultdict

def segments_cross(a, b, c, d) -> bool:
    epsilon = sys.float_info.epsilon
    if abs(orientation(a, b, c)) < epsilon and abs(orientation(a, b, d)) < epsilon:
        # segments are collinear
        # check whether both x and y projections intersect
        return projections_intersect(a, b, c, d)
    else:
        # segments are not collinear
        # if the other two points are both on the same side, segments do not cross
        if orientation(a, b, c) * orientation(a, b, d) > 0.0:
            return False
        if orientation(c, d, a) * orientation(c, d, b) > 0.0:
            return False
    return True
    

def ordered(i, j):
    if i > j:
        return (j, i)
    else:
        return (i, j)
        
      
def polygon_is_clockwise(polygon) -> bool:
    num_points = len(polygon)
    s = 0.0
    for i in range(num_points):
        j = (i + 1) % num_points
        s += (polygon[j][0] - polygon[i][0]) * (polygon[j][1] + polygon[i][1])
    return s > 0.0        
        
        
def edges_are_connected(edges) -> bool:
    d = defaultdict(set)
    for (a, b) in edges:
        assert a != b, "edge cannot start and end at same vertex"
        d[a].add(b)
        d[b].add(a)

    if not all([len(v) == 2 for (_, v) in d.items()]):
        return False

    vertices_to_visit = set(d.keys())
    vertices_visited = set()

    # start somewhere
    v = list(d.keys())[0]

    while True:
        vertices_visited.add(v)
        a = d[v].pop()
        b = d[v].pop()
        if a in vertices_visited and b in vertices_visited:
            break
        if not a in vertices_visited:
            v = a
        if not b in vertices_visited:
            v = b

    return vertices_to_visit == vertices_visited        
        
        
def orientation(u, v, w) -> float:
    uw_x = u[0] - w[0]
    uw_y = u[1] - w[1]

    vw_x = v[0] - w[0]
    vw_y = v[1] - w[1]

    return uw_x * vw_y - uw_y * vw_x


def random_polygon(num_points):
    assert num_points > 2

    points = [
        (random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)) for _ in range(num_points)
    ]

    edges_to_check = set()
    for i in range(num_points):
        edges_to_check.add(ordered(i, (i + 1) % num_points))

    non_intersecting_edges = set()
    while len(edges_to_check) > 0:
        (a, b) = edges_to_check.pop()
        intersecting_edges = find_intersecting_edges(
            (a, b), edges_to_check, points, only_first=True
        )

        if intersecting_edges == []:
            non_intersecting_edges.add(ordered(a, b))
        else:
            (c, d) = intersecting_edges[0]
            edges_to_check.remove((c, d))

            # don't split the polygon into two
            graph = edges_to_check.union(non_intersecting_edges)
            graph.add(ordered(c, a))
            graph.add(ordered(d, b))
            if edges_are_connected(graph):
                new_edges = [ordered(c, a), ordered(d, b)]
            else:
                new_edges = [ordered(c, b), ordered(d, a)]

            # check whether a new edge intersects with an edge which we have
            # previously found as non-intersecting
            for edge in new_edges:
                edges_to_check.add(edge)
                for intersecting_edge in find_intersecting_edges(
                    edge, non_intersecting_edges, points, only_first=False
                ):
                    if intersecting_edge in non_intersecting_edges:
                        edges_to_check.add(intersecting_edge)
                        non_intersecting_edges.remove(intersecting_edge)

    vertices = recombine_edges(non_intersecting_edges)

    polygon = list(map(lambda v: points[v], vertices))

    if polygon_is_clockwise(polygon):
        polygon = list(reversed(polygon))

    return fit_to_bbox(polygon)


def recombine_edges(edges):
    d = defaultdict(set)

    for (a, b) in edges:
        assert a != b, "edge cannot start and end at same vertex"
        d[a].add(b)
        d[b].add(a)

    # every vertex should appear exactly twice
    assert all([len(v) == 2 for (_, v) in d.items()]), "the edges do not form a cycle"

    polygon = []

    # we start with the smallest one
    first_index = sorted(d.keys())[0]
    polygon.append(first_index)

    last_index = polygon[-1]
    while True:
        next_index = d[last_index].pop()

        # we need to remove this also from the other vertex
        # to make sure we don't loop right back
        d[next_index].remove(last_index)

        if next_index == first_index:
            break
        polygon.append(next_index)
        last_index = next_index

    return polygon
    

def find_intersecting_edges(edge, edges, points, only_first):
    intersecting_edges = []
    (a, b) = edge
    pa = points[a]
    pb = points[b]
    for (c, d) in edges:
        if not a in (c, d):
            if not b in (c, d):
                pc = points[c]
                pd = points[d]
                if segments_cross(pa, pb, pc, pd):
                    intersecting_edges.append((c, d))
                    if only_first:
                        break
    return intersecting_edges


def get_bbox(points):
    huge = sys.float_info.max
    x_min = huge
    x_max = -huge
    y_min = huge
    y_max = -huge
    for (x, y) in points:
        x_min = min(x_min, x)
        x_max = max(x_max, x)
        y_min = min(y_min, y)
        y_max = max(y_max, y)
    return x_min, x_max, y_min, y_max

    
def fit_to_bbox(points):
    x_min, x_max, y_min, y_max = get_bbox(points)

    scale_x = 1.0 / (x_max - x_min)
    scale_y = 1.0 / (y_max - y_min)

    return [((x - x_min) * scale_x, (y - y_min) * scale_y) for (x, y) in points]
    
    

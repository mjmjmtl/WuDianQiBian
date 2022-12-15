import time

import numpy as np
import colorama
import networkx as nx
import trimesh
from scipy.spatial.transform import Rotation


def get_soccer_points(subdivisions):
    # initialization
    sphere = trimesh.creation.icosphere(subdivisions=subdivisions)
    graph = sphere.vertex_adjacency_graph
    key_point_distance = 1 << subdivisions
    is_black = np.full(len(sphere.vertices), False)

    # black pieces on soccer ball
    for u in range(12):
        for _, v in nx.bfs_edges(graph, u, depth_limit=key_point_distance // 3):
            is_black[v] = True

    # black edges on soccer ball
    for u in range(12):
        shortest_path = nx.single_source_shortest_path(graph, u, key_point_distance)
        for v in range(u + 1, 12):
            if v in shortest_path:
                is_black[shortest_path[v]] = True

    black_points = sphere.vertices[is_black]
    white_points = sphere.vertices[~is_black]
    return black_points, white_points


screen_size = 60
theta_spacing = 0.07
phi_spacing = 0.02
illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")

A = 1
B = 1
R1 = 1
R2 = 2
K2 = 20
K1 = screen_size * K2 * 3 / (8 * (R1 + R2))

black_points, white_points = get_soccer_points(6)


def render_frame(A: float, B: float) -> np.ndarray:
    """
    Returns a frame of the spinning 3D donut.
    Based on the pseudocode from: https://www.a1k0n.net/2011/07/20/donut-math.html
    """
    rotation_matrix = Rotation.from_euler('y', A).as_matrix()
    # rotation_matrix = np.array([])
    # cos_A = np.cos(A)
    # sin_A = np.sin(A)

    output = np.full((screen_size, screen_size), " ")  # (40, 40)

    radius = 3.5

    def _draw_points(points, is_black):
        points = points * radius @ rotation_matrix.T
        # points = points * radius
        # points = rotation_matrix.apply(points)
        for x, y, z in points:
            # x *= radius
            # y *= radius
            # z *= radius
            # x, z = x * cos_A - z * sin_A, z * cos_A + x * sin_A
            if z > 0:
                continue
            ooz = 1 / (z + K2)  # "one over z"
            xp = int(screen_size / 2 + K1 * ooz * x)
            yp = int(screen_size / 2 - K1 * ooz * y)
            if is_black:
                output[yp, xp] = ' '
                continue
            l = np.dot((x, y, z), (0, 1, -1)) / 3
            # if l < 0:
            #     continue
            luminance_index = int(l * 8)
            luminance_index = min(luminance_index, len(illumination) - 1)

            output[yp, xp] = illumination[luminance_index]

    _draw_points(white_points, False)
    _draw_points(black_points, True)

    return output


def pprint(array: np.ndarray) -> None:
    """Pretty print the frame."""
    print(*[''.join(np.repeat(row, 2)) for row in array], sep="\n")


colorama.init()
if __name__ == "__main__":
    pass
    print('\033[?25l', end="")
    for _ in range(screen_size * screen_size):
        A += theta_spacing
        B += phi_spacing
        print("\x1b[H")
        pprint(render_frame(A, B))
        time.sleep(0.1)
    #

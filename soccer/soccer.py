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


def draw_points(output, points, center, is_black):
    for point in points:
        normal = point - center
        if np.dot(normal, np.array([0, 0, -K]) - center) < 0:
            continue
        xp = int(point[0] * K / (K + point[2]) + screen_size / 2)
        yp = int(point[1] * K / (K + point[2]) + screen_size / 2)
        if is_black:
            output[yp, xp] = ' '
            continue
        l = np.dot(normal, L)
        if l < 0:
            l = 0  # add some light to the dark part
        luminance_index = int(l * (len(illumination) - 1))
        output[yp, xp] = illumination[luminance_index]


screen_size = 60
theta_spacing = 0.07
phi_spacing = 0.02
illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")

A = 1
B = 1
R1 = 1
R2 = 2
K2 = 6
K = 150
L = np.array([0, -np.sqrt(2) / 2, -np.sqrt(2) / 2])

black_points, white_points = get_soccer_points(6)


def render_frame(A: float, B: float) -> np.ndarray:
    """
    Returns a frame of the spinning 3D donut.
    Based on the pseudocode from: https://www.a1k0n.net/2011/07/20/donut-math.html
    """
    rotation_matrix = Rotation.from_euler('y', A).as_matrix()
    output = np.full((screen_size, screen_size), " ")
    center = np.array([0, 0, K2 - K])
    draw_points(output, (white_points) @ rotation_matrix.T + center, center, False)
    draw_points(output, (black_points) @ rotation_matrix.T + center, center, True)
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
        # time.sleep(0.1)
    #

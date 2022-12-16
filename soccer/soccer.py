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

        # Skip if the point is invisible.
        if np.dot(normal, np.array([0, 0, -K]) - center) < 0:
            continue

        # project to screen.
        xp = int(point[0] * K / (K + point[2]) + screen_size / 2)
        yp = int(point[1] * K / (K + point[2]) + screen_size / 2)

        # Set it to ' ' if is_black.
        if is_black:
            output[yp, xp] = ' '
            continue

        # Add lighting otherwise.
        l = np.dot(normal, L)
        if l < 0:
            l = 0  # add some light to the dark part
        luminance_index = int(l * (len(illumination) - 1))
        output[yp, xp] = illumination[luminance_index]


screen_size = 72
illumination = ".,-~:;=!*#$@"

K = 190
CENTER = np.array([0, 0, -184])
L = np.array([0, -np.sqrt(2) / 2, -np.sqrt(2) / 2])

colorama.init()
if __name__ == "__main__":
    print('\033[?25l', end="")
    black_points, white_points = get_soccer_points(6)
    for i in range(100):
        print("\x1b[H")
        rotation_matrix = Rotation.from_euler('y', i / 100).as_matrix()
        output = np.full((screen_size, screen_size), " ")
        draw_points(output, (white_points) @ rotation_matrix.T + CENTER, CENTER, False)
        draw_points(output, (black_points) @ rotation_matrix.T + CENTER, CENTER, True)
        print(*[''.join(np.repeat(row, 2)) for row in output], sep="\n")

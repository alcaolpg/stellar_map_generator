import numpy as np
import pandas as pd
import math
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from multiprocessing import Process, Manager

# Generador de coordenadas tridimencionales respecto a un punto central
# Asignar a clusters de puntos dominios de imperios
#   Traal'daar
#   Protectorado Astral
#   Confederación Unida de Gustair
#   Elysia (Posición Unica)
#   Conglomerado
#   Main Beacon (MV) (0,0,0)
# Estructura de la información de un sistema del conglomerado
#   Sistema(___Posición_relativa_MV[x,y,z]___, nombre,descripción, faccion_actual?) <--- PRINCIPAL
#   Cuerpo(___Posición_relativa_MV[x,y,z](Fk)___,___Posición_relativa_estrella[x,y,z]___, Nombre, Tipo(planeta, estación, Otro), Satelites?,Caracteristicas)

# factions = ["Traal'daar", "Protectorado Astral", "Confederación Unida de Gustair", "Elysia", "Conglomerado"]
# Velocidad de viaje recomendado aprox 0.31 parsec/h o 1 l y/h


def closest_star(systems, size, separation_factor):
    print("measuring distances...")
    distances = []
    for system in range(0, size):
        closest_dist = 100000000 * separation_factor
        for dif_system in range(0, size):
            if dif_system != system:
                distance = (
                    math.pow(systems[system][0] - systems[dif_system][0], 2)
                    + math.pow(systems[system][1] - systems[dif_system][1], 2)
                    + math.pow(systems[system][2] - systems[dif_system][2], 2)
                )
                if distance < closest_dist:
                    closest_dist = distance
                    closest_syst = dif_system
        distances.append([math.sqrt(closest_dist), system, closest_syst])

    return distances


def furthest_distance(systems, size):
    print("searching furthest_distance...")
    furthest = 0
    for system in range(size):
        for dif_system in range(system + 1, size):
            distance = (
                math.pow(systems[system][0] - systems[dif_system][0], 2)
                + math.pow(systems[system][1] - systems[dif_system][1], 2)
                + math.pow(systems[system][2] - systems[dif_system][2], 2)
            )
            if distance > furthest:
                closest_dist = distance
                furthest_syst = dif_system
        if system % 1000 == 0:
            print(system / 100)
    return [math.sqrt(closest_dist), system, furthest_syst]


def create_cube(map_bounds, size, separation_factor, systems):
    print("creating cube...")
    for i in range(0, size):
        systems.append(
            [
                np.random.uniform(
                    low=map_bounds[0][0] * separation_factor,
                    high=map_bounds[1][0] * separation_factor,
                    size=None,
                ),
                np.random.uniform(
                    low=map_bounds[0][1] * separation_factor,
                    high=map_bounds[1][1] * separation_factor,
                    size=None,
                ),
                np.random.uniform(
                    low=map_bounds[0][2] * separation_factor,
                    high=map_bounds[1][2] * separation_factor,
                    size=None,
                ),
            ]
        )
    return systems


def create_sphere(size, separation_factor, systems):
    print("creating sphere...")
    for i in range(0, size):

        system = [
            np.random.uniform(low=1, high=147100.0 * separation_factor, size=None),
            np.random.uniform(low=0, high=6.283185307, size=None),
            np.random.uniform(low=3.1415321467, high=6.23185307, size=None),
        ]

        systems.append(
            [
                system[0] * math.sin(system[1]) * math.cos(system[2]),
                system[0] * math.sin(system[1]) * math.sin(system[2]),
                system[0] * math.cos(system[1]),
            ]
        )
    return systems


def system_random_selection(system_candidates):
    selected_system = np.random.randint(low=0, high=(len(system_candidates) - 1))
    return selected_system


def system_out(system_candidates, selected_system):
    selected_system[1] = selected_system[1] - 1

    if selected_system[1] > 0:
        system_index = system_candidates.index(selected_system)
        system_candidates[system_index] = selected_system
    else:
        system_candidates.remove(selected_system)

    return system_candidates


def create_random_system(current_system, separation_factor):

    new_system_sc = [
        np.random.uniform(
            low=3.2 * separation_factor, high=16 * separation_factor, size=None
        ),
        np.random.uniform(low=0, high=6.283185307, size=None),
        np.random.uniform(low=3, high=6.23185307, size=None),
    ]

    new_system_cc = [
        new_system_sc[0] * math.sin(new_system_sc[1]) * math.cos(new_system_sc[2]),
        new_system_sc[0] * math.sin(new_system_sc[1]) * math.sin(new_system_sc[2]),
        new_system_sc[0] * math.cos(new_system_sc[1]),
    ]

    system_true_possition = [
        current_system[0] + new_system_cc[0],
        current_system[1] + new_system_cc[1],
        current_system[2] + new_system_cc[2],
    ]

    return system_true_possition


def create_cluster(size, separation_factor):

    print("creating cluster...")
    chances = 1
    system_candidates = [[0, chances], [1, chances]]
    systems = [[0, 0, 0], [4.2, 7.1, 10.47]]

    for i in range(size - 2):
        selected_system_index = system_candidates[
            int(system_random_selection(system_candidates))
        ]
        system_candidates = system_out(system_candidates, selected_system_index)
        selected_system = systems[selected_system_index[0]]
        new_system = create_random_system(selected_system, separation_factor)
        systems.append(new_system)
        system_candidates.append([len(systems) - 1, chances])
    return systems


def refinate_cluster(max_distance, min_distance, systems, size):
    print("modifying distances...")
    refinated_cluster = systems.copy()
    min = math.pow(min_distance, 2)
    to_obliterate = []
    for system in range(0, size):
        if systems[system] not in to_obliterate:
            for dif_system in range(system + 1, size):
                distance = (
                    math.pow(systems[system][0] - systems[dif_system][0], 2)
                    + math.pow(systems[system][1] - systems[dif_system][1], 2)
                    + math.pow(systems[system][2] - systems[dif_system][2], 2)
                )
                if distance < min and systems[dif_system] not in to_obliterate:
                    to_obliterate.append(systems[dif_system])
                # elif distance > max:
                # to_obliterate.append(systems[dif_system])
        if system % 1000 == 0:
            print(system)
    print("obliterating ", len(to_obliterate), " systems...")
    for system in to_obliterate:
        refinated_cluster.remove(system)
    return refinated_cluster


def set_map_bounds(x, y, z):

    print("setting map bounds...")
    map_bounds = [[-x, -y, -z], [x, y, z]]
    return map_bounds


# distancia de esquina a esquina, 85530.49
map_bounds = set_map_bounds(34710.0, 21048.0, 13465.0)
systems = []
separation_factor = 2  # de esquina a esquina, 85530.49 * separation_factor
size = 10
systems = create_cluster(size, separation_factor)
systems = refinate_cluster(690.420, 3.0, systems, len(systems))
# systems =  refinate_cluster(690.420,3.0,systems, len(systems))
# systems =  refinate_cluster(690.420,3.0,systems, len(systems))
distances = closest_star(systems, len(systems), separation_factor)
systems = np.asarray(systems)
np_distances = np.asarray(distances)
d_mean = np.mean(np_distances[:, 0])
d_median = np.median(np_distances[:, 0])
d_min = np.amin(np_distances[:, 0])
d_max = np.amax(np_distances[:, 0])
d_fut = furthest_distance(systems, len(systems))
speed = 0.1
print("-----")
print("Distancia media de viaje: ", d_mean, " Ly")
print(
    "Tiempo de viaje a ",
    speed,
    " Ly/h: ",
    d_mean / (24 * speed),
    "dias --- ",
    d_mean / (24 * 365 * speed),
    " Años",
)
print("-----")
print("Distancia de viaje de caso mediana: ", d_median, " Ly")
print(
    "Tiempo de viaje a ",
    speed,
    " Ly/h: ",
    d_median / (24 * speed),
    "dias --- ",
    d_median / (24 * 365 * speed),
    " Años",
)
print("-----")
print("Menor distancia entre dos estrellas cercanas: ", d_min, " Ly")
print(
    "Tiempo de viaje a ",
    speed,
    " Ly/h: ",
    d_min / (24 * speed),
    "dias --- ",
    d_min / (24 * 365 * speed),
    " Años",
)
print("-----")
print("Mayor distancia entre dos estrellas cercanas: ", d_max, " Ly")
print(
    "Tiempo de viaje a ",
    speed,
    " Ly/h: ",
    d_max / (24 * speed),
    "dias --- ",
    d_max / (24 * 365 * speed),
    " Años",
)
print("-----")
print("Mayor distancia en linea recta entre dos estrellas: ", d_fut[0])
print(
    "Tiempo de viaje a ",
    speed,
    " Ly/h de la mayor distancia: ",
    d_fut[0] / (24 * speed),
    "dias --- ",
    d_fut[0] / (24 * 365 * speed),
    " Años",
)
with open("mapa.txt", "w") as outfile:
    outfile.writelines("%s\n" % system for system in systems)
    outfile.close()
with open("distancias.json", "w") as outfile:
    json.dump(distances, outfile)
    outfile.close()
with open("distancias.txt", "w") as outfile:
    outfile.writelines("%s\n" % distance for distance in distances)
    outfile.close()
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.scatter(systems[:, 0], systems[:, 1], systems[:, 2])
plt.show()

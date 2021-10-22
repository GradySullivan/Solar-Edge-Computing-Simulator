import random
from geopy.distance import geodesic as gd
import operator

from __main__ import *


def config_setup():
    config_info = {}
    files_lines = 1
    with open('config.txt', 'r') as file:
        reader = csv.reader(file, delimiter=':')
        next(reader)  # skip header
        for line in reader:
            files_lines += 1
            if line[0] == '--- Node Locations ---':
                break
            config_info[line[0]] = line[1]

    coords = []  # list of (lat/long) tuples
    with open('config.txt', 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for i in range(files_lines):
            next(reader)
        for line in reader:
            coords.append((line[0], line[1]))

    return config_info, coords


def generate_nodes(num_edges, num_servers, edge_pv_efficiency, edge_pv_area, server_cores, server_memory, coords, method):
    edge_computing_systems = {}  # dictionary: edge_site:servers
    # create edge sites
    for edge in range(num_edges):
        latitude, longitude, coords = generate_location(coords, method)
        edge_site = EdgeSystem(edge_pv_efficiency, edge_pv_area, latitude, longitude, edge)
        servers = np.array([])
        for server in range(num_servers):
            servers = np.append(servers, edge_site.get_server_object(server_cores, server_memory, edge_site))
        edge_site.servers = servers
        edge_computing_systems[edge_site] = servers
    return edge_computing_systems


def generate_location(coords, method):
    if method == 'random':
        lat = random.uniform(-90, 90)
        long = random.uniform(-180, 80)
        return lat, long, coords
    elif method == 'assigned':
        lat = coords[0][0]
        long = coords[0][1]
        coords.remove(coords[0])
        return lat, long, coords
    else:
        return None, None, coords


def generate_applications(file):
    # create applications
    applications = []  # initialize list of class instances
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)  # skip header
        for row in csv_reader:
            runtime = int(row[2])
            cores = int(row[3])
            memory = int(row[5])
            applications.append(Application(runtime, cores, memory))  # instance for each application
    return applications


def generate_irradiance_list(file):
    irr_list = []
    with open(file, 'r') as txt_file:
        txt_reader = csv.reader(txt_file, delimiter=',')
        next(txt_reader)  # skip header
        for row in txt_reader:
            irr_interval = []
            for value in row:
                irr_interval.append(float(value))
            irr_list.append(irr_interval)
    return irr_list


def get_distances(edge_computing_systems, num_edges):
    if num_edges == 1:
        return None
    location_distances = {}  # dictionary lookup table; (loc1, loc2): distance
    if len(edge_computing_systems) > 1:  # only does if more than one node
        combos = itertools.combinations(edge_computing_systems, 2)  # every combination of two nodes
        for pair in combos:
            loc1 = (pair[0].lat, pair[0].long)  # coordinates for location 1
            loc2 = (pair[1].lat, pair[1].long)  # coordinates for location 2
            location_distances[pair] = gd(loc1, loc2).km  # calculate distance between locations in km, add to dictionary
    return location_distances


def get_shortest_distances(edge_computing_systems, location_distances, num_edges):
    if num_edges == 1:
        return None
    shortest_distances = {}
    for edge, key in itertools.product(edge_computing_systems.keys(), location_distances.keys()):
        potential_shortest = {}
        if (key[0] == edge or key[1] == edge) and key[0] != edge:
            potential_shortest[key[0]] = location_distances[key]
        else:
            potential_shortest[key[1]] = location_distances[key]
        shortest_distances[edge] = min(potential_shortest.items(), key=operator.itemgetter(1))
    return shortest_distances


def check_min_req(application_list, edge_sites, server_cores, server_memory):
    max_cores, max_memory = 0, 0

    for app in application_list:
        if app.cores > max_cores:
            max_cores = app.cores
        if app.memory > max_memory:
            max_memory = app.memory

    if max_cores > server_cores and max_memory > server_memory:
        print(f'Allotted {server_cores} core(s) per server. Minimum of {max_cores} required')
        print(f'Allotted {server_memory} MB of memory per server. Minimum of {max_memory} MB required')
        quit()
    if max_cores > server_cores:
        print(f'Allotted {server_cores} core(s) per server. Minimum of {max_cores} required')
        quit()
    if max_memory > server_memory:
        print(f'Allotted {server_memory} MB of memory per server. Minimum of {max_memory} MB required')
        quit()
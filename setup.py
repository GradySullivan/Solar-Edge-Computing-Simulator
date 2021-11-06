import operator
import random

from __main__ import *


def config_setup():
    """
    :return: config_info: dictionary containing parameter:value pairs
    """
    """Converts parameters from config.txt into a dictionary for the simulator to reference when needed"""
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
    config_info['Coords'] = coords

    return config_info


def generate_nodes(num_edges: int, num_servers: int, edge_pv_efficiency: float, edge_pv_area: float, server_cores: int,
                   server_memory: int, battery: float, coords: list, method: str):
    """
    :param battery: amount of energy that can be stored
    :param num_edges: number of nodes in the edge computing system
    :param num_servers: number of servers per node
    :param edge_pv_efficiency: efficiency of the PV cells
    :param edge_pv_area: area of solar panels
    :param server_cores: number of cores per server
    :param server_memory: amount of memory per core, in MB
    :param coords: coordinates of nodes
    :param method: algorithm to determine how nodes will be generated
    :return: edge_computing_systems (list of nodes)
    """
    """ Initialize nodes for edge computing system """
    edge_computing_systems = []
    # create edge sites
    for edge in range(num_edges):
        latitude, longitude = generate_location(coords, method)
        edge_site = EdgeSystem(edge_pv_efficiency, edge_pv_area, latitude, longitude, battery, edge)
        edge_site.servers = [edge_site.get_server_object(server_cores, server_memory, edge_site) for _
                             in range(num_servers)]
        edge_computing_systems.append(edge_site)
    return edge_computing_systems


def generate_location(coords: list, method: str):
    """
    :param coords: (latitude, longitude) tuples
    :param method: determines which location generation algorithm to choose
    :return: a single latitude, longitude
    """
    """Helper function which gets lat/long pairs for nodes"""
    if method == 'random':
        lat = random.uniform(-90, 90)
        long = random.uniform(-180, 180)
        return lat, long
    elif method == 'assigned':
        lat = coords[0][0]
        long = coords[0][1]
        coords.remove(coords[0])
        return lat, long
    else:
        return None, None


def generate_applications(file: str):
    """
    :param file: csv file containing applications
    :return: applications (list of applications)
    """
    """Convert application information from file into a list"""
    # create applications
    applications = []  # initialize list of class instances
    total_time = 0
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)  # skip header
        for index, row in enumerate(csv_reader):
            try:
                if int(row[3]) <= 64 and int(row[5]) <= 256000:
                    applications.append(Application(int(row[2]), int(row[3]), int(row[5])))  # instance for each application
                total_time += int(row[2])
            except:
                pass
    print(total_time)
    return applications


def generate_irradiance_list(file: str):
    """
    :param file: text file containing irradiance values for each time period
    :return: irr_list (tuple of tuples containing irradiance values for each node
    """
    """Convert solar irradiance information from file into a list"""
    irr_list = []
    with open(file, 'r') as txt_file:
        txt_reader = csv.reader(txt_file, delimiter=',')
        next(txt_reader)  # skip header
        for row in txt_reader:
            irr_interval = []
            for value in row:
                #irr_interval.append(float(value))
                irr_interval.append(random.randint(0, 56250))
            irr_list.append(tuple(irr_interval))
    return tuple(irr_list)


def get_distances(edge_computing_systems: list):
    """
    :param edge_computing_systems: list of nodes
    :return: location_distances (dictionary of (loc1,loc2):distance pairs)
    """
    """Helper function to calculate distances between each node"""
    if len(edge_computing_systems) == 1:
        return None
    location_distances = {}  # dictionary lookup table; (loc1, loc2): distance
    if len(edge_computing_systems) > 1:  # only does if more than one node
        combos = itertools.combinations(edge_computing_systems, 2)  # every combination of two nodes
        for pair in combos:
            loc1 = (pair[0].lat, pair[0].long)  # coordinates for location 1
            loc2 = (pair[1].lat, pair[1].long)  # coordinates for location 2
            location_distances[pair] = gd(loc1, loc2).km  # calculate distance between locations in km, add to dictionary
    return location_distances


def get_shortest_distances(edge_computing_systems: list):
    """
    :param edge_computing_systems: list of nodes
    :return: shortest_distances (dictionary of node:(closest node,distance) pairs)
    """
    """For each node, determines the nearest neighboring node"""
    if len(edge_computing_systems) == 1:
        shortest_distance = {edge_computing_systems[0]: (edge_computing_systems[0], 0)}
        return shortest_distance
    location_distances = get_distances(edge_computing_systems)
    shortest_distances = {}
    for edge, key in itertools.product(edge_computing_systems, location_distances.keys()):
        potential_shortest = {}
        if (key[0] == edge or key[1] == edge) and key[0] != edge:
            potential_shortest[key[0]] = location_distances[key]
        else:
            potential_shortest[key[1]] = location_distances[key]
        shortest_distances[edge] = min(potential_shortest.items(), key=operator.itemgetter(1))
    return shortest_distances


def check_min_req(application_list: list, server_cores: int, server_memory: int):
    """
    :param application_list: list of applications
    :param server_cores: cores per server
    :param server_memory: memory per server, in MB
    :return: None
    """
    """Determines if provided resources can support the application load"""
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
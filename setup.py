import csv
import random
import numpy as np
from __main__ import *
from edge_computing_system import *


def config_setup():
    config_info = {}
    with open('config.txt', 'r') as file:
        reader = csv.reader(file, delimiter=':')
        next(reader)  # skip header
        for line in reader:
            config_info[line[0]] = line[1]

    return int(config_info['Nodes']), int(config_info['Servers per Node']), int(config_info['Cores per Server']), \
           int(config_info['Memory per Server']), float(config_info['Power per Server Needed']), \
           float(config_info['PV Efficiency']), float(config_info['PV Area']), config_info['Traces'].strip(), \
            config_info['Irradiance List'].strip()


def generate_nodes(num_edges, num_servers, edge_pv_efficiency, edge_pv_area, server_cores, server_memory):
    edge_computing_systems = {}  # dictionary: edge_site:servers
    servers = np.array([])

    # create edge sites
    for edge in range(num_edges):
        latitude, longitude = generate_location('random')
        edge_site = EdgeSystem(edge_pv_efficiency, edge_pv_area, latitude, longitude)
        for server in range(num_servers):
            servers = np.append(servers, edge_site.get_server_object(server_cores, server_memory))
        edge_site.servers = servers
        edge_computing_systems[edge_site] = servers
    return edge_computing_systems


def generate_location(method):
    if method == 'random':
        lat = random.uniform(-90, 90)
        long = random.uniform(-180, 80)
        return lat, long
    else:
        return None, None


def generate_applications(file):
    # create applications
    applications = []  # initialize list of class instances
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)  # skip header
        for row in csv_reader:
            runtime = int(row[2])
            cores = int(row[3])
            try:
                memory = int(row[5])
            except:
                continue
            applications.append(Application(runtime, cores, memory))  # instance for each application
    return applications


def generate_irradiance_list(file):
    irr_list = []
    with open(file, 'r') as txt_file:
        txt_reader = csv.reader(txt_file, delimiter=',')
        next(txt_reader)  # skip header
        for row in txt_reader:
            irr_list.append(float(row[0]))
    return irr_list


def check_min_req(application_list, edge_sites, server_cores, server_memory):
    max_cores = 0
    max_memory = 0

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
    elif max_memory > server_memory:
        print(f'Allotted {server_memory} MB of memory per server. Minimum of {max_memory} MB required')
        quit()

import csv
import numpy as np


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

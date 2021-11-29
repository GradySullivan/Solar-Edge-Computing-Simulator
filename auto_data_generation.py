import os
import random
from datetime import datetime

import __main__
from compile_irradiances import *


def write_config(policy: str, migration_cost: float, battery: float):
    with open('config.txt', 'w') as config:
        config.write('Config\n')
        config.write('Nodes: 3\n')
        config.write('Servers per Node: 225\n')
        config.write('Cores per Server: 64\n')
        config.write('Memory per Server: 256000\n')
        config.write(f'Battery Size: {battery}\n')
        config.write('Power per Server Needed: 250\n')
        config.write('PV Efficiency: .22\n')
        config.write('PV Area: 100\n')
        config.write(f'Cost Multiplier: {migration_cost}\n')
        config.write('Node Placement: assigned\n')
        config.write(f'Policy: {policy}\n')
        config.write('Global Applications: False\n')
        config.write('Traces: traces-2019.csv\n')
        config.write('Irradiance List: irradiance.txt\n')
        config.write('Diagnostics: True\n')
        config.write('--- Node Locations ---\n')
        config.write('40.0755, -105.194\n')
        config.write('30.22859, -97.8138\n')
        config.write('44.17902, -73.6143')


if __name__ == '__main__':
    trials = 1

    num_servers = 225
    cost_per_server = 250
    pv_area = 100
    pv_efficiency = .22

    methods = ['passive', 'greedy', 'super-greedy', 'YOLO', 'look-ahead', 'practical']
    migration_costs = [0]
    batteries = [0]

    if trials > 1:
        # find number of irradiance files
        counter = 0
        for file in os.listdir('processed'):
            counter += 1

        node_lists = []
        for trial in range(trials):
            node_list = random.sample(range(1, counter), 3)
            node_lists.append(node_list)

        needed_power = num_servers * cost_per_server
        for node_list in node_lists:
            print(f'Nodes {node_list[0]}, {node_list[1]}, {node_list[2]}')
            compile_irradiances(1)

            for method in methods:
                for cost in migration_costs:
                    for battery in batteries:
                        write_config(method, cost, battery)
                        os.system('__main__.py')  # for Windows
                        # os.system('python3 __main__.py')  # for Linux

    else:
        compile_irradiances(1)

        for method in methods:
            for cost in migration_costs:
                for battery in batteries:
                    write_config(method, cost, battery)
                    os.system('__main__.py')  # for Windows
                    # os.system('python3 __main__.py')  # for Linux
                    if method == 'passive':
                        break

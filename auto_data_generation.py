import os
import random
from datetime import datetime

import __main__
from compile_irradiances import *


def write_config(policy: str, migration_cost: float, battery: float, pv_area):
    """
    :param policy: what type of migration policy will be used
    :param migration_cost: multiplier used in migration cost
    :param battery: how large the battery storage is, in Joules
    :param pv_area: area of PV cells, in m^2
    :return: None
    """
    with open('config.txt', 'w') as config:
        config.write('Config\n')
        config.write('Nodes: 3\n')
        config.write('Servers per Node: 1\n')
        config.write('Cores per Server: 64\n')
        config.write('Memory per Server: 256000\n')
        config.write(f'Battery Size: {battery}\n')
        config.write('Power per Server Needed: 250\n')
        config.write('PV Efficiency: .22\n')
        config.write(f'PV Area: {pv_area}\n')
        config.write(f'Cost Multiplier: {migration_cost}\n')
        config.write('Node Placement: assigned\n')
        config.write(f'Policy: {policy}\n')
        config.write('Global Applications: False\n')
        config.write('Traces: traces.csv\n')
        config.write('Irradiance List: irradiance.txt\n')
        config.write('Diagnostics: False\n')
        config.write('--- Node Locations ---\n')
        config.write('33, -112\n')
        config.write('36, 140\n')
        config.write('56, 38')


if __name__ == '__main__':
    methods = ['passive', 'greedy', 'super-greedy', 'YOLO', 'look-ahead', 'practical']
    migration_costs = [0, 0.001, 0.01, 0.1]
    batteries = [0]
    pv_area = 1000

    get_max_values()

    compile_irradiances(1)

    for method in methods:
        for cost in migration_costs:
            for battery in batteries:
                write_config(method, cost, battery, pv_area)
                if os.name == 'nt':  # for Windows
                    os.system('__main__.py')
                elif os.name == 'posix':  # for Linux
                    os.system('python3 __main__.py')
                if method == 'passive':
                    break

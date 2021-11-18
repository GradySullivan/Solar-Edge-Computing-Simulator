import os
import compile_irradiances
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
        config.write('Global Applications: True\n')
        config.write('Traces: traces-2019.csv\n')
        config.write('Irradiance List: irradiance.txt\n')
        config.write('Diagnostics: False\n')
        config.write('--- Node Locations ---\n')
        config.write('33.4484, -112.0740\n')
        config.write('40.7128, -74.0060\n')
        config.write('35.6762, 139.6503')


if __name__ == '__main__':
    num_servers = 225
    cost_per_server = 250
    pv_area = 100
    pv_efficiency = .22

    needed_power = num_servers * cost_per_server
    max_irr_pre_scale = get_max_irradiance()
    scale = needed_power / pv_area / pv_efficiency / max_irr_pre_scale

    compile_irradiances(scale)

    methods = ['passive', 'greedy', 'super-greedy', 'YOLO', 'look-ahead', 'practical']
    migration_costs = [0]
    batteries = [0]
    for method in methods:
        for cost in migration_costs:
            for battery in batteries:
                write_config(method, cost, battery)
                os.system('__main__.py')  # for Windows
                # os.system('python3 __main__.py')  # for Linux

import os
import random
from datetime import datetime

import __main__
from compile_irradiances import *


def write_config(policy: str, battery: float, pv_area):
    """
    :param policy: what type of migration policy will be used
    :param battery: how large the battery storage is, in Joules
    :param pv_area: area of PV cells, in m^2
    :return: None
    """
    """Writes Config File - allows for automatic changes"""
    with open('config.txt', 'w') as config:
        config.write('Config\n')
        config.write('Nodes: 3\n')
        config.write('Servers per Node: 1\n')
        config.write('Cores per Server: 1\n')
        config.write('Memory per Server: 4096\n')
        config.write(f'Battery Size: {battery}\n')
        config.write('Power per Server Needed: 250\n')
        config.write('PV Efficiency: .22\n')
        config.write(f'PV Area: {pv_area}\n')
        config.write(f'Delay Function: 40885*x**-0.702\n')
        config.write('Node Placement: assigned\n')
        config.write(f'Policy: {policy}\n')
        config.write('Global Applications: False\n')
        config.write('Traces: traces.csv\n')
        config.write('Irradiance List: irradiance.txt\n')
        config.write('Diagnostics: False\n')
        config.write('--- Node Locations ---\n')
        config.write('35.652832, 139.839478\n')
        config.write('37.5326, 127.024612\n')
        config.write('34.672314, 135.484802\n')
        config.write('19.07609, 72.877426\n')
        config.write('1.29027, 103.851959\n')
        config.write('-33.867487, 151.20699\n')
        config.write('55.50816463, -106.5924976\n')
        config.write('50.110573, 8.684966\n')
        config.write('53.35014, -6.266155\n')
        config.write('51.509865, -0.118092\n')
        config.write('48.864716, 2.349014\n')
        config.write('-23.533773, -46.62529\n')
        config.write('38.75066, -77.475143\n')
        config.write('40.358615, -82.706838\n')
        config.write('38.837522, -120.895824\n')
        config.write('44, -120.5')


if __name__ == '__main__':
    methods = ['passive', 'greedy', 'super-greedy', 'YOLO', 'look-ahead', 'practical']
    batteries = [0]
    pv_area = 1000

    get_max_values()
    compile_irradiances()
    print('irradiances compiled')

    for method in methods:
        for battery in batteries:
            write_config(method, battery, pv_area)
            if os.name == 'nt':  # for Windows
                os.system('__main__.py')
            elif os.name == 'posix':  # for Linux
                os.system('python3 __main__.py')

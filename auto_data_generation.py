import os
import random
from datetime import datetime

import __main__
from compile_irradiances import *


def write_config(file: str, policy: str, battery: float, pv_area):
    """
    :param file: file with trace data to run
    :param policy: what type of migration policy will be used
    :param battery: how large the battery storage is, in Joules
    :param pv_area: area of PV cells, in m^2
    :return: None
    """
    """Writes Config File - allows for automatic changes"""
    with open('config.txt', 'w') as config:
        config.write('Config\n')
        config.write('Servers per Node: 1\n')
        config.write('Cores per Server: 1\n')
        config.write('Memory per Server: 99999\n')
        config.write(f'Battery Size: {battery}\n')
        config.write('Power per Server Needed: 250\n')
        config.write('PV Efficiency: .22\n')
        config.write(f'PV Area: {pv_area}\n')
        config.write(f'Delay Function: 40885*x**-0.702\n')
        config.write('Node Placement: assigned\n')
        config.write(f'Policy: {policy}\n')
        config.write('Global Applications: False\n')
        config.write('Degradable Applications: False\n')
        config.write('Degradable Applications: True\n')
        config.write(f'Traces: {file}\n')
        config.write('Irradiance List: irradiance.txt\n')
        config.write('Diagnostics: False\n')


if __name__ == '__main__':
    methods = ['passive', 'greedy', 'super-greedy', 'YOLO', 'look-ahead', 'practical']
    files = ['traces.csv']
    batteries = [0]
    pv_area = 1000

    get_max_values()
    compile_irradiances()

    for file in files:
        for method in methods:
            print(method)
            for battery in batteries:
                write_config(file, method, battery, pv_area)
                if os.name == 'nt':  # for Windows
                    os.system('__main__.py')
                elif os.name == 'posix':  # for Linux
                    os.system('python3 __main__.py')

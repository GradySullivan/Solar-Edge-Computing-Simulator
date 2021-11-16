import os
import compile_irradiances
import __main__


def write_config(policy: str):
    with open('config.txt', 'w') as config:
        config.write('Config\n')
        config.write('Nodes: 3\n')
        config.write('Servers per Node: 225\n')
        config.write('Cores per Server: 64\n')
        config.write('Memory per Server: 256000\n')
        config.write('Battery Size: 0\n')
        config.write('Power per Server Needed: 250\n')
        config.write('PV Efficiency: .22\n')
        config.write('PV Area: 100\n')
        config.write('Cost Multiplier: 0.000\n')
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
    methods = ['passive', 'greedy', 'super-greedy', 'YOLO', 'look-ahead', 'practical']

    for method in methods:
        write_config(method)
        os.system('__main__.py')

import os
import csv
import time


def get_max_values():
    # determine scaling
    lst = []
    for file in os.listdir('Irradiance Lists'):
        with open(f'Irradiance Lists/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for line in reader:
                if line != '':
                    for i in range(1):
                        try:
                            if float(line[1]) < 0:
                                lst2.append(float(0))
                            else:
                                lst2.append(float(line[1]))
                        except ValueError:
                            lst2.append(0)
                        if len(lst2) > 50000000:
                            break
            lst.append((file, lst2))

    max_list = []
    for i in lst:
        max_list.append((i[0], max(i[1][0:864])))
    for index, value in enumerate(max_list):
        print(f'File: {value[0]}, Value: {value[1]}')


def compile_irradiances(scale: float):
    """
    :param scale: factor to multiply irradiance values by
    :return: None
    """
    lst = []
    for file in os.listdir('Irradiance Lists'):
        with open(f'Irradiance Lists/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for line in reader:
                for i in range(300):
                    try:
                        if float(line[1]) > 0:
                            lst2.append(float(line[1]) * scale)
                        else:
                            lst2.append(0)
                    except ValueError:
                        lst2.append(float(0))
                    if len(lst2) >= 5000000:
                        break
            lst.append(lst2)

    reformatted = []
    inner_len = min([len(i) for i in lst])
    for i in range(inner_len):
        temp = []
        for sublist in lst:
            temp.append(sublist[i])
        reformatted.append(temp)

    with open('irradiance.txt', 'w', newline='') as file:
        wr = csv.writer(file)
        file.write('irradiances\n')
        wr.writerows(reformatted)


def compile_irradiances2():
    data = []
    for file in os.listdir('Irradiance Lists'):
        with open(f'Irradiance Lists/{file}', 'r') as f:
            current_data = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for index, line in enumerate(reader):
                for _ in range(300):
                    if line[1] == '' or float(line[1]) < 0:
                        current_data.append(float(0))
                    else:
                        current_data.append(float(line[1]))
        data.append(current_data)

    final_data = [[location[index] for location in data] for index, _ in enumerate(data[0])]

    with open('irradiance.txt', 'w', newline='') as file:
        wr = csv.writer(file)
        file.write('irradiances\n')
        wr.writerows(final_data)
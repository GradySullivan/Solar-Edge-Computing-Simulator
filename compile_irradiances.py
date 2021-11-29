import os
import csv


def get_max_values():
    # determine scaling
    lst = []
    for file in os.listdir('processed'):
        with open(f'processed/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for line in reader:
                if line != '':
                    for i in range(1):
                        if float(line[4]) < 0:
                            lst2.append(float(0))
                        else:
                            lst2.append(float(line[4]) * 1)
                        if len(lst2) > 2000000:
                            break
            lst.append((file, lst2))

    max_list = []
    for i in lst:
        max_list.append((i[0], max(i[1][0:1000])))
    for index, value in enumerate(max_list):
        if value[1] < 1:
            print(f'File: {value[0]}, Value: {value[1]}')


def get_max_irradiance():
    # determine scaling
    current_max_lst = []
    for file in os.listdir('Irradiance Lists'):
        lst = []
        with open(f'Irradiance Lists/{file}', 'r') as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for index, line in enumerate(reader):
                if index > 1000:
                    break
                lst.append(float(line[4]))
            current_max_lst.append(max(lst))
    return max(current_max_lst)


def get_max_irradiance_random(nodes: list):
    # determine scaling
    files = []
    for index, file in enumerate(os.listdir('processed')):
        for node in nodes:
            if node == index:
                files.append(file)

    lst = []
    for file in files:
        with open(f'processed/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for line in reader:
                print(line)
                if line != '':
                    for i in range(3600):
                        if float(line[4]) < 0:
                            lst2.append(float(0))
                        else:
                            lst2.append(float(line[4]) * 1)
                if len(lst2) > 100000 * 3600:
                    break
            lst.append(lst2)
    max_list = []
    for i in lst:
        max_list.append(max(i))
    return max(max_list)


def compile_irradiances(scale: float):
    lst = []
    for file in os.listdir('Irradiance Lists'):
        with open(f'Irradiance Lists/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for line in reader:
                for i in range(3600):
                    if float(line[4]) < 0:
                        lst2.append(float(0))
                    else:
                        lst2.append(float(line[4]) * scale)
                    if len(lst2) >= 10000000:
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


if __name__ == '__main__':
    print(get_max_values())

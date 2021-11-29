import os
import csv


def compile_irradiances(scale: float):
    lst = []
    for file in os.listdir('Irradiance Lists'):
        with open(f'Irradiance Lists/{file}', 'r') as f:
            lst2 = []
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for line in reader:
                for i in range(3600):
                    if float(line[5]) < 0:
                        lst2.append(float(0))
                    else:
                        lst2.append(float(line[5]) * scale)
                    if len(lst2) >= 1000000:
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
    pass

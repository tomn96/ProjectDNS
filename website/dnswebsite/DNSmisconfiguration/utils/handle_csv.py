import csv


def handle_csv_file(file_name):
    result = list()
    with open(file_name, 'r') as csv_file:
        file_reader = csv.reader(csv_file)
        for row in file_reader:
            result.append(row)
    return result

import csv


def handle_csv_file(file):

    utf8 = (line.decode('utf-8') for line in file)
    file_reader = csv.reader(utf8)

    result = [row for row in file_reader]

    return result

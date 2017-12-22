import csv
from dan.dit.umsatz.umsatz import Umsatz


def read_umsatz(file_name):
    with open(file_name) as csv_file:
        dialect = csv.Sniffer().sniff(csv_file.read(1024), delimiters=";,")
        csv_file.seek(0)
        umsatz_data = csv.DictReader(csv_file, dialect=dialect)
        return Umsatz(umsatz_data)

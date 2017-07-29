import csv
from dan.dit.umsatz.umsatz import Umsatz


def read_umsatz(file_name):
    with open(file_name) as csv_file:
        umsatz_data = csv.DictReader(csv_file)
        return Umsatz(umsatz_data)

import datetime as dt
from itertools import accumulate
import sys


def sort_lists_simultaneous_by_first_key(*lists):
    return map(list, zip(*sorted(zip(*lists), key=lambda multis: multis[0])))


def pretty_delta(delta, currency):
    delta_str = str(delta) + currency
    if delta >= 0:
        return "+" + delta_str
    return "-" + delta_str

DATE_FORMAT = "%d.%m.%y"


def pretty_date(date):
    return date.strftime(DATE_FORMAT)


class Umsatz:
    def __init__(self, data_reader):
        self.dates = []
        self.deltas = []
        self.texts = []
        self.currencies = []
        for row in data_reader:
            self.dates.append(dt.datetime.strptime(row["Buchungstag"], DATE_FORMAT))
            self.deltas.append(float(row["Betrag"].replace(",", ".")))
            self.currencies.append(row["Waehrung"])
            self.texts.append((row["Buchungstext"], row["Verwendungszweck"], row["Beguenstigter/Zahlungspflichtiger"]))
        result = sort_lists_simultaneous_by_first_key(self.dates,
                                                      self.deltas,
                                                      self.texts,
                                                      self.currencies)
        self.dates, self.deltas, self.texts, self.currencies = result

        self.values = list(accumulate(self.deltas))
        self.descriptions = ["\n".join((pretty_date(date), *text, pretty_delta(delta, currency)))
                             for date, text, delta, currency
                             in zip(self.dates, self.texts, self.deltas, self.currencies)]

    def currency(self):
        currencies_count = len(set(self.currencies))
        if currencies_count == 0:
            return ""
        elif currencies_count == 1:
            return self.currencies[0]
        print("Warning! Multiple currencies in use!", file=sys.stderr)
        return self.currencies[0] + "(!?)"

    def date_name(self):
        return "Buchungstag"

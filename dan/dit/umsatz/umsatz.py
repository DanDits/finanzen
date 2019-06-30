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


def parse_buchungstag(row):
    try:
        return dt.datetime.strptime(row["Buchungstag"], DATE_FORMAT)
    except:
        return dt.datetime.strptime(row["Buchungstag"], "%d.%m.%Y")


def parse_value_robust(value_string, soll_haben=None):
    cleaned_value_string = value_string
    if "," in value_string and "." in value_string:
        # we just assume it is a german number then...
        cleaned_value_string = cleaned_value_string.replace(r".", "")
    cleaned_value_string = cleaned_value_string.replace(",", ".")
    value = float(cleaned_value_string)
    if soll_haben and "S" in soll_haben:
        return -value
    return value


def guess_delta_key(keys):
    if "Betrag" in keys:
        return "Betrag"
    return "Umsatz"


def guess_currency_key(keys):
    if "Währung" in keys:
        return "Währung"
    return "Waehrung"


def guess_verwendungszweck_key(keys):
    if "Verwendungszweck" in keys:
        return "Verwendungszweck"
    return 'Vorgang/Verwendungszweck'


def guess_empfaenger_key(keys):
    if "Beguenstigter/Zahlungspflichtiger" in keys:
        return "Beguenstigter/Zahlungspflichtiger"
    return 'Empfänger/Zahlungspflichtiger'


class Umsatz:
    def __init__(self, data_reader):
        self.dates = []
        self.deltas = []
        self.texts = []
        self.currencies = []
        for row in data_reader:
            self.dates.append(parse_buchungstag(row))
            self.deltas.append(parse_value_robust(row[guess_delta_key(row.keys())],
                                                  row["Soll/Haben"] if "Soll/Haben" in row.keys() else None))
            self.currencies.append(row[guess_currency_key(row.keys())])
            self.texts.append((row["Buchungstext"] if "Buchungstext" in row.keys() else "",
                               row[guess_verwendungszweck_key(row.keys())],
                               row[guess_empfaenger_key(row.keys())]))
        result = sort_lists_simultaneous_by_first_key(self.dates,
                                                      self.deltas,
                                                      self.texts,
                                                      self.currencies)
        self.dates, self.deltas, self.texts, self.currencies = result

        self.values = list(accumulate(self.deltas))
        self.descriptions = [self._make_description(date, text, delta, currency)
                             for date, text, delta, currency
                             in zip(self.dates, self.texts, self.deltas, self.currencies)]

    def _same_entry(self, other, index, other_index):
        return (self.dates[index] == other.dates[other_index]
            and self.deltas[index] == other.deltas[other_index]
            and self.texts[index] == other.texts[other_index]
            and self.currencies[index] == other.currencies[other_index])

    # god is this awful
    def merge(self, other):
        for i in range(len(other.dates)):
            insert_index = -1
            for j in range(len(self.dates)):
                if self._same_entry(other, j, i):
                    insert_index = -1
                    break
                if insert_index == -1 or other.dates[i] >= self.dates[j]:
                    insert_index = j + 1
            if insert_index != -1:
                self.dates.insert(insert_index, other.dates[i])
                self.deltas.insert(insert_index, other.deltas[i])
                self.texts.insert(insert_index, other.texts[i])
                self.currencies.insert(insert_index, other.currencies[i])
                self.values.insert(insert_index, self.values[-1] + self.deltas[-1])
                self.descriptions.insert(insert_index, self._make_description(other.dates[i], other.texts[i], other.deltas[i], other.currencies[i]))

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

    def _make_description(self, date, text, delta, currency):
        return "\n".join((pretty_date(date), *text, pretty_delta(delta, currency)))

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import dan.dit.pathutil as pathutil
from dan.dit.lib.AnnoteFinder import AnnoteFinder
from dan.dit.umsatz.parse_csv import read_umsatz


def total_over_time(umsatz):
    dates = mdates.date2num(umsatz.dates)
    values = umsatz.values
    description = umsatz.descriptions
    fig = plt.figure()
    plt.plot_date(dates, values, "-o")
    add_annotes(fig, dates, values, description)
    plt.show()


def deltas_over_time(umsatz):
    # skip first as this is the start value
    dates = mdates.date2num(umsatz.dates)[1:]
    values = umsatz.deltas[1:]
    description = umsatz.descriptions[1:]
    fig = plt.figure()
    plt.plot_date(dates, values, "-o")
    add_annotes(fig, dates, values, description)
    plt.plot((min(dates), max(dates)), (0, 0), "-")
    plt.show()


def add_annotes(fig, x, y, annotes):
    af = AnnoteFinder(x, y, annotes, tolPercent=0.02)
    fig.canvas.mpl_connect('button_press_event', af)


if __name__ == "__main__":
    name = pathutil.umsatz_file("umsatz_2017_01__2017_07.csv")
    curr_umsatz = read_umsatz(name)
    deltas_over_time(curr_umsatz)
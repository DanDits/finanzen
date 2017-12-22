import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import dan.dit.pathutil as pathutil
from dan.dit.lib.AnnoteFinder import AnnoteFinder
from dan.dit.umsatz.parse_csv import read_umsatz
from dan.dit.umsatz.umsatz import pretty_date, DATE_FORMAT
from matplotlib.widgets import Button


def _set_time_label_format(ax):
    fmt = mdates.DateFormatter(DATE_FORMAT)
    ax.xaxis.set_major_formatter(fmt)


def total_over_time(umsatz):
    dates = mdates.date2num(umsatz.dates)
    values = umsatz.values
    description = umsatz.descriptions
    fig = plt.figure()

    ax = plt.plot_date(dates, values, "-o")
    _set_time_label_format(plt.axes())
    plt.ylim(ymin=0)
    plt.xlabel(umsatz.date_name())
    plt.ylabel("Betrag in " + umsatz.currency())
    plt.title("Kontostand vom " + pretty_date(umsatz.dates[0]) + " bis zum " + pretty_date(umsatz.dates[-1]))
    af = add_annotes(fig, dates, values, descriptions_and_current_state(description, values, umsatz.currency()))
    add_clear_annotates(fig, af)
    plt.show()


def descriptions_and_current_state(descriptions, values, currency):
    return ["{}\nKontostand: {:.2f}{}".format(desc, value, currency)
                                     for desc, value in zip(descriptions, values)]


def deltas_over_time(umsatz, skip_first=True):
    start_index = 0
    if skip_first:
        start_index = 1  # arrays start at 1 http://i.imgur.com/ehiodI5.png
    dates = mdates.date2num(umsatz.dates)[start_index:]
    values = umsatz.deltas[start_index:]
    description = umsatz.descriptions[start_index:]
    fig = plt.figure()
    positive_indices = [i for (i, value) in enumerate(values) if value >= 0]
    negative_indices = [i for (i, value) in enumerate(values) if value < 0]
    plt.plot_date([dates[i] for i in positive_indices], [values[i] for i in positive_indices], "o", color="black")
    plt.plot_date([dates[i] for i in negative_indices], [values[i] for i in negative_indices], "o", color="red")
    _set_time_label_format(plt.axes())
    add_annotes(fig, dates, values, descriptions_and_current_state(description, values, umsatz.currency()))
    plt.plot((min(dates), max(dates)), (0, 0), "-")
    plt.xlabel(umsatz.date_name())
    plt.ylabel("Betrag in " + umsatz.currency())
    plt.title("Einzelumsätze vom " + pretty_date(umsatz.dates[0]) + " bis zum " + pretty_date(umsatz.dates[-1]))
    plt.show()


def add_annotes(fig, x, y, annotes):
    af = AnnoteFinder(x, y, annotes, tolPercent=0.02)
    fig.canvas.mpl_connect('button_press_event', af)
    return af



def add_clear_annotates(fig, annotate_finder):
    # x, y (fractions), width, height (fractions)
    reset_button_ax = fig.add_axes([0.6, 0.025, 0.4, 0.04])
    bcut = Button(reset_button_ax, 'Clear annotations', color='green', hovercolor='green')
    def _clear(mouse_event):
        if mouse_event.inaxes != reset_button_ax:
            return
        annotate_finder.clearAnnotations()
    bcut.connect_event('button_press_event',  _clear)


if __name__ == "__main__":
    name = pathutil.umsatz_file("umsatz_2017_01__2017_07.csv")
    curr_umsatz = read_umsatz(name)
    name = pathutil.umsatz_file("umsatz_2017_08__2017_09.CSV")
    curr_umsatz2 = read_umsatz(name)
    curr_umsatz.merge(curr_umsatz2)
    name = pathutil.umsatz_file("20170901-20171221-5126525-umsatz.txt")
    curr_umsatz3 = read_umsatz(name)
    curr_umsatz.merge(curr_umsatz3)
    total_over_time(curr_umsatz)
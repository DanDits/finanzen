import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import dan.dit.pathutil as pathutil
from dan.dit.lib.AnnoteFinder import AnnoteFinder
from dan.dit.umsatz.parse_csv import read_umsatz
from dan.dit.umsatz.umsatz import pretty_date, DATE_FORMAT
from matplotlib.widgets import Button


def _set_time_label_format(ax):
    fmt = mdates.DateFormatter(DATE_FORMAT)
    ax.xaxis.set_major_formatter(fmt)


def find_data_before_gehalt(umsatz):
    gehalt_dates = []
    gehalt_values = []
    for i in range(len(umsatz.values)):
        if (len(umsatz.texts[i]) > 0 and any("GEHALT" in umsatz.texts[i][j].upper() for j in range(len(umsatz.texts[i])))):
            # could fail if first entry is a GEHALT but whatever
            gehalt_dates.append(umsatz.dates[i-1])
            gehalt_values.append(umsatz.values[i-1])
    return gehalt_dates, gehalt_values


def total_over_time(umsatz):
    dates = mdates.date2num(umsatz.dates)
    values = umsatz.values
    description = umsatz.descriptions
    fig = plt.figure()

    plt.plot_date(dates, values, "-o")
    _set_time_label_format(plt.axes())
    value_format = lambda x: format(int(x), ",")
    plt.axes().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: value_format(x)))

    gehalt_dates, gehalt_values = find_data_before_gehalt(umsatz)
    def format_gain(gain, isTrueGain=True):
        delta_text = "-+"[gain >= 0] if isTrueGain else ""
        return delta_text + "{0:,.2f}".format(gain) + umsatz.currency()
    # plot per-month(aka. when I got the paycheck) data
    plt.plot(gehalt_dates, gehalt_values, "-x")
    for d, v, prev in zip(gehalt_dates, gehalt_values, [0] + gehalt_values[:-1]):
        plt.axes().annotate(format_gain(v - prev, prev != 0),
                            (mdates.date2num(d), v),
                            xytext=(15,-15),
                            textcoords='offset points',
                            arrowprops=dict(arrowstyle='-|>'))

    # plot gain since first pay-check (aka. average per-month)
    total_color = [0,0.7,0.6,0.4]
    total_color_solid = total_color[:]
    total_color_solid[-1] = 1
    plt.plot((gehalt_dates[0], gehalt_dates[-1]),
              (gehalt_values[0], gehalt_values[-1]), "-", color=total_color)
    total_gain = gehalt_values[-1] - gehalt_values[0]
    total_gain_formatted = format_gain(total_gain)
    days = (gehalt_dates[-1] - gehalt_dates[0]).days
    gain_in_day = "    " + total_gain_formatted + " in " + str(days) + " Tagen"
    gain_per_year = "≙ " + format_gain(total_gain / days * 365.25) + " pro Jahr"
    gain_per_day = "≙ " + format_gain(total_gain / days) + " pro Tag"
    plt.axes().annotate(gain_in_day + "\n" + gain_per_year + "\n" + gain_per_day,
                        ((mdates.date2num(gehalt_dates[-1]) + mdates.date2num(gehalt_dates[0])) / 2,
                         (gehalt_values[-1] + gehalt_values[0]) / 2),
                        xytext=(-100, 100),
                        textcoords='offset points',
                        color=total_color_solid,
                        arrowprops=dict(arrowstyle='-|>', color=total_color))

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
    bcut = Button(reset_button_ax, 'Einzelangaben entfernen', color='green', hovercolor='green')
    def _clear(mouse_event):
        if mouse_event.inaxes != reset_button_ax:
            return
        annotate_finder.clearAnnotations()
    bcut.connect_event('button_press_event',  _clear)


if __name__ == "__main__":
    # export as CSV-CAMT (usually iso-8859-1 encoded)

    # to output file encoding file -i input.file
    # to convert from iso-8859-1 to utf8: iconv -f ISO-8859-1 -t UTF-8//TRANSLIT input.file -o output.file

    if "miriam" in pathutil.umsatz_dir():
        # Remove first lines that show metadata, remove last lines that show start and end values
        # Edit last column to have a proper name: Soll/Haben
        curr_umsatz = read_umsatz(pathutil.umsatz_file("Umsaetze_2018_09_03__2018_12_07_utf8.csv"))
        curr_umsatz.merge(read_umsatz(pathutil.umsatz_file("Umsaetze_DE96663912000097495203_2019.06.10.csv")))
        total_over_time(curr_umsatz)
    else:
        # year 2017
        curr_umsatz = read_umsatz(pathutil.umsatz_file("umsatz_2017_01__2017_07.csv"))
        curr_umsatz.merge(read_umsatz(pathutil.umsatz_file("umsatz_2017_08__2017_09.CSV")))
        curr_umsatz.merge(read_umsatz(pathutil.umsatz_file("20170901-20171221-5126525-umsatz.txt")))
        # year 2018
        curr_umsatz.merge(read_umsatz(pathutil.umsatz_file("umsatz_2018_01__2018_12_08_utf8.CSV")))
        # year 2019
        curr_umsatz.merge(read_umsatz(pathutil.umsatz_file("umsatz_2019_01__2019_06_10_utf8.CSV")))
        total_over_time(curr_umsatz)
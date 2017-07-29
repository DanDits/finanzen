import math

import matplotlib.pyplot as plt

# Credit to: http://scipy-cookbook.readthedocs.io/items/Matplotlib_Interactive_Plotting.html
class AnnoteFinder(object):
    """callback for matplotlib to display an annotation when points are
    clicked on.  The point which is closest to the click and within
    xtol and ytol is identified.

    Register this function like this:

    scatter(xdata, ydata)
    af = AnnoteFinder(xdata, ydata, annotes)
    connect('button_press_event', af)
    """

    def __init__(self, xdata, ydata, annotes, ax=None, xtol=None, ytol=None, tolPercent=None):
        self.data = list(zip(xdata, ydata, annotes))
        xdiff = (max(xdata) - min(xdata))
        ydiff = (max(ydata) - min(ydata))
        if xtol is None and ytol is None and tolPercent is not None:
            xtol = xdiff * tolPercent
            ytol = ydiff * tolPercent
        if xtol is None:
            xtol = (xdiff / float(len(xdata))) / 2
        if ytol is None:
            ytol = (ydiff / float(len(ydata))) / 2
        self.xtol = xtol
        self.ytol = ytol

        self.xDrawOffset = -xdiff * 0.01
        self.yDrawOffset = ydiff * 0.02
        if ax is None:
            self.ax = plt.gca()
        else:
            self.ax = ax
        self.drawnAnnotations = {}
        self.links = []

    def distance(self, x1, x2, y1, y2):
        """
        return the distance between two points
        """
        return (math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))

    def __call__(self, event):

        if event.inaxes:

            clickX = event.xdata
            clickY = event.ydata
            if (self.ax is None) or (self.ax is event.inaxes):
                annotes = []
                # print(event.xdata, event.ydata)
                for x, y, a in self.data:
                    # print(x, y, a)
                    if ((clickX - self.xtol < x < clickX + self.xtol) and
                            (clickY - self.ytol < y < clickY + self.ytol)):
                        annotes.append(
                            (self.distance(x, clickX, y, clickY), x, y, a))
                if annotes:
                    annotes.sort()
                    distance, x, y, annote = annotes[0]
                    self.drawAnnote(event.inaxes, x, y, annote)
                    for l in self.links:
                        l.drawSpecificAnnote(annote)

    def drawAnnote(self, ax, x, y, annote):
        """
        Draw the annotation on the plot
        """
        if (x, y) in self.drawnAnnotations:
            markers = self.drawnAnnotations[(x, y)]
            for m in markers:
                m.set_visible(not m.get_visible())
            self.ax.figure.canvas.draw_idle()
        else:
            t = ax.text(x + self.xDrawOffset, y + self.yDrawOffset, "%s" % (annote), )
            m = ax.scatter([x], [y], marker='d', c='r', zorder=100)
            self.drawnAnnotations[(x, y)] = (t, m)
            self.ax.figure.canvas.draw_idle()

    def drawSpecificAnnote(self, annote):
        annotesToDraw = [(x, y, a) for x, y, a in self.data if a == annote]
        for x, y, a in annotesToDraw:
            self.drawAnnote(self.ax, x, y, a)
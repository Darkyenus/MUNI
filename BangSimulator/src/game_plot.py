import matplotlib.pyplot as plt
import math
import numpy

plot_values = {}
plot_values_suggested_max = {}

def plot_add_value(series_name, value, suggested_max=None):
    values = plot_values.get(series_name)
    if values is None:
        values = []
        plot_values[series_name] = values

        if suggested_max is not None:
            plot_values_suggested_max[series_name] = suggested_max
    values.append(value)

def plot_display():
    f, subplots = plt.subplots(len(plot_values), sharex=True)
    plt.subplots_adjust(left=0.05, top=1-0.03, right=0.7)
    i = 0
    colors = ['b', 'g', 'r', 'c', 'm']
    for series_name, values in plot_values.items():
        subplot = subplots[i]
        subplot.plot(values, colors[i], label=series_name)
        subplot.set_ylim(bottom=0)
        plot_max = plot_values_suggested_max.get(series_name)
        if plot_max is not None:
            subplot.set_ylim(top=plot_max)
        else:
            subplot.set_ylim(top=math.ceil(max(values) * 1.1))

        z = numpy.polyfit(range(0, len(values)), values, deg=1)
        p = numpy.poly1d(z)
        subplot.plot([p(x) for x in range(0, len(values))], colors[i+1]+"--", label=str(p)[1:])

        subplot.legend(loc="center left", frameon=True, bbox_to_anchor=(1, 0.5)).draggable()
        i += 1
    print("Close plot to continue...")
    plt.show()
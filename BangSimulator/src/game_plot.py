import matplotlib.pyplot as plt
import math

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
    i = 0
    for series_name, values in plot_values.items():
        subplot = subplots[i]
        subplot.plot(values, label=series_name)
        subplot.set_ylim(bottom=0)
        plot_max = plot_values_suggested_max.get(series_name)
        if plot_max is not None:
            subplot.set_ylim(top=plot_max)
        else:
            subplot.set_ylim(top=math.ceil(max(values) * 1.1))
        subplot.legend(loc="best", frameon=False)
        i += 1
    plt.show()
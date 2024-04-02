from matplotlib import pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot(d_sionna, d_wi, scenario):
    d_sionna = 100 * np.array(d_sionna)
    d_wi = 100 * np.array(d_wi)

    df_sionna = pd.DataFrame(d_sionna, columns=['Base-Twin', '1R-Twin', '3R-Twin'])
    df_wi = pd.DataFrame(d_wi, columns=['Base-Twin', '1R-Twin', '3R-Twin'])

    ax = plt.figure(figsize=(5, 5)).add_subplot(1,1,1)

    bar_width = 0.35
    index = np.arange(len(df_sionna.columns))

    plots_sionna = df_sionna.plot(ax=ax, kind='bar', width=bar_width, position=0,
                                  color=['lightgreen', 'mediumseagreen', 'darkgreen'], edgecolor='black', legend=False)

    plots_wi = df_wi.plot(ax=ax, kind='bar', width=bar_width, position=1,
                          color=['lightblue', 'mediumblue', 'darkblue'], edgecolor='black', legend=False)

    ax.legend(loc='upper center', ncol=2, fontsize=10)
    plt.xticks(index + bar_width / 2, ['$\mathdefault{Acc_{(10,0)}}$', '$\mathdefault{Acc_{(10,1)}}$',
                                       '$\mathdefault{Acc_{(10,2)}}$'], fontsize=12, rotation=0)
    plt.yticks(fontsize=18)
    axes = plt.gca()
    axes.set_ylim([50, 100])
    axes.set_xlim([-0.5, len(df_sionna.columns) - 0.5])

    # Add grid lines that go through the y-axis ticks
    ax.grid(axis='y', linestyle='-', color='grey')

    plt.savefig(f'plots/{scenario}_compare.png', bbox_inches='tight', dpi=400)
    # plt.show()



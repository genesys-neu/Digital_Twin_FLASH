from matplotlib import pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_los(d, simulator):
    # d= 100*np.array([[0.523836096,0.717419592,0.726990546],[0.66929104,0.760386094,0.774503486],[0.766344896,0.787735874,0.794318105]])    # gps,img,lidar,all
    d = 100 * np.array(d)


    df = pd.DataFrame(d, columns=['B-Twin','1R-Twin', '3R-Twin'])
    print(df)
    ax = plt.figure(figsize=(6,3)).add_subplot(111)

    plots = df.plot(ax=ax, kind='bar',width=0.7,color=['#FBD6AB', '#D1D1D1','#2F5597'],edgecolor='black',legend=False)

    bars = ax.patches
    hatches = ''.join(h*len(df) for h in 'xo\.')
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)
        ######################################
    #     plots.annotate(format(bar.get_height(), '.2f'),(bar.get_x() + bar.get_width() ,bar.get_height()), ha='right', va='center',size=12, xytext=(0, 5),  weight='bold',textcoords='offset points')
    #     ######################################

    ax.legend(loc='center right', bbox_to_anchor=(1.01, 1.11), ncol=3,fontsize=14)
    plt.xticks([0,1,2],['$\mathdefault{Acc_{(10,0)}}$', '$\mathdefault{Acc_{(10,1)}}$', '$\mathdefault{Acc_{(10,2)}}$'],fontsize=18,rotation=0)
    plt.yticks(fontsize=18)
    axes = plt.gca()
    axes.set_ylim([50, 100])

    if 'sionna' in simulator:
        plt.savefig('plots/Sionna-LOS.png',bbox_inches='tight',dpi=400)
    elif 'WI' in simulator:
        plt.savefig('plots/WI-LOS.png',bbox_inches='tight',dpi=400)
    # plt.show()




######################NLOS
from matplotlib import pyplot as plt


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_nlos(d, simulator):
    # d= 100*np.array([[0.585930117,0.773015595,0.833195609],[0.746200108,0.826989243,0.862120697],[0.798447524,0.861584815,0.873762517]])    # gps,img,lidar,all
    # d= 100*np.array([[0.585930117,0.773015595,0.800838779029525],[0.746200108,0.826989243,0.844179575707209],[0.798447524,0.861584815,0.852268667987478]])    # gps,img,lidar,all
    d = 100 * np.array(d)


    df = pd.DataFrame(d, columns=['B-Twin','1R-Twin', '3R-Twin'])
    print(df)
    ax = plt.figure(figsize=(6,3)).add_subplot(111)

    plots = df.plot(ax=ax, kind='bar',width=0.7,color=['#FBD6AB', '#D1D1D1','#2F5597'],edgecolor='black',legend=False)

    bars = ax.patches
    hatches = ''.join(h*len(df) for h in 'xo\.')
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)
        ######################################
    #     plots.annotate(format(bar.get_height(), '.2f'),(bar.get_x() + bar.get_width() ,bar.get_height()), ha='right', va='center',size=12, xytext=(0, 5),  weight='bold',textcoords='offset points')
    #     ######################################

    ax.legend(loc='center right', bbox_to_anchor=(1.01, 1.11), ncol=3,fontsize=14)
    plt.xticks([0,1,2],['$\mathdefault{Acc_{(10,0)}}$', '$\mathdefault{Acc_{(10,1)}}$', '$\mathdefault{Acc_{(10,2)}}$'],fontsize=18,rotation=0)
    plt.yticks(fontsize=18)
    axes = plt.gca()
    axes.set_ylim([50, 100])


    if 'sionna' in simulator:
        plt.savefig('plots/Sionna-NLOS.png',bbox_inches='tight',dpi=400)
    elif 'WI' in simulator:
        plt.savefig('plots/WI-NLOS.png',bbox_inches='tight',dpi=400)
    # plt.show()

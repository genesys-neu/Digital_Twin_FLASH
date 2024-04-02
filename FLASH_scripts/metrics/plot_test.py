from matplotlib import pyplot as plt
# plt.rcParams["font.family"] = "Arial"

import numpy as np
import pandas as pd
from plot import plot


import pandas as pd

# Provided data
df_sionna_los = [
    [0.5444267787201617, 0.7300628870982894, 0.8171026669548291],
    [0.6863950599106696, 0.7954603799973149, 0.880592525953741],
    [0.7721658407594769, 0.8032771874739985, 0.8988340604744994]
]

df_sionna_nlos = [
    [0.6495389502514543, 0.7472447779365947, 0.7934894742199423],
    [0.7221216281881536, 0.7945006664017317, 0.8030688541406653],
    [0.8226914517592807, 0.8916792770567048, 0.9059717066385083]
]

df_WI_los = [
    [0.5238360958569666, 0.6692910402081916, 0.7663448955479667],
    [0.7174195916483261, 0.7603860944785873, 0.787735874167965],
    [0.7730155951979739, 0.8269892425848147, 0.8615848149293667]
]

df_WI_nlos = [
    [0.5859301172789049, 0.7462001080346313, 0.798447523808121],
    [0.7269905460129503, 0.7745034862922783, 0.7943181049754978],
    [0.8008387790295254, 0.8441795757072095, 0.8522686679874782]
]

# Create DataFrames
df_sionna_los = pd.DataFrame(df_sionna_los, columns=['Base-Twin', '1R-Twin', '3R-Twin'])
df_sionna_nlos = pd.DataFrame(df_sionna_nlos, columns=['Base-Twin', '1R-Twin', '3R-Twin'])
df_WI_los = pd.DataFrame(df_WI_los, columns=['Base-Twin', '1R-Twin', '3R-Twin'])
df_WI_nlos = pd.DataFrame(df_WI_nlos, columns=['Base-Twin', '1R-Twin', '3R-Twin'])

# Save DataFrames to CSV files
df_sionna_los.to_csv('accuracies/df_sionna_los.csv', index=False)
df_sionna_nlos.to_csv('accuracies/df_sionna_nlos.csv', index=False)
df_WI_los.to_csv('accuracies/df_WI_los.csv', index=False)
df_WI_nlos.to_csv('accuracies/df_WI_nlos.csv', index=False)
plot(df_sionna_los, df_WI_los, 'LOS')
plot(df_sionna_nlos, df_WI_nlos, 'NLOS')

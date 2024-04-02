import pandas as pd
import numpy as np
from sklearn.metrics import ndcg_score
import os

synthetic_files = [
                # 'Twin-1_LOS.csv',
                # 'Twin-1_NLOS.csv', 
                'Twin-2_LOS.csv',
                'Twin-2_NLOS.csv',
                'Twin-3_LOS.csv',
                'Twin-3_NLOS.csv',
                ]

# Metrics
# base_sionna_path = 'test_rf/sionna/Twin-1_LOS.csv'
base_sionna_path = '../test_rf/sionna/'
base_wi_path = '../test_rf/WI/'
# base_sionna_path = ''
base_real_path = '../test_rf/real/'
restricted = False


for file in synthetic_files:
    df_synthetic = pd.read_csv(base_wi_path + file)
    if '_LOS' in file:
        df_real_path = base_real_path + f'LOS/episode_{0}_snr.csv'
        length = 201
    else:
        df_real_path = base_real_path + f'NLOS/episode_{0}_snr.csv'
        length = 161
    df_real = pd.read_csv(df_real_path)
    mag_total = 0
    cos_sim_tot = 0
    ci_tot = 0
    ndcg_tot = 0
    ndcg_top10_tot = 0
    ci_ndcg_count = 0

    for i in range(1, length):
        column_to_sort_by = f'Power-{i} (dBm)'
        df_synthetic = df_synthetic.sort_values(by=column_to_sort_by)
        df_real = df_real.sort_values(by=column_to_sort_by)
        sionna_antenna = df_synthetic[f'Antennas-{i}'].to_list()
        real_antenna = df_real[f'Antennas-{i}'].to_list()
        sionna_power = df_synthetic[column_to_sort_by].to_numpy() + 119
        real_power = df_real[column_to_sort_by].to_numpy()
        sionna_antenna = np.array(\
                            [antenna.replace("Legacy_", "") for antenna in sionna_antenna])\
                            .astype(int)
        real_antenna = np.array(\
                        [antenna.replace("Legacy_", "") for antenna in real_antenna])\
                        .astype(int)
        # print(df_real)
        if (restricted):
            zero_indices = np.where(real_power == 0)[0]
            zero_real_ant = real_antenna[zero_indices]
            index = 0
            while index < len(sionna_antenna):
                if sionna_antenna[index] in zero_real_ant:
                    sionna_antenna = np.delete(sionna_antenna, index)
                    sionna_power = np.delete(sionna_power, index)
                else:
                    index += 1
            
            real_antenna = np.delete(real_antenna, zero_indices)
            real_power = np.delete(real_power, zero_indices)
        l2_norm_sionna = np.linalg.norm(sionna_power)
        l2_norm_wi = np.linalg.norm(real_power)
        dot_prod = np.dot(real_power, sionna_power)
        cos_sim_tot += dot_prod / (l2_norm_wi * l2_norm_sionna)
        mag_total += np.linalg.norm(real_power - sionna_power) / 34

        concordant_pairs = 0
        discordant_pairs = 0

        for j in range(len(real_antenna)):
                for k in range(j + 1, len(real_antenna)):
                    # Check if the pair is concordant or discordant
                    if (real_antenna[j] < real_antenna[k] and sionna_antenna[j] < sionna_antenna[k]) or \
                    (real_antenna[j] > real_antenna[k] and sionna_antenna[j] > sionna_antenna[k]):
                        concordant_pairs += 1
                    else:
                        discordant_pairs += 1
        if len(sionna_antenna) > 1:

            ci_tot += concordant_pairs / (concordant_pairs + discordant_pairs)

            # Relevance scores in Ideal order
            true_relevance = np.asarray([real_antenna])
            
            # Relevance scores in output order
            relevance_score = np.asarray([sionna_antenna])
            
            ndcg_tot += ndcg_score(true_relevance, relevance_score)
            ndcg_top10_tot += ndcg_score(true_relevance, relevance_score, k=10)
            ci_ndcg_count += 1
    mag_ave = mag_total / 200
    cos_sim_ave = cos_sim_tot / 200
    ci_ave = ci_tot / ci_ndcg_count
    ndcg_ave = ndcg_tot / ci_ndcg_count
    ndcg_top10_ave = ndcg_top10_tot / ci_ndcg_count
    print(df_real_path)
    print(f"{file} Magnitude difference: {mag_ave}")
    print(f"{file} Cosine Similarity: {cos_sim_ave}")
    print(f"{file} Concordance index: ", ci_ave)
    print(f"{file} nDCG score: ", ndcg_ave)
    print(f"{file} nDCG score (accounting for only top 10): ", ndcg_top10_ave)
    print()



# For twins 2 and 3, get average of scores for entire 200 point experiment
# For every geo loc, find the closest
# sol 1, regen synth to find 1 to 1 mapping for real world
# sol 2, produce 1 to 1 correspondance between real and synth
# sol 2' if x - x' < delta, keep. If not, throw out
# sol 3, interpolate beam powers
# generate sionna data by friday: put in paper by next tuesday
# average scores out and/or histograms, quantile bar plots, fidelity of an episode from t = 0 to t = end, t meaning 
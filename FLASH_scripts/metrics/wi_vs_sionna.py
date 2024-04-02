import pandas as pd
import numpy as np
from sklearn.metrics import ndcg_score
import os

folder_names = ['Twin-1_LOS.csv',
                'Twin-1_NLOS.csv', 
                'Twin-2_LOS.csv',
                'Twin-2_NLOS.csv',
                'Twin-3_LOS.csv',
                'Twin-3_NLOS.csv']

# folder_names = ['power_real.csv']
# Metrics
# base_sionna_path = 'test_rf/sionna/Twin-1_LOS.csv'
base_sionna_path = '../test_rf/sionna/'
base_wi_path = '../test_rf/WI/'
# base_sionna_path = ''
# base_wi_path = ''


for file in folder_names:
    df_sionna = pd.read_csv(base_sionna_path + file)
    df_wi = pd.read_csv(base_wi_path + file)
    # print(df_sionna)
    if 'Twin-1' in file:
        column_to_sort_by = 'Max Propogated Power(dBm)'
        df_sionna = df_sionna.sort_values(by=column_to_sort_by)
        df_wi = df_wi.sort_values(by=column_to_sort_by)
        sionna_power = df_sionna[column_to_sort_by].to_numpy() + 119
        print(sionna_power)
        wi_power = df_wi[column_to_sort_by].to_numpy() + 174
        print(wi_power)
        sionna_antenna = df_sionna['Antenna'].to_list()
        wi_antenna = df_wi['Antenna'].to_list()
        sionna_antenna = np.array(\
                            [antenna.replace("Legacy_", "") for antenna in sionna_antenna])\
                            .astype(int)
        wi_antenna = np.array(\
                        [antenna.replace("Legacy_", "") for antenna in wi_antenna])\
                        .astype(int)
        l2_norm_sionna = np.linalg.norm(sionna_power)
        l2_norm_wi = np.linalg.norm(wi_power)
        dot_prod = np.dot(wi_power, sionna_power)
        cos_sim = dot_prod / (l2_norm_wi * l2_norm_sionna)
        l2_norm_mag_diff = np.linalg.norm(wi_power - sionna_power) / 34
        print(f"{file} Magnitude difference: {l2_norm_mag_diff}")
        print(f"{file} Cosine Similarity: {cos_sim}")

        concordant_pairs = 0
        discordant_pairs = 0

        for i in range(len(wi_antenna)):
                for j in range(i + 1, len(wi_antenna)):
                    # Check if the pair is concordant or discordant
                    if (wi_antenna[i] < wi_antenna[j] and sionna_antenna[i] < sionna_antenna[j]) or \
                    (wi_antenna[i] > wi_antenna[j] and sionna_antenna[i] > sionna_antenna[j]):
                        concordant_pairs += 1
                    else:
                        discordant_pairs += 1

        ci = concordant_pairs / (concordant_pairs + discordant_pairs)
        print(f"{file} concordance index: ", ci)

        # Relevance scores in Ideal order
        true_relevance = np.asarray([wi_antenna])
        
        # Relevance scores in output order
        relevance_score = np.asarray([sionna_antenna])
        
        # or we can use the scikit-learn ndcg_score package
        print(f"{file} nDCG score: ", ndcg_score(
            true_relevance, relevance_score))
        print()
    else:
        mag_total = 0
        cos_sim_tot = 0
        ci_tot = 0
        ndcg_tot = 0
        ndcg_top10_tot = 0
        for i in range (1, 201):
            column_to_sort_by = f'Power-{i} (dBm)'
            df_sionna = df_sionna.sort_values(by=column_to_sort_by)
            df_wi = df_wi.sort_values(by=column_to_sort_by)
            sionna_power = df_sionna[column_to_sort_by].to_numpy() + 119
            wi_power = df_wi[column_to_sort_by].to_numpy() + 174
            sionna_antenna = df_sionna[f'Antennas-{i}'].to_list()
            wi_antenna = df_wi[f'Antennas-{i}'].to_list()
            sionna_antenna = np.array(\
                                [antenna.replace("Legacy_", "") for antenna in sionna_antenna])\
                                .astype(int)
            wi_antenna = np.array(\
                            [antenna.replace("Legacy_", "") for antenna in wi_antenna])\
                            .astype(int)
            l2_norm_sionna = np.linalg.norm(sionna_power)
            l2_norm_wi = np.linalg.norm(wi_power)
            dot_prod = np.dot(wi_power, sionna_power)
            cos_sim_tot += dot_prod / (l2_norm_wi * l2_norm_sionna)
            mag_total += np.linalg.norm(wi_power - sionna_power) / 34

            concordant_pairs = 0
            discordant_pairs = 0

            for i in range(len(wi_antenna)):
                    for j in range(i + 1, len(wi_antenna)):
                        # Check if the pair is concordant or discordant
                        if (wi_antenna[i] < wi_antenna[j] and sionna_antenna[i] < sionna_antenna[j]) or \
                        (wi_antenna[i] > wi_antenna[j] and sionna_antenna[i] > sionna_antenna[j]):
                            concordant_pairs += 1
                        else:
                            discordant_pairs += 1

            ci_tot += concordant_pairs / (concordant_pairs + discordant_pairs)

            # Relevance scores in Ideal order
            true_relevance = np.asarray([wi_antenna])
            
            # Relevance scores in output order
            relevance_score = np.asarray([sionna_antenna])
            
            ndcg_tot += ndcg_score(true_relevance, relevance_score)
            ndcg_top10_tot += ndcg_score(true_relevance, relevance_score, k=10)
        mag_ave = mag_total / 200
        cos_sim_ave = cos_sim_tot / 200
        ci_ave = ci_tot / 200
        ndcg_ave = ndcg_tot / 200
        ndcg_top10_ave = ndcg_top10_tot / 200
    
        print(f"{file} Magnitude difference: {mag_ave}")
        print(f"{file} Cosine Similarity: {cos_sim_ave}")
        print(f"{file} Concordance index: ", ci_ave)
        print(f"{file} nDCG score: ", ndcg_ave)
        print(f"{file} nDCG score (accounting for only top 10): ", ndcg_top10_ave)
        print()



# For twins 2 and 3, get average of scores for entire 200 point experiment

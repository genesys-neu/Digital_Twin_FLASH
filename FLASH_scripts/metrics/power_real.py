import pandas as pd
import math

for ep in range(0, 10):
    # csv_file_path = f'../../flash/flash/Cat1/opposite/Extract/Cat1_10mph_lr_opposite/episode_{ep}/Synchornized_data_with_SNR.csv'
    csv_file_path = f'../../flash/flash/Cat3/static_in_front/Extract/Cat3_15mph_lr_opposite/episode_{ep}/Synchornized_data_with_SNR.csv'
    df = pd.read_csv(csv_file_path)

    df['snr'] = df['snr'].apply(eval)
    df['all_sector'] = df['all_sector'].apply(eval)

    df_total = pd.DataFrame()

    for index, row in df.iterrows():
        max_snr = {sector: 0 for sector in range(1, 32)}
        max_snr.update({sector: 0 for sector in range(61, 64)})
        for sector, snr in zip(row['all_sector'], row['snr']):
            if sector in max_snr and (max_snr[sector] == 0 or snr + 30 > max_snr[sector]):
                max_snr[sector] = snr + 30
        formatted_max_snr = {f"Legacy_{sector:02}": snr for sector, snr in max_snr.items()}
        max_snr_list = [(key, value) for key, value in formatted_max_snr.items()]
        df_max_snr = pd.DataFrame(max_snr_list, columns=[f'Antennas-{index+1}', f'Power-{index+1} (dBm)'])
        df_total = pd.concat([df_total, df_max_snr], axis=1)
    # print(df_total)


    # df_total.to_csv(f'../test_rf/real/LOS/episode_{ep}_snr.csv')
    df_total.to_csv(f'../test_rf/real/NLOS/episode_{ep}_snr.csv')


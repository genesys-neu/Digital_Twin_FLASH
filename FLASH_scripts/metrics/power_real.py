import pandas as pd

for ep in range(0, 10):
    csv_file_path = f'../../flash/flash/Cat1/opposite/Extract/Cat1_10mph_lr_opposite/episode_{ep}/Synchornized_data_with_SNR.csv'
    # csv_file_path = f'../../flash/flash/Cat3/static_in_front/Extract/Cat3_15mph_lr_opposite/episode_{ep}/Synchornized_data_with_SNR.csv'
    df = pd.read_csv(csv_file_path)

    df['all_rssi'] = df['all_rssi'].apply(eval)
    df['all_sector'] = df['all_sector'].apply(eval)

    df_total = pd.DataFrame()

    for index, row in df.iterrows():
        max_rssi = {sector: 0 for sector in range(1, 32)}
        max_rssi.update({sector: 0 for sector in range(61, 64)})
        for sector, rssi in zip(row['all_sector'], row['all_rssi']):
            if sector in max_rssi and (max_rssi[sector] == -1 or rssi > max_rssi[sector]):
                max_rssi[sector] = rssi
        formatted_max_rssi = {f"Legacy_{sector:02}": rssi for sector, rssi in max_rssi.items()}
        max_rssi_list = [(key, value) for key, value in formatted_max_rssi.items()]
        df_max_rssi = pd.DataFrame(max_rssi_list, columns=[f'Antennas-{index+1}', f'Power-{index+1} (dBm)'])
        df_total = pd.concat([df_total, df_max_rssi], axis=1)
    # print(df_total)


    df_total.to_csv(f'../test_rf/real/LOS/episode_{ep}.csv')
    # df_total.to_csv(f'../test_rf/real/NLOS/episode_{ep}.csv')


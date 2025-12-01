import pandas as pd
import glob

dosya_yolu = "BirlesikVeri/*.csv"
dosyalar = glob.glob(dosya_yolu)

dataframes = []

for dosya in dosyalar:
    df = pd.read_csv(dosya)


    dataframes.append(df)
birlesmis_df = pd.concat(dataframes, axis=0, ignore_index=True, sort=False)

birlesmis_df.to_csv("birlesmis_dosya.csv", index=False)

print(f"İşlem tamamlandı. Toplam satır sayısı: {len(birlesmis_df)}")
print("Sütunlar:", birlesmis_df.columns.tolist())
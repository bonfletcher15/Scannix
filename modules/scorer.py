import pandas as pd

def rate_network(signal, encryption):
    rating = "Low"
    if encryption.lower() in ["wpa3", "wpa2"]:
        if signal > -50:
            rating = "Safe"
        elif signal > -70:
            rating = "Medium"
        else:
            rating = "Low"
    else:
        rating = "Danger"
    return rating

def score_networks(csv_path):
    df = pd.read_csv(csv_path)
    df['Rating'] = df.apply(lambda row: rate_network(row['SignalStrength'], row['Encryption']), axis=1)
    return df

if __name__ == "__main__":
    scored_df = score_networks("../data/oui_sample.csv")
    print(scored_df)
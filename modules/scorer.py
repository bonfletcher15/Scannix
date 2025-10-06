import os
import pandas as pd

def enc_score(enc):
    enc = str(enc).lower()
    if "wpa3" in enc: return 3
    if "wpa2" in enc: return 2
    if "wep" in enc: return 1
    return 0

def signal_score(rssi):
    try:
        rssi = int(rssi)
    except Exception:
        return 0
    if rssi > -50: return 2
    if rssi > -65: return 1
    return 0

def openness_score(enc):
    return 0 if "open" in str(enc).lower() else 1

def vendor_score(vendor):
    trusted = {"Cisco", "Aruba", "Ubiquiti", "Apple", "Netgear", "D-Link"}
    return 1 if str(vendor) in trusted else 0

def channel_congestion_score(df, channel):
    try:
        channel = int(channel)
    except Exception:
        return 0
    same = df[df["Channel"] == channel].shape[0]
    overlap = df[df["Channel"].isin([channel-1, channel+1])].shape[0]
    raw = same + 0.5 * overlap
    if raw <= 1:
        return 0
    if raw <= 3:
        return 1
    return 2

def overall_score_and_rating(row, df):
    enc = str(row.get("Encryption", "")).lower()
    if "open" in enc or "wep" in enc:
        return {"Score": 0, "Congestion": channel_congestion_score(df, row.get("Channel")), "Rating": "Danger"}

    congestion = channel_congestion_score(df, row.get("Channel"))

    score = (3 * enc_score(row.get("Encryption"))
             + 1 * signal_score(row.get("SignalStrength"))
             + 2 * openness_score(row.get("Encryption"))
             + 1 * vendor_score(row.get("Vendor"))
             - 1 * congestion)

    if score >= 6:
        rating = "Safe"
    elif 3 <= score <= 5:
        rating = "Suspicious"
    else:
        rating = "Danger"

    return {"Score": int(score), "Congestion": int(congestion), "Rating": rating}

def score_networks(input_data):
    if isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
    else:
        path = str(input_data)
        if not os.path.isabs(path):
            possible = os.path.join(os.path.dirname(__file__), "..", path)
            if os.path.exists(possible):
                path = possible
        df = pd.read_csv(path)

    required = ["SSID","BSSID","SignalStrength","Encryption","Channel","Vendor"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    results = df.apply(lambda row: overall_score_and_rating(row, df), axis=1)
    res_df = pd.DataFrame(results.tolist(), index=df.index)
    out = pd.concat([df.reset_index(drop=True), res_df.reset_index(drop=True)], axis=1)
    return out

if __name__ == "__main__":
    default_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/oui_sample.csv"))
    if not os.path.exists(default_csv):
        default_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/scan_sim.csv"))
    scored = score_networks(default_csv)
    print(scored.to_string(index=False))
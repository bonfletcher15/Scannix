import os
import sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/wirisk.db"))

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS networks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            SSID TEXT,
            BSSID TEXT,
            SignalStrength INTEGER,
            Encryption TEXT,
            Channel INTEGER,
            Vendor TEXT,
            HiddenSSID INTEGER,
            BeaconInterval INTEGER,
            ChannelWidth INTEGER,
            Standard TEXT,
            EncryptionDetails TEXT,
            LastSeen TEXT,
            Score INTEGER,
            Congestion INTEGER,
            Rating TEXT,
            ScanTime TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_networks(df):
    init_db()
    if "ScanTime" not in df.columns:
        df["ScanTime"] = datetime.utcnow().isoformat()
    cols = ["SSID","BSSID","SignalStrength","Encryption","Channel","Vendor",
            "HiddenSSID","BeaconInterval","ChannelWidth","Standard","EncryptionDetails","LastSeen",
            "Score","Congestion","Rating","ScanTime"]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    to_write = df[cols].copy()
    if to_write["HiddenSSID"].dtype == bool:
        to_write["HiddenSSID"] = to_write["HiddenSSID"].astype(int)
    conn = sqlite3.connect(DB_PATH)
    to_write.to_sql("networks", conn, if_exists="append", index=False)
    conn.close()
    print(f"[db] Saved {len(to_write)} row(s) to {DB_PATH}")

if __name__ == "__main__":
    init_db()
    print(f"Initialized DB at {DB_PATH}")
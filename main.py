"""
    python main.py            #simulated scan
    python main.py --real     #real scan 
"""
import argparse
import os
from modules import scanner, scorer, db
import pandas as pd

def run(real=False, n=8):
    print("[main] starting scan (real=%s)..." % real)
    df = scanner.get_scan_dataframe(real=real, n=n, csv_out=True)
    print(f"[main] obtained {len(df)} networks from scanner.")
    scored = scorer.score_networks(df)
    print("[main] scoring done. Sample output:")
    print(scored[["SSID","BSSID","SignalStrength","Encryption","Vendor","Score","Congestion","Rating"]].to_string(index=False))
    db.save_networks(scored)
    print("[main] pipeline complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Use real scanner (not implemented)")
    parser.add_argument("-n", type=int, default=8, help="How many networks to simulate (if not real)")
    args = parser.parse_args()
    run(real=args.real, n=args.n)
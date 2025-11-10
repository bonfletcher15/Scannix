import time
import pandas as pd
from pywifi import PyWiFi, const
import scorer
import os
import requests
import traceback
_vendor_cache = {}

def is_SSID_Hidden(ssid):
    if not ssid or ssid.strip() == "":
        return "Hidden SSID"
    return ssid

def get_encryption(network):
    if not getattr(network, "akm", None):
        return "Open"
    try:
        if hasattr(const, "AKM_TYPE_WPA3PSK") and const.AKM_TYPE_WPA3PSK in network.akm:
            return "WPA3"
        elif const.AKM_TYPE_WPA2PSK in network.akm:
            return "WPA2"
        elif const.AKM_TYPE_WPAPSK in network.akm:
            return "WPA"
        else:
            return "Other"
    except Exception:
        return "Other"

def get_freq(network):
    try:
        f = int(network.freq)
        if f > 100000:
            f //= 1000
    except Exception:
        return None, None, None

    if 2412 <= f <= 2472:
        channel = (f - 2407) // 5
    elif f == 2484:
        channel = 14
    elif 5000 <= f <= 6000:
        channel = (f - 5000) // 5
    else:
        channel = None

    if f < 3000:
        band = "2.4GHz"
    elif f < 6000:
        band = "5GHz"
    else:
        band = "6GHz"

    return f, band, channel

def lookup_vendor(bssid):
    if not bssid or ":" not in bssid:
        return "Unknown"

    prefix = ":".join(bssid.split(":")[:3]).upper()
    if prefix in _vendor_cache:
        return _vendor_cache[prefix]

    try:
        url = f"https://api.macvendors.com/{prefix}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            vendor = response.text.strip()
        else:
            vendor = "Unknown"
    except Exception:
        vendor = "Unknown"

    _vendor_cache[prefix] = vendor
    return vendor

def scan_networks():
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(3)
    results = iface.scan_results()

    networks = []
    for network in results:

        ssid = is_SSID_Hidden(network.ssid)
        bssid = network.bssid
        signal = network.signal
        encryption = get_encryption(network)  
        mhz, band, channel = get_freq(network)
        vendor = lookup_vendor(bssid)

        networks.append({
            "SSID": ssid,
            "BSSID": bssid,
            "SignalStrength": signal,
            "Encryption": encryption,
            "Frequency": mhz,
            "Band": band,
            "Channel": channel,
            "Vendor": vendor,        
        })
    return pd.DataFrame(networks)

def run_scan():
    try:
        df = scan_networks()
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/field_scan.csv"))
        df.to_csv(output_path, index=False)
        print(df.to_string(index=False))

    except Exception as e:
        print("Scan failed:", e)
        traceback.print_exc()

    # Scorer
    # df = scorer.score_networks(df)
    # output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/field_scan.csv"))
    # df.to_csv(output_path, index=False)
    # print(df.to_string(index=False))

if __name__ == "__main__":
    run_scan()
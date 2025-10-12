import time
import pandas as pd
from pywifi import PyWiFi, const
import scorer
import os
import csv
import requests
from functools import lru_cache

_vendor_cache = {}
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

def normalize_freq_to_mhz(freq):
    try:
        f = int(freq)
    except Exception:
        return None
    if f > 100000:
        f = f // 1000
    return f

def freq_to_channel_mhz(mhz):
    try:
        f = int(mhz)
    except Exception:
        return None
    if 2412 <= f <= 2472:
        return (f - 2407) // 5
    if f == 2484:
        return 14
    if 5000 <= f <= 6000:
        return (f - 5000) // 5
    return None

def band_from_mhz(mhz):
    try:
        f = int(mhz)
    except Exception:
        return None
    if f < 3000:
        return "2.4GHz"
    if f < 6000:
        return "5GHz"
    return "6GHz"

def cipher_name_from_const(cipher_val):
    try:
        mapping = {}
        for attr in dir(const):
            if attr.startswith("CIPHER_"):
                mapping[getattr(const, attr)] = attr.replace("CIPHER_", "")
        if cipher_val in mapping:
            return mapping[cipher_val]
    except Exception:
        pass

    if cipher_val is None:
        return None
    try:
        v = int(cipher_val)
        if v == 0:
            return "NONE"
        if v == 1:
            return "WEP"
        if v == 2:
            return "TKIP"
        if v == 3:
            return "CCMP"
    except Exception:
        pass
    return str(cipher_val)

def scan_networks():
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(3)
    results = iface.scan_results()

    networks = []
    for network in results:
        ssid = network.ssid
        bssid = network.bssid
        signal = network.signal
        raw_freq = getattr(network, "freq", None)
        mhz = normalize_freq_to_mhz(raw_freq)
        channel = freq_to_channel_mhz(mhz) if mhz else None
        band = band_from_mhz(mhz) if mhz else None
        raw_cipher = getattr(network, "cipher", None)
        cipher = cipher_name_from_const(raw_cipher)
        encryption = "Open"
        if getattr(network, "akm", None):
            try:
                if hasattr(const, "AKM_TYPE_WPA3PSK") and const.AKM_TYPE_WPA3PSK in network.akm:
                    encryption = "WPA3"
                elif const.AKM_TYPE_WPA2PSK in network.akm:
                    encryption = "WPA2"
                elif const.AKM_TYPE_WPAPSK in network.akm:
                    encryption = "WPA"
                else:
                    encryption = "Other"
            except Exception:
                encryption = "Other"

        vendor = lookup_vendor(bssid)

        networks.append({
            "SSID": ssid,
            "BSSID": bssid,
            "SignalStrength": signal,
            "Encryption": encryption,
            "Cipher": cipher,
            "Frequency": mhz,
            "Band": band,
            "Channel": channel,
            "Vendor": vendor
        })

    return pd.DataFrame(networks)

def run_scan():
    df = scan_networks()
    df = scorer.score_networks(df)
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/field_scan.csv"))
    df.to_csv(output_path, index=False)
    print(df.to_string(index=False))

if __name__ == "__main__":
    run_scan()
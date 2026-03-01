import requests
import json

try:
    r = requests.get("http://localhost:5000/api/history/BTC/USDT?tf=1h")
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print("Keys found in response:", list(data.keys()))
        for key in ['candles', 'rsi_div', 'stoch_rsi', 'st_trend', 'signals']:
            if key in data:
                print(f"Count for {key}: {len(data[key])}")
                if len(data[key]) > 0:
                    print(f"Sample {key}[0]:", data[key][0])
            else:
                print(f"MISSING KEY: {key}")
    else:
        print(f"Error: API returned {r.status_code}")
except Exception as e:
    print(f"Connection Error: {e}")

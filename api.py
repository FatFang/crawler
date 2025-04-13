import requests
import pandas as pd
import os

# 政府開放平台 即時&歷史地震資訊
API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
API_KEY = "rdec-key-123-45678-011121314"

OUTPUT_DIR = "./"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_data():
    params = {
        "Authorization": API_KEY
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()

# 根據資料結構去擷取及整理需要的特定資料及欄位
def parse_earthquake_data(data):
    earthquakes = data['records']['Earthquake']
    eq_list = []
    station_list = []

    for eq in earthquakes:
        eq_info = eq.get('EarthquakeInfo', {})
        intensity = eq.get('Intensity', {})
        shaking_area = intensity.get('ShakingArea', [])

        eq_base = {
            'EarthquakeNo': eq.get('EarthquakeNo'),
            'ReportType': eq.get('ReportType'),
            'ReportColor': eq.get('ReportColor'),
            'ReportContent': eq.get('ReportContent'),
            'OriginTime': eq_info.get('OriginTime'),
            'FocalDepth': eq_info.get('FocalDepth'),
            'EpicenterLatitude': eq_info.get('Epicenter', {}).get('EpicenterLatitude'),
            'EpicenterLongitude': eq_info.get('Epicenter', {}).get('EpicenterLongitude'),
            'EpicenterLocation': eq_info.get('Epicenter', {}).get('Location'),
            'MagnitudeType': eq_info.get('EarthquakeMagnitude', {}).get('MagnitudeType'),
            'MagnitudeValue': eq_info.get('EarthquakeMagnitude', {}).get('MagnitudeValue'),
            'Web': eq.get('Web')
        }
        eq_list.append(eq_base)

        for area in shaking_area:
            for station in area.get('EqStation', []):
                station_data = {
                    'EarthquakeNo': eq.get('EarthquakeNo'),
                    'AreaDesc': area.get('AreaDesc'),
                    'CountyName': area.get('CountyName'),
                    'StationName': station.get('StationName'),
                    'StationID': station.get('StationID'),
                    'SeismicIntensity': station.get('SeismicIntensity'),
                    'EpicenterDistance': station.get('EpicenterDistance'),
                    'EWComponent_pga': station.get('pga', {}).get('EWComponent'),
                    'NSComponent_pga': station.get('pga', {}).get('NSComponent'),
                    'VComponent_pga': station.get('pga', {}).get('VComponent'),
                    'EWComponent_pgv': station.get('pgv', {}).get('EWComponent'),
                    'NSComponent_pgv': station.get('pgv', {}).get('NSComponent'),
                    'VComponent_pgv': station.get('pgv', {}).get('VComponent'),
                    'WaveImageURI': station.get('WaveImageURI'),
                }
                station_list.append(station_data)

    return pd.DataFrame(eq_list), pd.DataFrame(station_list)

def export_to_csv(df, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    print(f"輸出完成：{path}")

def main():
    data = fetch_data()
    eq_df, station_df = parse_earthquake_data(data)
    export_to_csv(eq_df, f'api1.csv')
    export_to_csv(station_df, f'api2.csv')

if __name__ == "__main__":
    print("--start--")
    main()
    print("--end--")


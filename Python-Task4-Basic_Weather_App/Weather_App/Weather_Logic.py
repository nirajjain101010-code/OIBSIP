
# weather_logic.py
import requests

class WeatherLogic:
    def __init__(self, api_key):
        self.API_KEY = api_key

    def get_geocoding(self, query):
        try:
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={self.API_KEY}"
            res = requests.get(geo_url, timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    def fetch_weather_data(self, lat, lon, units="metric"):
        try:
            curr_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={self.API_KEY}"
            curr_res = requests.get(curr_url, timeout=5)
            curr_data = curr_res.json() if curr_res.status_code == 200 else None

            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units={units}&appid={self.API_KEY}"
            forecast_res = requests.get(forecast_url, timeout=5)
            forecast_data = forecast_res.json() if forecast_res.status_code == 200 else None

            pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.API_KEY}"
            pollution_res = requests.get(pollution_url, timeout=5)
            pollution_data = pollution_res.json() if pollution_res.status_code == 200 else None

            return {
                "current": curr_data,
                "forecast": forecast_data,
                "pollution": pollution_data
            }
        except Exception:
            return None

    def calculate_aqi(self, pollution_data):
        try:
            comp = pollution_data.get("list", [{}])[0].get("components", {})
            pm25 = comp.get("pm2_5", 0.0)
            
            if pm25 <= 12.0:
                aqi_val = int((pm25 / 12.0) * 50)
            elif pm25 <= 35.4:
                aqi_val = int(50 + ((pm25 - 12.1) / (35.4 - 12.1)) * 50)
            elif pm25 <= 55.4:
                aqi_val = int(100 + ((pm25 - 35.5) / (55.4 - 35.5)) * 100)
            elif pm25 <= 150.4:
                aqi_val = int(200 + ((pm25 - 55.5) / (150.4 - 55.5)) * 100)
            elif pm25 <= 250.4:
                aqi_val = int(300 + ((pm25 - 150.5) / (250.4 - 150.5)) * 100)
            else:
                aqi_val = int(min(5000, 400 + ((pm25 - 250.5) / 250.0) * 4600))

            if aqi_val <= 50:
                aqi_text, aqi_color = "Good 🟢", "#22c55e"
            elif aqi_val <= 100:
                aqi_text, aqi_color = "Satisfactory 🟢", "#84cc16"
            elif aqi_val <= 200:
                aqi_text, aqi_color = "Moderate 🟡", "#f59e0b"
            elif aqi_val <= 400:
                aqi_text, aqi_color = "Poor 🟠", "#f97316"
            elif aqi_val <= 1000:
                aqi_text, aqi_color = "Very Poor 🔴", "#ef4444"
            else:
                aqi_text, aqi_color = "Severe / Hazardous ☣️", "#7f1d1d"

            return aqi_val, aqi_text, aqi_color
        except Exception:
            return None, "Unavailable", "#9ca3af"

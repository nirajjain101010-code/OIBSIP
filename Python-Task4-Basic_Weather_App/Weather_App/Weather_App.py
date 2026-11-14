from io import BytesIO
import sys
import threading
import tkinter as tk
import requests
from datetime import datetime

try:
    import customtkinter as ctk
    from PIL import Image, ImageEnhance
except ImportError as e:
    print(f"Missing dependency: {e}. Run: pip install customtkinter requests pillow")
    sys.exit(1)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

API_KEY = "fa8d6e84c1a96c9aec04c2287d996558"


class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nexus Weather // 2050")
        self.geometry("420x820")
        self.resizable(True, True)
        self.minsize(380, 700)

        self.unit_celsius = True
        self.show_aqi = False  # Optional AQI toggle state
        self.current_raw_data = None
        self.hourly_expanded = False
        self.daily_expanded = False
        self.icon_cache = {}
        self.bg_cache = {}

        self._build_ui()

        # Non-blocking background auto-locate on startup
        threading.Thread(target=self.auto_detect_location, daemon=True).start()

    def _build_ui(self):
        # 1. Full-window background wallpaper label covering the entire app window
        self.bg_lbl = ctk.CTkLabel(self, text="")
        self.bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)

        # 2. Main content container placed over background
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Search Bar Card (Black background panel)
        search_card = ctk.CTkFrame(
            self.main_frame, fg_color="#111827", corner_radius=10,
            border_width=1, border_color="#374151"
        )
        search_card.pack(fill="x", pady=(0, 10))

        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.pack(fill="x", padx=10, pady=8)
        search_inner.columnconfigure(0, weight=1)

        self.city_entry = ctk.CTkEntry(
            search_inner, placeholder_text="Enter city name (Auto-correct active)...",
            font=("Consolas", 12), height=32, fg_color="#1f2937",
            text_color="#ffffff", border_width=0
        )
        self.city_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.city_entry.bind("<Return>", lambda e: self.start_fetch_thread())

        search_btn = ctk.CTkButton(
            search_inner, text="GET", font=("Consolas", 12, "bold"),
            width=55, height=32, command=self.start_fetch_thread
        )
        search_btn.grid(row=0, column=1)

        # Control Bar
        control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        control_frame.pack(fill="x", pady=(0, 8))

        self.unit_btn = ctk.CTkButton(
            control_frame, text="UNIT: °C", font=("Consolas", 10, "bold"),
            width=75, height=28, fg_color="#111827", hover_color="#1f2937",
            border_width=1, border_color="#374151", command=self.toggle_units
        )
        self.unit_btn.pack(side="left")

        # Optional AQI Toggle Button
        self.aqi_toggle_btn = ctk.CTkButton(
            control_frame, text="📊 AQI: OFF", font=("Consolas", 10, "bold"),
            width=95, height=28, fg_color="#111827", hover_color="#1f2937",
            border_width=1, border_color="#374151", command=self.toggle_aqi_view
        )
        self.aqi_toggle_btn.pack(side="left", padx=5)

        auto_btn = ctk.CTkButton(
            control_frame, text="📍 AUTO", font=("Consolas", 10, "bold"),
            width=80, height=28, fg_color="#111827", hover_color="#1f2937",
            border_width=1, border_color="#374151",
            command=lambda: threading.Thread(target=self.auto_detect_location, daemon=True).start()
        )
        auto_btn.pack(side="right")

        # Current Weather Card (Black background panel)
        self.current_card = ctk.CTkFrame(
            self.main_frame, fg_color="#111827", corner_radius=12,
            border_width=1, border_color="#374151"
        )
        self.current_card.pack(fill="x", pady=(0, 8))

        self.location_lbl = ctk.CTkLabel(
            self.current_card, text="--", font=("Consolas", 18, "bold"),
            text_color="#38bdf8", fg_color="transparent"
        )
        self.location_lbl.pack(pady=(10, 0))

        self.icon_lbl = ctk.CTkLabel(self.current_card, text="", fg_color="transparent")
        self.icon_lbl.pack(pady=0)

        self.temp_lbl = ctk.CTkLabel(
            self.current_card, text="--°", font=("Consolas", 40, "bold"),
            text_color="#ffffff", fg_color="transparent"
        )
        self.temp_lbl.pack(pady=(0, 0))

        self.desc_lbl = ctk.CTkLabel(
            self.current_card, text="Enter a location to scan", font=("Consolas", 12),
            text_color="#9ca3af", fg_color="transparent"
        )
        self.desc_lbl.pack(pady=(0, 10))

        # --- Optional AQI Telemetry Panel (Created under main_frame) ---
        self.aqi_frame = ctk.CTkFrame(self.main_frame, fg_color="#111827", corner_radius=10, border_width=1,
                                      border_color="#374151")

        self.aqi_lbl = ctk.CTkLabel(
            self.aqi_frame, text="Air Quality Index (0-5000 Scale): --", font=("Consolas", 10, "bold"),
            text_color="#9ca3af", fg_color="transparent"
        )
        self.aqi_lbl.pack(pady=8, padx=10)
        # Initially hidden safely
        self.aqi_frame.pack_forget()

        # --- HOURLY SECTION ---
        hourly_header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        hourly_header_frame.pack(fill="x", pady=(2, 2))

        ctk.CTkLabel(
            hourly_header_frame, text="HOURLY FORECAST",
            font=("Consolas", 10, "bold"), text_color="#93c5fd"
        ).pack(side="left")

        self.hourly_toggle_btn = ctk.CTkButton(
            hourly_header_frame, text="View More ▾", font=("Consolas", 9, "bold"),
            width=75, height=20, fg_color="#1f2937", hover_color="#374151",
            text_color="#38bdf8", command=self.toggle_hourly_expand
        )
        self.hourly_toggle_btn.pack(side="right")

        self.hourly_frame = ctk.CTkFrame(
            self.main_frame, fg_color="#111827", corner_radius=10,
            border_width=1, border_color="#374151"
        )
        self.hourly_frame.pack(fill="x", pady=(0, 8))

        # --- DAILY SECTION ---
        daily_header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        daily_header_frame.pack(fill="x", pady=(2, 2))

        ctk.CTkLabel(
            daily_header_frame, text="MULTI-DAY OUTLOOK",
            font=("Consolas", 10, "bold"), text_color="#93c5fd"
        ).pack(side="left")

        self.daily_toggle_btn = ctk.CTkButton(
            daily_header_frame, text="View More ▾", font=("Consolas", 9, "bold"),
            width=75, height=20, fg_color="#1f2937", hover_color="#374151",
            text_color="#38bdf8", command=self.toggle_daily_expand
        )
        self.daily_toggle_btn.pack(side="right")

        self.daily_frame = ctk.CTkFrame(
            self.main_frame, fg_color="#111827", corner_radius=10,
            border_width=1, border_color="#374151"
        )
        self.daily_frame.pack(fill="x", pady=(0, 5))

        # Status Bar
        self.status_lbl = ctk.CTkLabel(
            self.main_frame, text="Ready", font=("Consolas", 9), text_color="#d1d5db"
        )
        self.status_lbl.pack(anchor="w", pady=(2, 0))

        self.load_background("clear")

    def toggle_aqi_view(self):
        self.show_aqi = not self.show_aqi
        if self.show_aqi:
            self.aqi_toggle_btn.configure(text="📊 AQI: ON", fg_color="#1f2937")
            # Pack aqi_frame right below current_card safely
            self.aqi_frame.pack(fill="x", pady=(0, 8), after=self.current_card)
        else:
            self.aqi_toggle_btn.configure(text="📊 AQI: OFF", fg_color="#111827")
            self.aqi_frame.pack_forget()

        if self.current_raw_data:
            self.update_display()

    def toggle_hourly_expand(self):
        self.hourly_expanded = not self.hourly_expanded
        self.hourly_toggle_btn.configure(text="View Less ▴" if self.hourly_expanded else "View More ▾")
        self.update_display()

    def toggle_daily_expand(self):
        self.daily_expanded = not self.daily_expanded
        self.daily_toggle_btn.configure(text="View Less ▴" if self.daily_expanded else "View More ▾")
        self.update_display()

    def load_background(self, condition):
        bg_urls = {
            "clear": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
            "clouds": "https://images.unsplash.com/photo-1534088568595-a066fa4108a0?auto=format&fit=crop&w=800&q=80",
            "rain": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?auto=format&fit=crop&w=800&q=80",
            "snow": "https://images.unsplash.com/photo-1491002052546-bf38f186af56?auto=format&fit=crop&w=800&q=80",
            "thunderstorm": "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?auto=format&fit=crop&w=800&q=80"
        }

        url = bg_urls.get(condition, bg_urls["clear"])
        if url in self.bg_cache:
            self.bg_lbl.configure(image=self.bg_cache[url])
            self.bg_lbl.image = self.bg_cache[url]
            return

        def fetch_bg():
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    pil_img = Image.open(BytesIO(res.content))

                    enhancer = ImageEnhance.Brightness(pil_img)
                    pil_img = enhancer.enhance(0.40)

                    w = max(self.winfo_width(), 420)
                    h = max(self.winfo_height(), 820)
                    ctk_bg_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w, h))
                    self.bg_cache[url] = ctk_bg_img
                    self.after(0, lambda: (
                        self.bg_lbl.configure(image=ctk_bg_img),
                        setattr(self.bg_lbl, 'image', ctk_bg_img)
                    ))
            except Exception:
                pass

        threading.Thread(target=fetch_bg, daemon=True).start()

    def auto_detect_location(self):
        try:
            self.update_status("Detecting location via IP...", "#f59e0b")
            res = requests.get("https://ipinfo.io/json", timeout=3)
            data = res.json()
            city = data.get("city")
            if city:
                self.city_entry.delete(0, "end")
                self.city_entry.insert(0, city)
                self.start_fetch_thread()
            else:
                self.update_status("IP geolocation failed. Enter city manually.", "#ef4444")
        except Exception:
            self.update_status("Offline mode / Auto-locate skipped.", "#737373")

    def start_fetch_thread(self):
        threading.Thread(target=self.fetch_weather, daemon=True).start()

    def fetch_weather(self):
        query = self.city_entry.get().strip()
        if not query:
            self.update_status("ERROR: Enter a valid city name.", "#ef4444")
            return

        units = "metric" if self.unit_celsius else "imperial"
        try:
            self.update_status("Resolving location & telemetry...", "#38bdf8")

            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}"
            geo_res = requests.get(geo_url, timeout=5)
            geo_data = geo_res.json()

            if not geo_data:
                self.update_status(f"ERROR: City '{query}' not found. Check spelling.", "#ef4444")
                return

            matched_city = geo_data[0].get("name")
            country = geo_data[0].get("country", "")
            lat = geo_data[0].get("lat")
            lon = geo_data[0].get("lon")
            corrected_name = f"{matched_city}, {country}"

            self.after(0, lambda: (
                self.city_entry.delete(0, "end"),
                self.city_entry.insert(0, matched_city)
            ))

            curr_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={API_KEY}"
            curr_res = requests.get(curr_url, timeout=5)
            curr_data = curr_res.json()

            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units={units}&appid={API_KEY}"
            forecast_res = requests.get(forecast_url, timeout=5)
            forecast_data = forecast_res.json()

            pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
            pollution_res = requests.get(pollution_url, timeout=5)
            pollution_data = pollution_res.json()

            if curr_res.status_code != 200:
                self.update_status("ERROR: Failed to fetch weather data.", "#ef4444")
                return

            self.current_raw_data = {
                "current": curr_data,
                "forecast": forecast_data,
                "pollution": pollution_data
            }

            weather_main = curr_data.get("weather", [{}])[0].get("main", "Clear").lower()
            if "rain" in weather_main or "drizzle" in weather_main:
                self.load_background("rain")
            elif "snow" in weather_main:
                self.load_background("snow")
            elif "thunder" in weather_main:
                self.load_background("thunderstorm")
            elif "cloud" in weather_main:
                self.load_background("clouds")
            else:
                self.load_background("clear")

            self.after(0, self.update_display)
            self.update_status(f"Telemetry loaded for {corrected_name}", "#22c55e")

        except requests.exceptions.RequestException:
            self.update_status("ERROR: Network connection failed.", "#ef4444")

    def update_status(self, text, color):
        self.after(0, lambda: self.status_lbl.configure(text=text, text_color=color))

    def update_display(self, event=None):
        if not self.current_raw_data:
            return

        curr = self.current_raw_data["current"]
        forecast = self.current_raw_data["forecast"]
        pollution = self.current_raw_data["pollution"]

        city_name = f"{curr.get('name')}, {curr.get('sys', {}).get('country')}"
        temp = round(curr.get("main", {}).get("temp", 0))
        desc = curr.get("weather", [{}])[0].get("description", "").title()
        icon_code = curr.get("weather", [{}])[0].get("icon", "01d")

        unit_symbol = "°C" if self.unit_celsius else "°F"
        self.location_lbl.configure(text=city_name)
        self.temp_lbl.configure(text=f"{temp}{unit_symbol}")
        self.desc_lbl.configure(text=desc)

        self.load_icon(icon_code, self.icon_lbl, size=(56, 56))

        # --- Parse AQI on 0-5000 Scale (if enabled) ---
        if self.show_aqi:
            try:
                comp = pollution.get("list", [{}])[0].get("components", {})
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

                self.aqi_lbl.configure(text=f"AQI (0-5000 Scale): {aqi_val} - {aqi_text}", text_color=aqi_color)
            except Exception:
                self.aqi_lbl.configure(text="AQI (0-5000 Scale): Unavailable", text_color="#9ca3af")

        # --- HOURLY FORECAST UPDATE ---
        for w in self.hourly_frame.winfo_children():
            w.destroy()

        limit_hourly = 12 if self.hourly_expanded else 6
        list_items = forecast.get("list", [])[:limit_hourly]
        cols_count = len(list_items)

        for i in range(cols_count):
            self.hourly_frame.columnconfigure(i, weight=1)
        self.hourly_frame.rowconfigure(0, weight=1)

        for i, item in enumerate(list_items):
            time_str = item.get("dt_txt", "").split(" ")[1][:5]
            item_temp = round(item.get("main", {}).get("temp", 0))
            item_icon = item.get("weather", [{}])[0].get("icon", "01d")

            f_card = ctk.CTkFrame(self.hourly_frame, fg_color="transparent")
            f_card.grid(row=0, column=i, sticky="nsew", padx=1, pady=4)

            ctk.CTkLabel(f_card, text=time_str, font=("Consolas", 8), text_color="#d1d5db",
                         fg_color="transparent").pack(pady=(2, 0))
            icon_lbl_sub = ctk.CTkLabel(f_card, text="", fg_color="transparent")
            icon_lbl_sub.pack(pady=0)
            self.load_icon(item_icon, icon_lbl_sub, size=(20, 20))
            ctk.CTkLabel(f_card, text=f"{item_temp}°", font=("Consolas", 9, "bold"), text_color="#ffffff",
                         fg_color="transparent").pack(pady=(0, 2))

        # --- DAILY FORECAST UPDATE ---
        for w in self.daily_frame.winfo_children():
            w.destroy()

        daily_items = []
        seen_dates = set()
        for item in forecast.get("list", []):
            date_str = item.get("dt_txt", "").split(" ")[0]
            if date_str not in seen_dates and "12:00:00" in item.get("dt_txt", ""):
                seen_dates.add(date_str)
                daily_items.append(item)

        limit_daily = 7 if self.daily_expanded else 5
        daily_items = daily_items[:limit_daily]

        for i, item in enumerate(daily_items):
            dt_txt = item.get("dt_txt", "")
            day_name = datetime.strptime(dt_txt.split(" ")[0], "%Y-%m-%d").strftime("%a, %b %d")

            day_temp = round(item.get("main", {}).get("temp", 0))
            day_desc = item.get("weather", [{}])[0].get("description", "").title()
            day_icon = item.get("weather", [{}])[0].get("icon", "01d")

            d_row = ctk.CTkFrame(self.daily_frame, fg_color="transparent")
            d_row.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(d_row, text=day_name, font=("Consolas", 10, "bold"), text_color="#38bdf8", width=95,
                         anchor="w", fg_color="transparent").pack(side="left")

            icon_lbl_daily = ctk.CTkLabel(d_row, text="", fg_color="transparent")
            icon_lbl_daily.pack(side="left", padx=4)
            self.load_icon(day_icon, icon_lbl_daily, size=(20, 20))

            ctk.CTkLabel(d_row, text=day_desc, font=("Consolas", 10), text_color="#ffffff", anchor="w",
                         fg_color="transparent").pack(side="left", fill="x", expand=True, padx=4)
            ctk.CTkLabel(d_row, text=f"{day_temp}{unit_symbol}", font=("Consolas", 10, "bold"), text_color="#ffffff",
                         fg_color="transparent").pack(side="right")

    def load_icon(self, icon_code, label_widget, size=(50, 50)):
        cache_key = (icon_code, size)
        if cache_key in self.icon_cache:
            label_widget.configure(image=self.icon_cache[cache_key])
            label_widget.image = self.icon_cache[cache_key]
            return

        def fetch_and_set():
            try:
                url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    pil_img = Image.open(BytesIO(response.content))
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
                    self.icon_cache[cache_key] = ctk_img
                    self.after(0,
                               lambda: (label_widget.configure(image=ctk_img), setattr(label_widget, 'image', ctk_img)))
            except Exception:
                pass

        threading.Thread(target=fetch_and_set, daemon=True).start()

    def toggle_units(self):
        self.unit_celsius = not self.unit_celsius
        self.unit_btn.configure(text="UNIT: °C" if self.unit_celsius else "UNIT: °F")
        if self.city_entry.get().strip():
            self.start_fetch_thread()


if __name__ == "__main__":
    try:
        app = WeatherApp()
        app.mainloop()
    except Exception as e:
        print(f"Startup crash: {e}")
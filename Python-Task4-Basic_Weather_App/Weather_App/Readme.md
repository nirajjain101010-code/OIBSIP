# 🌤️ NEXUS WEATHER // 2050

**A sleek, futuristic desktop Weather & Air Quality Telemetry Suite built with Python, CustomTkinter, and the OpenWeatherMap API.**

# 🌟 ADVANCED TIER FEATURE CHECKLIST

> Fully satisfies all Beginner and Advanced requirements with robust modular architecture.

| Feature | Status | Description | 
| ----- | ----- | ----- | 
| 🖥️ **GUI Window & Results Panel** | ✅ | Modern dark-mode interface (`#111827`) with separate standalone bordered cards for search, controls, current weather, and forecasts. | 
| 🖼️ **Dynamic Weather Icons** | ✅ | Asynchronously fetches and caches official OpenWeatherMap icon sprites via Pillow (`PIL`). | 
| ⏱️ **Hourly Forecast Panel** | ✅ | Displays weather for the next 6 hours in a grid layout (expandable up to 12 intervals via **View More**). | 
| 📅 **Daily Forecast Panel** | ✅ | Shows a 5-day multi-day weather outlook (expandable up to 7 days). | 
| 🌡️ **Unit Toggle (°C / °F)** | ✅ | Instant switching between Metric and Imperial unit systems. | 
| 📍 **IP-Based Auto-Location** | ✅ | Automatically detects location on startup using `ipinfo.io` API via background threading. | 
| 🛡️ **GUI-Based Error Handling** | ✅ | All network errors, invalid inputs, and status alerts are pushed directly to the in-app status bar with color indicators. | 

# ✨ EXTRA ENHANCEMENTS

* **Modular Architecture**: Cleanly separated into `weather_app.py` (GUI & presentation) and `weather_logic.py` (API requests & data calculations).

* **Dynamic Wallpapers**: Background wallpapers automatically adapt based on live weather conditions (Rain, Snow, Thunderstorm, Clouds, Clear) with brightness enhancement.

* **Optional Extended AQI**: Toggleable **📊 AQI** panel mapping real-time $\text{PM}_{2.5}$ pollutant levels onto an extended **0–5000 scale** with health color coding.

* **Smart Typos & Region Selection**: Supports spelling corrections and state/region lookups (e.g., searching *Nagaland* provides a district selection dropdown).

# 📁 PROJECT STRUCTURE

```
nexus-weather-2050/
│
├── .gitignore          # Files and directories ignored by Git
├── weather_app.py      # Main application GUI & Event Controllers
├── weather_logic.py    # Core API fetching, Geocoding & AQI calculation engine
├── requirements.txt    # External dependency package list
└── README.md           # Project documentation

```

## 🛠️ REQUIREMENTS & INSTALLATION

This application requires Python 3.8 or higher along with a few external libraries for graphical rendering and networking.

### 1️⃣ Install Dependencies

```
pip install -r requirements.txt

```

*(Or install manually: `pip install customtkinter requests pillow`)*

### 2️⃣ Run the Application

Launch the modular workstation by running `weather_app.py`:

```
python weather_app.py

```

## 💡 HOW TO USE

1. **Auto-Location**: On startup, the application queries your IP via `ipinfo.io` to load local weather automatically.

2. **Search Location**: Type any city, state (e.g., `Maharashtra`), or type (e.g., `delhi`) into the search card and press **Enter** or click **GET**.

3. **Toggle Units**: Click **UNIT: °C / °F** to switch temperature units instantly.

4. **Monitor Air Quality**: Click **📊 AQI: OFF / ON** to reveal the real-time 0–5000 scale Air Quality Index box.

5. **Expand Forecasts**: Click **View More ▾** on the Hourly or Multi-Day header bars to view extended periods.

# 👤 AUTHOR

### **DEVELOPED BY @ NIRAJ JAIN**
# Import required libraries
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime, timezone, timedelta
import os
import math
from io import BytesIO
import config  # Import the config file

class WeatherApp:
    def __init__(self):
        """Initialize the Weather App and set up the main window"""
        # Create the main window
        self.root = tk.Tk()
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        self.root.configure(bg=config.COLORS["bg_dark"])
        
        # Lock window size to prevent resizing
        self.root.resizable(False, False)
        
        # Create and set the application icon
        app_icon = self.create_app_icon()
        icon_photo = ImageTk.PhotoImage(app_icon)
        self.root.iconphoto(True, icon_photo)
        self.icon_photo = icon_photo  # Keep a reference to prevent garbage collection
        
        # Dictionary to store weather icons
        self.weather_icons = {}
        
        # Set up custom styles for widgets
        self.setup_styles()
        
        # Create all GUI elements
        self.create_widgets()
        
        # Get API key from config file
        self.api_key = config.API_KEY

    def setup_styles(self):
        """Configure custom styles for ttk widgets"""
        # Create style object for ttk widgets
        style = ttk.Style()
        
        # Configure search button style
        style.configure("Search.TButton",
                       padding=10,          # Button padding
                       font=("Arial", 12))  # Button font
        
        # Configure search entry style
        style.configure("Search.TEntry",
                       padding=10,          # Entry field padding
                       font=("Arial", 12))  # Entry field font

    def create_widgets(self):
        """Create and arrange all GUI elements"""
        # Create header frame
        self.header_frame = tk.Frame(self.root, bg="#3B4252", height=50)
        self.header_frame.pack(fill="x", pady=(0, 10))
        
        # Create search frame inside header
        search_frame = tk.Frame(self.header_frame, bg="#3B4252")
        search_frame.pack(expand=True)
        
        # Create "Enter a city" label
        search_label = tk.Label(search_frame,
                              text="Enter a city:",
                              font=("Arial", 12),
                              bg="#3B4252",
                              fg="#D8DEE9",
                              padx=8)
        search_label.pack(side="left")
        
        # Create city entry field
        self.city_entry = ttk.Entry(search_frame, 
                                  font=("Arial", 12),
                                  width=25,
                                  style="Search.TEntry")
        self.city_entry.pack(side="left", padx=15)
        
        # Bind Enter key to update weather
        self.city_entry.bind("<Return>", lambda e: self.update_weather())
        
        # Create search button
        search_button = ttk.Button(search_frame,
                                 text="Search",
                                 command=self.update_weather,
                                 style="Search.TButton")
        search_button.pack(side="left", padx=8)

        # Create main content frame
        self.main_frame = tk.Frame(self.root, bg="#2E3440")
        self.main_frame.pack(fill="both", expand=True, pady=(0, 10), padx=40)
        
        # Create location and time frame
        self.location_frame = tk.Frame(self.main_frame, bg="#2E3440")
        self.location_frame.pack(fill="x", pady=(0, 5))
        
        # Create location label
        self.location_label = tk.Label(self.location_frame,
                                     text="",
                                     font=("Arial", 24, "bold"),
                                     bg="#2E3440",
                                     fg="#ECEFF4")
        self.location_label.pack(side="left")

        # Create time label
        self.time_label = tk.Label(self.location_frame,
                                 text="",
                                 font=("Arial", 12),
                                 bg="#2E3440",
                                 fg="#D8DEE9")
        self.time_label.pack(side="right", pady=4)
        
        # Create weather info frame
        self.weather_frame = tk.Frame(self.main_frame, bg="#2E3440")
        self.weather_frame.pack(fill="x", pady=(0, 10))
        
        # Create weather icon label
        self.weather_icon_label = tk.Label(self.weather_frame, bg="#2E3440")
        self.weather_icon_label.pack(pady=5)
        
        # Create temperature label
        self.temp_label = tk.Label(self.weather_frame,
                                 text="--°C",
                                 font=("Arial", 68, "bold"),
                                 bg="#2E3440",
                                 fg="#88C0D0")
        self.temp_label.pack(pady=(0, 3))
        
        # Create weather status label
        self.status_label = tk.Label(self.weather_frame,
                                   text="Weather Status",
                                   font=("Arial", 16),
                                   bg="#2E3440",
                                   fg="#D8DEE9")
        self.status_label.pack(pady=8)
        
        # Create additional weather details frame
        self.details_frame = tk.Frame(self.main_frame, bg="#2E3440")
        self.details_frame.pack(fill="x", pady=10)
        
        # Create three columns for details
        for i in range(3):
            self.details_frame.columnconfigure(i, weight=1)
        
        # Create humidity label
        self.humidity_label = self.create_detail_label("Humidity: --", 0)
        
        # Create wind label
        self.wind_label = self.create_detail_label("Wind: -- m/s", 1)
        
        # Create pressure label
        self.pressure_label = self.create_detail_label("Pressure: -- hPa", 2)
        
        # Create air quality index frame
        self.aqi_frame = tk.Frame(self.main_frame, bg="#2E3440")
        self.aqi_frame.pack(fill="x", pady=5)
        
        # Create air quality index label
        self.aqi_label = tk.Label(self.aqi_frame,
                                text="Air Quality: --",
                                font=("Arial", 14, "bold"),
                                bg="#2E3440",
                                fg="#ECEFF4",
                                padx=15,
                                pady=8)
        self.aqi_label.pack()
        
        # Create forecast frame
        forecast_container = tk.Frame(self.root, bg="#2E3440", height=160)
        forecast_container.pack(fill="x", padx=30, pady=(0, 10))
        
        # Create forecast title label
        forecast_title = tk.Label(forecast_container,
                                text="5-Day Forecast",
                                font=("Arial", 18, "bold"),
                                bg="#2E3440",
                                fg="#ECEFF4")
        forecast_title.pack(pady=(0, 8))
        
        # Create forecast frame
        self.forecast_frame = tk.Frame(forecast_container, bg="#2E3440")
        self.forecast_frame.pack(fill="x")
        
        # Configure grid for forecast cards
        for i in range(5):
            self.forecast_frame.columnconfigure(i, weight=1)
        
        # Create footer frame
        self.footer_frame = tk.Frame(self.root, bg="#3B4252", height=30)
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)
        
        # Create footer label
        footer_label = tk.Label(self.footer_frame,
                              text="Powered by OpenWeatherMap",
                              font=("Arial", 9),
                              bg="#3B4252",
                              fg="#D8DEE9")
        footer_label.pack(expand=True)

    def create_detail_label(self, text, column):
        """Create a label for additional weather details"""
        # Create frame for detail label
        frame = tk.Frame(self.details_frame, bg="#3B4252", padx=15, pady=8)
        frame.grid(row=0, column=column, sticky="ew", padx=4)
        
        # Create detail label
        label = tk.Label(frame,
                        text=text,
                        font=("Arial", 12),
                        bg="#3B4252",
                        fg="#D8DEE9")
        label.pack(expand=True)
        return label

    def create_forecast_card(self, date, temp, description, icon_code, column):
        """Create a forecast card"""
        # Create a transparent frame with alpha=0.8
        card = tk.Frame(self.forecast_frame, bg="#3B4252", padx=5, pady=5)
        card.grid(row=0, column=column, sticky="nsew", padx=15)
        
        # Make the card semi-transparent
        card.bind('<Configure>', lambda e: self._make_transparent(card, 0.0))
        
        # Add hover animation
        self.setup_card_animation(card)
        
        # Create date label
        date_label = tk.Label(card,
                            text=date,
                            font=("Arial", 12, "bold"),
                            bg="#3B4252",
                            fg="#ECEFF4")
        date_label.pack()
        
        # Create weather icon
        icon = self.get_weather_icon(icon_code, size=45)
        if icon:
            icon_label = tk.Label(card, image=icon, bg="#3B4252")
            icon_label.image = icon
            icon_label.pack(pady=2)
        
        # Create temperature label
        temp_label = tk.Label(card,
                            text=f"{temp}°C",
                            font=("Arial", 14, "bold"),
                            bg="#3B4252",
                            fg="#88C0D0")
        temp_label.pack()
        
        # Create description label
        desc_label = tk.Label(card,
                            text=description,
                            font=("Arial", 10),
                            bg="#3B4252",
                            fg="#D8DEE9",
                            wraplength=100)
        desc_label.pack()

    def setup_card_animation(self, card):
        """Setup bounce animation for forecast cards"""
        # Dictionary to track animation states for each card
        self.animation_running = {}
        
        def start_bounce(event):
            """Start the bounce animation when mouse enters"""
            if card not in self.animation_running or not self.animation_running[card]:
                self.animation_running[card] = True
                bounce_up(event)
        
        def stop_bounce(event):
            """Stop the bounce animation when mouse leaves"""
            self.animation_running[card] = False
            bounce_down(event)
        
        def bounce_up(event, current_y=0, step=0):
            """Animate the card moving upward"""
            # Stop if animation is no longer active
            if not self.animation_running.get(card, False):
                return
            
            # Calculate smooth bounce using sine wave
            target_y = -10  # Maximum bounce height
            duration = 10   # Number of steps for animation
            
            if step < duration:
                # Calculate new position using sine wave for smooth motion
                progress = step / duration
                new_y = target_y * (math.sin(progress * math.pi / 2))
                
                # Update card position
                current_pos = card.grid_info()
                card.grid(row=current_pos['row'], column=current_pos['column'], 
                         sticky="nsew", padx=15, pady=(new_y, 5))
                
                # Schedule next animation frame
                card.after(20, lambda: bounce_up(event, new_y, step + 1))
        
        def bounce_down(event):
            """Reset card to original position"""
            current_pos = card.grid_info()
            card.grid(row=current_pos['row'], column=current_pos['column'], 
                     sticky="nsew", padx=15, pady=5)
        
        # Bind mouse events to animation functions
        card.bind('<Enter>', start_bounce)
        card.bind('<Leave>', stop_bounce)

    def _make_transparent(self, widget, alpha):
        """Make a widget semi-transparent"""
        # Create a transparent image for the background
        image = Image.new('RGBA', (30, 30), color=(59, 66, 82, int(255 * alpha)))
        bg_image = ImageTk.PhotoImage(image)
        
        # Set the transparent background
        widget.bg_image = bg_image  # Keep a reference to prevent garbage collection
        widget.configure(bg='#3B4252')
        
        # Make all child widgets transparent too
        for child in widget.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg='#3B4252')

    def get_weather_icon(self, icon_code, size=150):
        """Download and create weather icon"""
        # Create a unique key for caching
        cache_key = f"{icon_code}_{size}"
        
        # Check if icon is already cached
        if cache_key not in self.weather_icons:
            try:
                # Download icon from OpenWeatherMap
                url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                response = requests.get(url)
                image = Image.open(BytesIO(response.content))
                
                # Resize icon to specified size
                image = image.resize((size, size), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage and cache it
                self.weather_icons[cache_key] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading weather icon: {e}")
                return None
        
        # Return cached icon
        return self.weather_icons[cache_key]

    def get_weather_data(self, city):
        """Fetch weather data from OpenWeatherMap API"""
        try:
            # Fetch current weather data
            params = {
                "q": city,
                "appid": config.API_KEY,
                "units": "metric"
            }
            
            # Get current weather
            response = requests.get(config.WEATHER_BASE_URL, params=params)
            current_data = response.json()
            
            if response.status_code != 200:
                return None, None, None
            
            # Get coordinates for air quality data
            lat = current_data['coord']['lat']
            lon = current_data['coord']['lon']
            
            # Get air quality data
            aqi_params = {
                "lat": lat,
                "lon": lon,
                "appid": config.API_KEY
            }
            aqi_response = requests.get(config.AQI_BASE_URL, params=aqi_params)
            aqi_data = aqi_response.json()
            
            # Get forecast data
            forecast_response = requests.get(config.FORECAST_BASE_URL, params=params)
            forecast_data = forecast_response.json()
            
            return current_data, aqi_data, forecast_data
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch weather data: {str(e)}")
            return None, None, None

    def get_aqi_color(self, aqi):
        """Get color and description based on Air Quality Index"""
        # Define color codes and descriptions for different AQI levels
        aqi_colors = {
            1: ("#4CAF50", "Good"),      # Green
            2: ("#FDD835", "Fair"),      # Yellow
            3: ("#FF9800", "Moderate"),  # Orange
            4: ("#F44336", "Poor"),      # Red
            5: ("#9C27B0", "Very Poor")  # Purple
        }
        return aqi_colors.get(aqi, ("#808080", "Unknown"))  # Gray as default

    def update_weather(self):
        """Update the GUI with new weather data"""
        # Get city name from entry field
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Warning", "Please enter a city name")
            return
        
        # Fetch weather data
        current_data, aqi_data, forecast_data = self.get_weather_data(city)
        
        if current_data and current_data.get('cod') == 200:
            # Update location and time
            timezone_offset = current_data['timezone']
            local_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(seconds=timezone_offset)))
            self.location_label.config(text=f"{city.title()}")
            self.time_label.config(text=local_time.strftime("%I:%M %p"))
            
            # Update current weather
            temp = round(current_data['main']['temp'])
            self.temp_label.config(text=f"{temp}°C")
            
            weather_desc = current_data['weather'][0]['description']
            self.status_label.config(text=weather_desc.title())
            
            # Update weather icon
            icon_code = current_data['weather'][0]['icon']
            icon = self.get_weather_icon(icon_code, size=150)
            if icon:
                self.weather_icon_label.configure(image=icon)
                self.weather_icon_label.image = icon
            
            # Update additional weather details
            humidity = current_data['main']['humidity']
            self.humidity_label.config(text=f"Humidity: {humidity}%")
            
            wind_speed = current_data['wind']['speed']
            self.wind_label.config(text=f"Wind: {wind_speed} m/s")
            
            pressure = current_data['main']['pressure']
            self.pressure_label.config(text=f"Pressure: {pressure} hPa")
            
            # Update air quality
            if aqi_data and aqi_data.get('cod') != "404":
                aqi = aqi_data['list'][0]['main']['aqi']
                color, desc = self.get_aqi_color(aqi)
                self.aqi_label.config(text=f"Air Quality: {desc}", fg=color)
            
            # Update 5-day forecast
            if forecast_data and forecast_data.get('cod') == "200":
                # Process forecast data for next 5 days
                processed_dates = set()
                daily_forecasts = []
                
                for item in forecast_data['list']:
                    forecast_date = datetime.fromtimestamp(item['dt'])
                    date_str = forecast_date.strftime("%A")
                    
                    if date_str not in processed_dates and forecast_date.date() > datetime.now().date():
                        processed_dates.add(date_str)
                        temp = round(item['main']['temp'])
                        desc = item['weather'][0]['description']
                        icon_code = item['weather'][0]['icon']
                        daily_forecasts.append((date_str, temp, desc, icon_code))
                        
                        if len(daily_forecasts) == 5:
                            break
                
                # Create forecast cards
                for i, (date, temp, desc, icon_code) in enumerate(daily_forecasts):
                    self.create_forecast_card(date, temp, desc, icon_code, i)
        else:
            self.status_label.config(text="City not found!")

    def run(self):
        """Start the application main loop"""
        self.root.mainloop()

    def create_app_icon(self):
        """Create a 3D cloud icon with multiple shades of grey"""
        # Create a 32x32 image with transparency
        icon_size = 32
        icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Define colors for 3D effect (from darkest to lightest)
        shadow_color = "#3B4252"    # Darkest - for shadow
        base_color = "#4C566A"      # Base color
        mid_color = "#D8DEE9"       # Mid tone
        highlight = "#ECEFF4"       # Lightest - for highlights
        
        # Draw the cloud shape with 3D effect
        # Shadow layer (slightly offset)
        draw.ellipse([9, 17, 25, 29], fill=shadow_color)  # Bottom shadow
        draw.ellipse([7, 13, 19, 25], fill=shadow_color)  # Middle-left shadow
        draw.ellipse([13, 9, 27, 23], fill=shadow_color)  # Middle-right shadow
        draw.ellipse([17, 11, 29, 23], fill=shadow_color)  # Top shadow
        
        # Base layer
        draw.ellipse([8, 16, 24, 28], fill=base_color)    # Bottom cloud
        draw.ellipse([6, 12, 18, 24], fill=base_color)    # Middle-left cloud
        draw.ellipse([12, 8, 26, 22], fill=base_color)    # Middle-right cloud
        draw.ellipse([16, 10, 28, 22], fill=base_color)   # Top cloud
        
        # Mid-tone highlights (smaller circles on top-left of each cloud part)
        draw.ellipse([9, 14, 16, 21], fill=mid_color)     # Middle-left highlight
        draw.ellipse([14, 10, 22, 18], fill=mid_color)    # Middle-right highlight
        draw.ellipse([18, 12, 25, 19], fill=mid_color)    # Top highlight
        
        # Bright highlights (small dots for 3D effect)
        draw.ellipse([10, 15, 13, 18], fill=highlight)    # Small highlight 1
        draw.ellipse([15, 11, 18, 14], fill=highlight)    # Small highlight 2
        draw.ellipse([19, 13, 22, 16], fill=highlight)    # Small highlight 3
        
        return icon

if __name__ == "__main__":
    app = WeatherApp()
    app.run()

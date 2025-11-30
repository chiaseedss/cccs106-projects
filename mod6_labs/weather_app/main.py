"""Weather Application using Flet v0.28.3"""

import flet as ft
import json
import httpx
import asyncio
from pathlib import Path
from weather_service import WeatherService
from config import Config


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history_file = Path("search_history.json")
        self.search_history = self.load_history()
        self.current_unit = "metric"
        self.current_weather_data = None
        self.setup_page()
        self.build_ui()
    
    def load_history(self):
        """Load search history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Save search history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.search_history, f)
    
    def add_to_history(self, city: str):
        """Add city to history."""
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:10]
            self.save_history()
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()
    
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=45,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
            text_align=ft.TextAlign.CENTER,
        )
        
        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )
        
        # Unit toggle button
        self.unit_button = ft.IconButton(
            icon=ft.Icons.THERMOSTAT,
            tooltip="Toggle °C/°F",
            on_click=self.toggle_units,
        )
        
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLACK,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=False,
            on_submit=self.on_search,
            on_focus=self.show_history_suggestions,
            on_blur=self.hide_history_suggestions,
            fill_color=ft.Colors.GREY_300,
            filled=True,
        )
        
        # History suggestions list 
        self.history_suggestions = ft.Column(
            visible=False,
            spacing=0,
        )
        
        # Container for input and suggestions
        self.input_container = ft.Container(
            content=ft.Column(
                [
                    self.city_input,
                    self.history_suggestions,
                ],
                spacing=0,
            ),
            width=300,
        )

        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
                shape=ft.RoundedRectangleBorder(radius=5),
            ),
            height=48,
            width=180,
        )
        
        # Location button
        self.location_button = ft.ElevatedButton(
            "My Location",
            icon=ft.Icons.MY_LOCATION,
            on_click=lambda e: self.page.run_task(self.get_current_location_weather),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
                shape=ft.RoundedRectangleBorder(radius=5),
            ),
            height=48,
            width=180,
        )
        
        # Weather display container
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        # Forecast container
        self.forecast_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Add all components to page
        self.page.add(
            ft.Container(
                content=ft.Column(
                [
                    ft.Row(
                        [
                            self.title,
                            ft.Row(
                                [
                                    self.unit_button,
                                    self.theme_button,
                                ],
                                spacing=5,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        [
                            self.input_container,
                            self.search_button,
                            self.location_button,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        spacing=10,
                        wrap=True,
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                    self.forecast_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            )
        )
    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)
    
    def load_from_history(self, e):
        """Load weather from history."""
        city = e.control.value
        if city:
            self.city_input.value = city
            self.page.run_task(self.get_weather)
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        if not city:
            self.show_error("Please enter a city name")
            return
        
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)
            self.current_weather_data = weather_data
            
            # Fetch forecast data
            forecast_data = await self.weather_service.get_forecast(city)
            
            # Display weather and forecast
            await self.display_weather(weather_data)
            self.display_forecast(forecast_data)
            
            # Add to history
            self.add_to_history(city)
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def get_current_location_weather(self):
        """Get weather for current location using IP."""
        self.loading.visible = True
        self.page.update()
        
        try:
            async with httpx.AsyncClient() as client:
                # Get location from IP
                response = await client.get("https://ipapi.co/json/")
                data = response.json()
                city = data.get('city', '')
                
                if city:
                    self.city_input.value = city
                    await self.get_weather()
                else:
                    self.show_error("Could not detect your location")
        except Exception as e:
            self.show_error("Could not detect your location")
        finally:
            self.loading.visible = False
            self.page.update()
    
    def show_history_suggestions(self, e):
        """Show search history when input is focused."""
        if len(self.search_history) > 0:
            # Build suggestion items
            suggestion_items = []
            # Add history items
            for city in self.search_history[:5]:  # Show last 5
                # Create a simple container that definitely captures clicks
                item = ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.HISTORY, size=16, color=ft.Colors.GREY_600),
                            ft.Text(city, size=14),
                        ],
                        spacing=10,
                    ),
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY_300)),
                    on_click=lambda e, c=city: self.handle_history_click(c),
                    ink=True,
                )
                suggestion_items.append(item)
            
            self.history_suggestions.controls = suggestion_items
            self.history_suggestions.visible = True
            self.page.update()

    def handle_history_click(self, city: str):
        """Handle click on history item."""
        print(f"HISTORY CLICKED: {city}")
        self.city_input.value = city
        self.history_suggestions.visible = False
        self.page.update()
        self.page.run_task(self.get_weather)

    def hide_history_suggestions(self, e): 
        """Hide suggestions when input loses focus.""" 
        async def delayed_hide():
            await asyncio.sleep(0.3)
            self.history_suggestions.visible = False
            self.page.update()
        
        self.page.run_task(delayed_hide)

    def select_history_item(self, city: str):
        """Select a city from history suggestions."""
        self.city_input.value = city
        self.history_suggestions.visible = False
        self.page.update()
        self.page.run_task(self.get_weather)

    def get_weather_color(self, weather_id: int) -> str:
        """Get background color based on weather condition."""
        # Weather condition codes: https://openweathermap.org/weather-conditions
        if 200 <= weather_id < 300:  # Thunderstorm
            return ft.Colors.PURPLE_100
        elif 300 <= weather_id < 600:  # Drizzle/Rain
            return ft.Colors.BLUE_100
        elif 600 <= weather_id < 700:  # Snow
            return ft.Colors.LIGHT_BLUE_50
        elif 700 <= weather_id < 800:  # Atmosphere (fog, mist, etc.)
            return ft.Colors.GREY_200
        elif weather_id == 800:  # Clear
            return ft.Colors.AMBER_100
        elif weather_id > 800:  # Clouds
            return ft.Colors.GREY_100
        return ft.Colors.BLUE_50
    
    async def display_weather(self, data: dict):
        """Display weather information."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        weather_id = data.get("weather", [{}])[0].get("id", 800)
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Get color based on weather
        bg_color = self.get_weather_color(weather_id)
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            description,
                            size=20,
                            italic=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text(
                    f"{temp:.1f}°{'C' if self.current_unit == 'metric' else 'F'}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),
                ft.Text(
                    f"Feels like {feels_like:.1f}°{'C' if self.current_unit == 'metric' else 'F'}",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),
                ft.Divider(),
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%"
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s"
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Update container color
        self.weather_container.bgcolor = bg_color
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()
        
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()
        
        # Show weather alerts
        self.show_weather_alerts(temp)
    
    def display_forecast(self, data: dict):
        """Display 5-day forecast."""
        forecast_list = data.get("list", [])
        
        # Group by day (take one forecast per day at noon)
        daily_forecasts = []
        seen_dates = set()
        
        for item in forecast_list:
            date = item.get("dt_txt", "").split()[0]
            time = item.get("dt_txt", "").split()[1] if len(item.get("dt_txt", "").split()) > 1 else ""
            
            # Take forecast around noon (12:00:00)
            if date not in seen_dates and "12:00:00" in time:
                daily_forecasts.append(item)
                seen_dates.add(date)
            
            if len(daily_forecasts) >= 5:
                break
        
        # Build forecast cards
        forecast_cards = []
        for forecast in daily_forecasts:
            date = forecast.get("dt_txt", "").split()[0]
            temp = forecast.get("main", {}).get("temp", 0)
            temp_min = forecast.get("main", {}).get("temp_min", 0)
            temp_max = forecast.get("main", {}).get("temp_max", 0)
            description = forecast.get("weather", [{}])[0].get("description", "").title()
            icon_code = forecast.get("weather", [{}])[0].get("icon", "01d")
            
            forecast_cards.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(date, size=14, weight=ft.FontWeight.BOLD),
                            ft.Image(
                                src=f"https://openweathermap.org/img/wn/{icon_code}.png",
                                width=50,
                                height=50,
                            ),
                            ft.Text(description, size=12, text_align=ft.TextAlign.CENTER),
                            ft.Text(
                                f"H: {temp_max:.0f}° L: {temp_min:.0f}°",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=10,
                    width=120,
                )
            )
        
        self.forecast_container.content = ft.Column(
            [
                ft.Text(
                    "5-Day Forecast",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    forecast_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                    spacing=10,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        self.forecast_container.visible = True
        self.page.update()
    
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()
    
    def show_weather_alerts(self, temp: float):
        """Show weather alerts based on conditions."""
        if temp > 35:
            alert = ft.Banner(
                bgcolor=ft.Colors.AMBER_100,
                leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER, size=40),
                content=ft.Text("⚠️ High temperature alert!"),
                actions=[
                    ft.TextButton("Dismiss", on_click=lambda e: self.close_banner()),
                ],
            )
            self.page.banner = alert
            self.page.banner.open = True
            self.page.update()
        elif temp < 0:
            alert = ft.Banner(
                bgcolor=ft.Colors.LIGHT_BLUE_100,
                leading=ft.Icon(ft.Icons.AC_UNIT, color=ft.Colors.BLUE, size=40),
                content=ft.Text("❄️ Freezing temperature alert!"),
                actions=[
                    ft.TextButton("Dismiss", on_click=lambda e: self.close_banner()),
                ],
            )
            self.page.banner = alert
            self.page.banner.open = True
            self.page.update()
    
    def close_banner(self):
        """Close the alert banner."""
        self.page.banner.open = False
        self.page.update()
    
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()
    
    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit."""
        if not self.current_weather_data:
            return
        
        if self.current_unit == "metric":
            self.current_unit = "imperial"
        else:
            self.current_unit = "metric"
        
        # Refresh display with current data
        self.page.run_task(self.refresh_weather_display)
    
    async def refresh_weather_display(self):
        """Refresh weather display with new units."""
        if self.current_weather_data:
            city = self.current_weather_data.get("name", "")
            if city:
                # Change the config unit temporarily
                old_unit = Config.UNITS
                Config.UNITS = self.current_unit
                
                try:
                    weather_data = await self.weather_service.get_weather(city)
                    self.current_weather_data = weather_data
                    await self.display_weather(weather_data)
                finally:
                    Config.UNITS = old_unit


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)
import math
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from datetime import datetime, timedelta
from datetime import datetime, timedelta, timezone
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError





class RestaurantBooker:

    @staticmethod
    def bookbyurl(url: str) -> str:
        """
        Book the restaurant through URL
        
        Args:
            url: the url contains "https://inline.app/booking/"
            
        Returns:
            the url
        """
        if not url.startswith("https://inline.app/booking/"):
            url = "https://inline.app/booking/" + url.lstrip("/")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach",True)
        driver = webdriver.Chrome(options = options,service=Service(ChromeDriverManager().install()))
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd(
            "Network.setExtraHTTPHeaders",
            {"headers": {
                "User-Agent": "Mozilla/5.0 ...",
                "Referer": "https://inline.app/"
            }}
        )
        driver.get("https://inline.app/booking/-OOuuRwnTgKRpg9MGo5J:inline-live-3/-OOuuS3WRVzDkx9z1xEW")
        sleep(15)
        driver.close()
        return f"Sucessfully book the restaurant through {url}"
    





class PaintCalculator:

    @staticmethod
    def calculate_paint_cost(area: float, price_per_gallon: float, add_paint_supply_costs: bool = False) -> float:
        """
        Calculate the total cost of paint needed for a given area.
        
        Args:
            area: Area to be painted in square feet
            price_per_gallon: Price per gallon of paint
            add_paint_supply_costs: Whether to add $50 for painting supplies
            
        Returns:
            Total cost of paint and supplies if requested
        """
        gallons_needed = math.ceil((area / 400) * 2) # Assuming 2 gallons are needed for 400 square feet
        total_cost = round(gallons_needed * price_per_gallon, 2)
        if add_paint_supply_costs:
            total_cost += 50
        return total_cost

    @staticmethod
    def calculate_paint_gallons_needed(area: float) -> int:
        """
        Calculate the number of gallons of paint needed for a given area.
        
        Args:
            area: Area to be painted in square feet
            
        Returns:
            Number of gallons needed (rounded up to ensure coverage)
        """
        # Using the same formula as in PaintCostCalculator: 2 gallons needed for 400 square feet
        gallons_needed = math.ceil((area / 400) * 2)
        return gallons_needed




class ShoppingCart:
    # In-memory shopping cart
    _cart_items = []
    
    @staticmethod
    def add_to_cart(store_name: str,phone:str) -> dict:
        """
        Add an item to the shopping cart.
        Add a product to a user's shopping cart.
        This function ensures a seamless update to the shopping cart by specifying each required input clearly.
        
        Args:
            product_name: Name of the paint product
            quantity: Number of units/gallons
            price_per_unit: Price per unit/gallon
            
        Returns:
            Dict with confirmation message and current cart items
        """
        now = datetime.now() + timedelta(hours=2)
        minute = now.minute

        
        if minute < 15:
            rounded_minute = 0
        elif minute < 45:
            rounded_minute = 30
        else:
            now += timedelta(hours=1)
            rounded_minute = 0

        
        time = now.replace(minute=rounded_minute, second=0, microsecond=0).strftime("%H:%M")

        item = {
            "store_name": store_name,
            "time": time,
            "phonenumber": phone,
        }
        
        
        ShoppingCart._cart_items.append(item)
        SCOPES = ["https://www.googleapis.com/auth/calendar"]

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("calendar", "v3", credentials=creds)

            # Current time in UTC+8 (Asia/Taipei)
            now = datetime.now(timezone.utc) + timedelta(hours=8)

            minute = now.minute
            if minute < 15:
                rounded_minute = 0
            elif minute < 45:
                rounded_minute = 30
            else:
                now += timedelta(hours=1)
                rounded_minute = 0

            start_time = now.replace(minute=rounded_minute, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=2)

            event = {
                "summary": "PRESERVE ORDER REMINDER",
                "location": "131 Trade Road, Section 2, Banqiao District, Taipei City",
                "description": "Phone: 0227863757",
                "colorId": "6",
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "Asia/Taipei",
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "Asia/Taipei",
                },
            }

            created_event = service.events().insert(calendarId="primary", body=event).execute()
            

        except HttpError as error:
            print(f"An error occurred: {error}")

        return {
            "message": f"Added {store_name} to your Callender Link:{created_event.get('htmlLink')}",
            "cart": ShoppingCart._cart_items
        }
    
    @staticmethod
    def get_cart_items() -> list:
        """
        Get all items currently in the shopping cart.
        
        Returns:
            List of items in the cart with their details
        """
        return ShoppingCart._cart_items
    
    @staticmethod
    def clear_cart() -> dict:
        """
        Clear all items from the shopping cart.
        
        Returns:
            Confirmation message
        """
        ShoppingCart._cart_items = []
        return {"message": "Shopping cart has been cleared"}
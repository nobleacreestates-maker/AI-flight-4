"""
AI Flight Search Agent - GUARANTEED Itinerary Generation
"""

import os
from datetime import datetime, timedelta
import json
from anthropic import Anthropic
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Map airport codes to city names for hotel searches
AIRPORT_TO_CITY = {
    # Europe - Western
    "BCN": "Barcelona, Spain",
    "MAD": "Madrid, Spain",
    "AGP": "Malaga, Spain",
    "PMI": "Palma de Mallorca, Spain",
    "IBZ": "Ibiza, Spain",
    "ALC": "Alicante, Spain",
    "SVQ": "Seville, Spain",
    "VLC": "Valencia, Spain",
    "PAR": "Paris, France",
    "CDG": "Paris, France",
    "ORY": "Paris, France",
    "NCE": "Nice, France",
    "MRS": "Marseille, France",
    "LYS": "Lyon, France",
    "ROM": "Rome, Italy",
    "FCO": "Rome, Italy",
    "MXP": "Milan, Italy",
    "VCE": "Venice, Italy",
    "NAP": "Naples, Italy",
    "FLR": "Florence, Italy",
    "AMS": "Amsterdam, Netherlands",
    "BRU": "Brussels, Belgium",
    "LUX": "Luxembourg City, Luxembourg",

    # Europe - Central
    "BER": "Berlin, Germany",
    "MUC": "Munich, Germany",
    "FRA": "Frankfurt, Germany",
    "DUS": "Dusseldorf, Germany",
    "HAM": "Hamburg, Germany",
    "CGN": "Cologne, Germany",
    "VIE": "Vienna, Austria",
    "SZG": "Salzburg, Austria",
    "ZRH": "Zurich, Switzerland",
    "GVA": "Geneva, Switzerland",
    "PRG": "Prague, Czech Republic",
    "BUD": "Budapest, Hungary",
    "WAW": "Warsaw, Poland",
    "KRK": "Krakow, Poland",

    # Europe - Northern
    "CPH": "Copenhagen, Denmark",
    "ARN": "Stockholm, Sweden",
    "OSL": "Oslo, Norway",
    "HEL": "Helsinki, Finland",
    "KEF": "Reykjavik, Iceland",

    # Europe - Southern & Eastern
    "LIS": "Lisbon, Portugal",
    "OPO": "Porto, Portugal",
    "FAO": "Faro, Portugal",
    "ATH": "Athens, Greece",
    "SKG": "Thessaloniki, Greece",
    "JTR": "Santorini, Greece",
    "CFU": "Corfu, Greece",
    "HER": "Heraklion, Greece",
    "IST": "Istanbul, Turkey",
    "AYT": "Antalya, Turkey",
    "DUB": "Dublin, Ireland",
    "SNN": "Shannon, Ireland",
    "ORK": "Cork, Ireland",
    "SOF": "Sofia, Bulgaria",
    "OTP": "Bucharest, Romania",
    "ZAG": "Zagreb, Croatia",
    "SPU": "Split, Croatia",
    "DBV": "Dubrovnik, Croatia",
    "LJU": "Ljubljana, Slovenia",

    # USA - East Coast
    "NYC": "New York, USA",
    "JFK": "New York, USA",
    "EWR": "Newark, USA",
    "LGA": "New York, USA",
    "BOS": "Boston, USA",
    "PHL": "Philadelphia, USA",
    "IAD": "Washington DC, USA",
    "DCA": "Washington DC, USA",
    "MIA": "Miami, USA",
    "FLL": "Fort Lauderdale, USA",
    "MCO": "Orlando, USA",
    "TPA": "Tampa, USA",
    "ATL": "Atlanta, USA",
    "CLT": "Charlotte, USA",

    # USA - West Coast & Central
    "LAX": "Los Angeles, USA",
    "SFO": "San Francisco, USA",
    "SJC": "San Jose, USA",
    "SAN": "San Diego, USA",
    "SEA": "Seattle, USA",
    "PDX": "Portland, USA",
    "LAS": "Las Vegas, USA",
    "PHX": "Phoenix, USA",
    "DEN": "Denver, USA",
    "DFW": "Dallas, USA",
    "IAH": "Houston, USA",
    "ORD": "Chicago, USA",
    "MSP": "Minneapolis, USA",
    "DTW": "Detroit, USA",
    "HNL": "Honolulu, USA",

    # Canada
    "YYZ": "Toronto, Canada",
    "YVR": "Vancouver, Canada",
    "YUL": "Montreal, Canada",
    "YYC": "Calgary, Canada",

    # Caribbean & Central America
    "CUN": "Cancun, Mexico",
    "MEX": "Mexico City, Mexico",
    "SJU": "San Juan, Puerto Rico",
    "NAS": "Nassau, Bahamas",
    "MBJ": "Montego Bay, Jamaica",
    "PUJ": "Punta Cana, Dominican Republic",
    "AUA": "Aruba",
    "CUR": "Curacao",
    "PTY": "Panama City, Panama",
    "SJO": "San Jose, Costa Rica",

    # South America
    "GRU": "Sao Paulo, Brazil",
    "GIG": "Rio de Janeiro, Brazil",
    "EZE": "Buenos Aires, Argentina",
    "SCL": "Santiago, Chile",
    "BOG": "Bogota, Colombia",
    "LIM": "Lima, Peru",

    # Asia - East
    "TYO": "Tokyo, Japan",
    "NRT": "Tokyo, Japan",
    "HND": "Tokyo, Japan",
    "KIX": "Osaka, Japan",
    "ICN": "Seoul, South Korea",
    "HKG": "Hong Kong",
    "PEK": "Beijing, China",
    "PVG": "Shanghai, China",
    "TPE": "Taipei, Taiwan",

    # Asia - Southeast
    "BKK": "Bangkok, Thailand",
    "HKT": "Phuket, Thailand",
    "SIN": "Singapore",
    "KUL": "Kuala Lumpur, Malaysia",
    "CGK": "Jakarta, Indonesia",
    "DPS": "Bali, Indonesia",
    "MNL": "Manila, Philippines",
    "SGN": "Ho Chi Minh City, Vietnam",
    "HAN": "Hanoi, Vietnam",

    # Asia - South
    "DEL": "New Delhi, India",
    "BOM": "Mumbai, India",
    "BLR": "Bangalore, India",
    "CMB": "Colombo, Sri Lanka",
    "MLE": "Maldives",
    "KTM": "Kathmandu, Nepal",

    # Middle East
    "DXB": "Dubai, UAE",
    "AUH": "Abu Dhabi, UAE",
    "DOH": "Doha, Qatar",
    "AHM": "Amman, Jordan",
    "TLV": "Tel Aviv, Israel",
    "CAI": "Cairo, Egypt",
    "SSH": "Sharm El Sheikh, Egypt",
    "HRG": "Hurghada, Egypt",
    "RUH": "Riyadh, Saudi Arabia",
    "JED": "Jeddah, Saudi Arabia",
    "MCT": "Muscat, Oman",
    "BAH": "Bahrain",
    "KWI": "Kuwait City, Kuwait",

    # Africa
    "JNB": "Johannesburg, South Africa",
    "CPT": "Cape Town, South Africa",
    "NBO": "Nairobi, Kenya",
    "CMN": "Casablanca, Morocco",
    "RAK": "Marrakech, Morocco",
    "TUN": "Tunis, Tunisia",
    "ACC": "Accra, Ghana",
    "LOS": "Lagos, Nigeria",
    "MRU": "Mauritius",
    "SEZ": "Seychelles",

    # Oceania
    "SYD": "Sydney, Australia",
    "MEL": "Melbourne, Australia",
    "BNE": "Brisbane, Australia",
    "PER": "Perth, Australia",
    "AKL": "Auckland, New Zealand",
    "CHC": "Christchurch, New Zealand",
    "NAN": "Fiji",

    # UK
    "LHR": "London, UK",
    "LGW": "London, UK",
    "STN": "London, UK",
    "LTN": "London, UK",
    "LCY": "London, UK",
    "SEN": "London Southend, UK",
    "MAN": "Manchester, UK",
    "BHX": "Birmingham, UK",
    "EDI": "Edinburgh, UK",
    "GLA": "Glasgow, UK",
    "BRS": "Bristol, UK",
    "NCL": "Newcastle, UK",
    "LPL": "Liverpool, UK",
    "LBA": "Leeds Bradford, UK",
    "EMA": "East Midlands, UK",
    "ABZ": "Aberdeen, UK",
    "BFS": "Belfast, UK",
    "CWL": "Cardiff, UK",
    "EXT": "Exeter, UK",
    "SOU": "Southampton, UK",
    "BOH": "Bournemouth, UK",
    "NQY": "Newquay, UK",
    "INV": "Inverness, UK",
    "JER": "Jersey, UK",
    "GCI": "Guernsey, UK",
    "IOM": "Isle of Man, UK"
}

def get_city_name(airport_code):
    """Convert airport code to city name"""
    return AIRPORT_TO_CITY.get(airport_code, airport_code)

class TravelPlanningAgent:
    def __init__(self):
        self.serpapi_key = os.environ.get("SERPAPI_KEY")
        
    def search_flights(self, origin, destination, outbound_date, return_date=None):
        """Search flights with detailed times and prices"""
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": outbound_date,
            "currency": "GBP",
            "hl": "en",
            "api_key": self.serpapi_key
        }
        
        if return_date:
            params["return_date"] = return_date
            params["type"] = "1"
        
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"Flight search error: {e}")
            return {"error": str(e)}
    
    def search_hotels(self, destination_code, check_in, check_out):
        """Search hotels with images and detailed info"""
        city_name = get_city_name(destination_code)
        print(f"Searching hotels for: {city_name}")
        
        params = {
            "engine": "google_hotels",
            "q": city_name,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "currency": "GBP",
            "gl": "uk",
            "hl": "en",
            "api_key": self.serpapi_key
        }
        
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            result = response.json()
            print(f"Hotel API returned {len(result.get('properties', []))} properties")
            return result
        except Exception as e:
            print(f"Hotel search error: {e}")
            return {"error": str(e)}
    
    def search_airbnb(self, destination_code, check_in, check_out):
        """Search Airbnb listings"""
        city_name = get_city_name(destination_code)
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        
        params = {
            "engine": "google",
            "q": f"airbnb {city_name}",
            "api_key": self.serpapi_key,
            "num": 10
        }
        
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            results = response.json()
            
            airbnb_listings = []
            if "organic_results" in results:
                for result in results["organic_results"][:8]:
                    if "airbnb" in result.get("link", "").lower():
                        airbnb_listings.append({
                            "name": result.get("title", "Airbnb Listing"),
                            "description": result.get("snippet", ""),
                            "link": result.get("link", "#"),
                            "price_per_night": "50-150",
                            "total_price": f"{nights * 75}",
                            "type": "Entire home/Private room"
                        })
            
            return airbnb_listings
        except Exception as e:
            print(f"Airbnb search error: {e}")
            return []
    
    def analyze_flexible_dates(self, origin, destination, start_date, return_date, days_range=10):
        """Search flights across flexible dates - expanded range for more options"""
        results = []
        base_date = datetime.strptime(start_date, "%Y-%m-%d")

        if return_date:
            return_date_obj = datetime.strptime(return_date, "%Y-%m-%d")

        # Search before and after the selected date for more flexibility
        search_offsets = list(range(-3, days_range + 1))  # -3 to +10 days from selected date

        for i in search_offsets:
            search_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
            # Skip past dates
            if datetime.strptime(search_date, "%Y-%m-%d") < datetime.now():
                continue

            search_return = (return_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") if return_date else None

            flight_data = self.search_flights(origin, destination, search_date, search_return)

            # Process best_flights
            if "best_flights" in flight_data:
                for flight in flight_data.get("best_flights", [])[:5]:  # Get top 5 from each day
                    flight_details = self._extract_flight_details(flight, origin, destination, search_date, search_return)
                    if flight_details:
                        results.append(flight_details)

            # Also check other_flights for budget options
            if "other_flights" in flight_data:
                for flight in flight_data.get("other_flights", [])[:3]:  # Get top 3 budget options
                    flight_details = self._extract_flight_details(flight, origin, destination, search_date, search_return)
                    if flight_details:
                        results.append(flight_details)

        return results

    def _extract_flight_details(self, flight, origin, destination, search_date, search_return):
        """Extract flight details from API response"""
        flights_info = flight.get("flights", [])
        outbound_flight = flights_info[0] if flights_info else {}

        # Handle return flights - could be in flights array or separate
        return_flight = None
        if len(flights_info) > 1:
            return_flight = flights_info[-1]  # Last flight is usually the return

        flight_details = {
            "outbound_date": search_date,
            "return_date": search_return,
            "price": flight.get("price"),
            "total_duration": flight.get("total_duration"),
            "airline": outbound_flight.get("airline", "Unknown"),
            "airline_logo": outbound_flight.get("airline_logo", ""),
            "outbound_departure_time": outbound_flight.get("departure_airport", {}).get("time", ""),
            "outbound_arrival_time": outbound_flight.get("arrival_airport", {}).get("time", ""),
            "outbound_departure_airport": outbound_flight.get("departure_airport", {}).get("id", origin),
            "outbound_arrival_airport": outbound_flight.get("arrival_airport", {}).get("id", destination),
            "outbound_duration": outbound_flight.get("duration"),
            "return_departure_time": return_flight.get("departure_airport", {}).get("time", "") if return_flight else "",
            "return_arrival_time": return_flight.get("arrival_airport", {}).get("time", "") if return_flight else "",
            "return_duration": return_flight.get("duration") if return_flight else "",
            "booking_link": f"https://www.google.com/travel/flights?q=Flights+from+{origin}+to+{destination}+on+{search_date}",
            "layovers": outbound_flight.get("layovers", []),
            "flight_number": outbound_flight.get("flight_number", ""),
            "airplane": outbound_flight.get("airplane", ""),
            "carbon_emissions": flight.get("carbon_emissions", {}).get("this_flight"),
            "is_overnight": outbound_flight.get("overnight", False)
        }

        return flight_details if flight_details.get("price") else None
    
    def create_structured_itinerary(self, destination_code, keywords, budget, duration_days, hotels):
        """GUARANTEED itinerary generation - ALWAYS returns complete data"""
        city_name = get_city_name(destination_code)

        print(f"\n=== CREATING ITINERARY ===")
        print(f"City: {city_name}")
        print(f"Duration: {duration_days} days")
        print(f"Budget: £{budget}")
        print(f"Keywords: {keywords}")

        # Build hotel context
        hotel_info = ""
        if hotels and "properties" in hotels:
            top_hotels = hotels["properties"][:3]
            hotel_info = "\n\nTop Hotels:\n"
            for hotel in top_hotels:
                hotel_info += f"- {hotel.get('name', 'N/A')}: £{hotel.get('rate_per_night', {}).get('lowest', 'N/A')}/night\n"

        # Enhanced prompt with more itinerary options
        prompt = f"""You are creating a comprehensive {duration_days}-day travel itinerary for {city_name}.

CRITICAL REQUIREMENTS:
1. Respond ONLY with valid JSON
2. NO markdown, NO code blocks, NO extra text
3. Include EXACTLY {duration_days} days in daily_itinerary array
4. Include 6-8 restaurants for breakfast, lunch, AND dinner
5. Include alternative activities and hidden gems

JSON Structure (copy this exactly):
{{
  "overview": {{
    "destination": "{city_name}",
    "best_time_to_visit": "Best months to visit with weather info",
    "getting_around": "Detailed transport options including metro, bus, taxi costs",
    "money_saving_tips": ["tip1", "tip2", "tip3", "tip4", "tip5"],
    "local_customs": "Cultural notes and etiquette",
    "emergency_info": "Emergency numbers and useful phrases",
    "best_neighborhoods": ["neighborhood1", "neighborhood2", "neighborhood3"]
  }},
  "daily_itinerary": [
    {{
      "day": 1,
      "theme": "Theme for day 1",
      "weather_tip": "What to expect/wear this time of year",
      "early_morning": {{
        "time": "7:00 AM",
        "activity": "Optional early activity (sunrise spots, markets)",
        "description": "For early risers",
        "cost": 0,
        "duration": "1-2 hours",
        "location": "Neighborhood",
        "is_optional": true
      }},
      "morning": {{
        "time": "9:00 AM",
        "activity": "Main morning activity",
        "description": "What to do and why",
        "cost": 15,
        "duration": "2-3 hours",
        "location": "Neighborhood",
        "insider_tip": "Beat the crowds tip"
      }},
      "morning_alternative": {{
        "time": "9:00 AM",
        "activity": "Alternative if main is crowded/closed",
        "description": "Great backup option",
        "cost": 10,
        "duration": "2 hours",
        "location": "Nearby area"
      }},
      "lunch_break": {{
        "time": "12:30 PM",
        "suggested_area": "Neighborhood for lunch",
        "budget_option": "Affordable local spot",
        "splurge_option": "Nice restaurant nearby"
      }},
      "afternoon": {{
        "time": "2:00 PM",
        "activity": "Main afternoon activity",
        "description": "What to do",
        "cost": 20,
        "duration": "3 hours",
        "location": "Neighborhood",
        "insider_tip": "Pro tip for this activity"
      }},
      "afternoon_alternative": {{
        "time": "2:00 PM",
        "activity": "Rainy day/alternative option",
        "description": "Indoor or different experience",
        "cost": 15,
        "duration": "2-3 hours",
        "location": "Area"
      }},
      "evening": {{
        "time": "6:00 PM",
        "activity": "Evening activity",
        "description": "What to do",
        "cost": 25,
        "duration": "2 hours",
        "location": "Neighborhood"
      }},
      "night": {{
        "time": "9:00 PM",
        "activity": "Nightlife/late evening option",
        "description": "For those with energy left",
        "cost": 30,
        "duration": "2-3 hours",
        "location": "Nightlife area",
        "is_optional": true
      }},
      "hidden_gem": {{
        "activity": "Local secret most tourists miss",
        "description": "Why it's special",
        "location": "Off the beaten path location",
        "best_time": "When to visit"
      }},
      "daily_total": 60
    }}
  ],
  "restaurants": {{
    "breakfast": [
      {{"name": "Café Name", "cuisine": "Type", "price_per_person": 12, "rating": 4.5, "description": "Why visit", "neighborhood": "Area", "signature_dish": "Dish", "best_for": "Quick bite/Leisurely brunch", "reservation_needed": false}}
    ],
    "lunch": [
      {{"name": "Restaurant", "cuisine": "Type", "price_per_person": 18, "rating": 4.6, "description": "Why visit", "neighborhood": "Area", "signature_dish": "Dish", "best_for": "Business/Casual/Date", "reservation_needed": false}}
    ],
    "dinner": [
      {{"name": "Restaurant", "cuisine": "Type", "price_per_person": 35, "rating": 4.7, "description": "Why visit", "neighborhood": "Area", "signature_dish": "Dish", "best_for": "Romantic/Family/Group", "reservation_needed": true}}
    ],
    "street_food": [
      {{"name": "Food stall/market", "specialty": "What they're known for", "price_range": "5-10", "location": "Where to find", "hours": "Operating hours"}}
    ],
    "cafes_bars": [
      {{"name": "Café/Bar name", "type": "Coffee shop/Wine bar/Cocktail bar", "vibe": "Atmosphere description", "must_try": "Signature drink", "neighborhood": "Area"}}
    ]
  }},
  "must_see_attractions": [
    {{"name": "Top attraction", "why": "Why it's unmissable", "time_needed": "2-3 hours", "best_time": "Early morning", "cost": 20, "skip_if": "When to skip it"}}
  ],
  "day_trips": [
    {{"destination": "Nearby place", "distance": "1 hour by train", "highlights": "What to see", "cost": 50, "best_for": "Day trip on day X"}}
  ],
  "budget_summary": {{
    "activities": 200,
    "food": 300,
    "transport": 75,
    "accommodation_estimate": 400,
    "total_estimate": 975,
    "budget_version": 600,
    "comfort_version": 1000,
    "luxury_version": 1800
  }}
}}

MUST include {duration_days} complete days with all time slots (early_morning, morning, morning_alternative, lunch_break, afternoon, afternoon_alternative, evening, night, hidden_gem).

User interests: {', '.join(keywords)}
Budget: £{budget}
{hotel_info}

Respond with ONLY the JSON object above."""

        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Clean response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            itinerary_data = json.loads(response_text)
            
            # CRITICAL VALIDATION
            if "daily_itinerary" not in itinerary_data or not itinerary_data["daily_itinerary"]:
                print("❌ NO daily_itinerary - using fallback")
                itinerary_data["daily_itinerary"] = self._get_default_itinerary(city_name, duration_days)
            else:
                # Check we have enough days
                if len(itinerary_data["daily_itinerary"]) < duration_days:
                    print(f"⚠️ Only {len(itinerary_data['daily_itinerary'])} days, need {duration_days} - filling gaps")
                    current_days = len(itinerary_data["daily_itinerary"])
                    for extra_day in range(current_days + 1, duration_days + 1):
                        itinerary_data["daily_itinerary"].append({
                            "day": extra_day,
                            "theme": f"Day {extra_day} Exploration",
                            "morning": {"time": "9:00 AM", "activity": "Morning exploration", "description": f"Explore {city_name}", "cost": 15, "duration": "2-3 hours", "location": "City Center"},
                            "afternoon": {"time": "2:00 PM", "activity": "Afternoon activity", "description": "Continue exploring", "cost": 20, "duration": "3 hours", "location": "Main area"},
                            "evening": {"time": "7:00 PM", "activity": "Evening entertainment", "description": "Dinner and relaxation", "cost": 30, "duration": "2 hours", "location": "Evening district"},
                            "daily_total": 65
                        })
            
            if "restaurants" not in itinerary_data or not itinerary_data["restaurants"]:
                print("❌ NO restaurants - using fallback")
                itinerary_data["restaurants"] = self._get_default_restaurants(city_name)
            
            print(f"✅ Itinerary created successfully:")
            print(f"   - Days: {len(itinerary_data['daily_itinerary'])}")
            print(f"   - Breakfast: {len(itinerary_data['restaurants'].get('breakfast', []))}")
            print(f"   - Lunch: {len(itinerary_data['restaurants'].get('lunch', []))}")
            print(f"   - Dinner: {len(itinerary_data['restaurants'].get('dinner', []))}")
            
            return itinerary_data
            
        except Exception as e:
            print(f"❌ Error creating itinerary: {e}")
            print("Using complete fallback...")
            return self._get_fallback_itinerary(city_name, duration_days)
    
    def _get_default_restaurants(self, city_name):
        """Fallback restaurant data"""
        return {
            "breakfast": [
                {"name": f"{city_name} Morning Café", "cuisine": "Café", "price_per_person": 12, "rating": 4.5, "description": "Popular breakfast spot with locals", "neighborhood": "City Center", "signature_dish": "Breakfast special", "best_for": "Quick bite", "reservation_needed": False},
                {"name": "Early Bird Bakery", "cuisine": "Bakery", "price_per_person": 10, "rating": 4.3, "description": "Fresh pastries and artisan bread", "neighborhood": "Old Town", "signature_dish": "Croissants", "best_for": "Pastry lovers", "reservation_needed": False},
                {"name": "Sunrise Bistro", "cuisine": "International", "price_per_person": 14, "rating": 4.4, "description": "Great coffee and brunch", "neighborhood": "Downtown", "signature_dish": "Full breakfast", "best_for": "Leisurely brunch", "reservation_needed": False},
                {"name": "The Local's Kitchen", "cuisine": "Traditional", "price_per_person": 11, "rating": 4.6, "description": "Where locals eat breakfast", "neighborhood": "Residential Area", "signature_dish": "Traditional breakfast", "best_for": "Authentic experience", "reservation_needed": False},
                {"name": "Healthy Start", "cuisine": "Health Food", "price_per_person": 15, "rating": 4.4, "description": "Organic and healthy options", "neighborhood": "Trendy District", "signature_dish": "Acai bowls", "best_for": "Health conscious", "reservation_needed": False},
                {"name": "Grand Hotel Café", "cuisine": "Continental", "price_per_person": 22, "rating": 4.7, "description": "Elegant breakfast experience", "neighborhood": "City Center", "signature_dish": "Eggs Benedict", "best_for": "Special occasion", "reservation_needed": True}
            ],
            "lunch": [
                {"name": f"{city_name} Lunch House", "cuisine": "Local", "price_per_person": 18, "rating": 4.6, "description": "Authentic local cuisine", "neighborhood": "City Center", "signature_dish": "Daily special", "best_for": "Local flavors", "reservation_needed": False},
                {"name": "Midday Kitchen", "cuisine": "Mediterranean", "price_per_person": 20, "rating": 4.5, "description": "Fresh ingredients daily", "neighborhood": "Harbor", "signature_dish": "Grilled fish", "best_for": "Seafood lovers", "reservation_needed": False},
                {"name": "Quick Bites", "cuisine": "International", "price_per_person": 12, "rating": 4.3, "description": "Fast and delicious", "neighborhood": "Business District", "signature_dish": "Gourmet sandwiches", "best_for": "Quick lunch", "reservation_needed": False},
                {"name": "Garden Terrace", "cuisine": "Fusion", "price_per_person": 25, "rating": 4.7, "description": "Beautiful outdoor seating", "neighborhood": "Park Area", "signature_dish": "Seasonal salads", "best_for": "Nice weather days", "reservation_needed": True},
                {"name": "Market Fresh", "cuisine": "Farm to Table", "price_per_person": 22, "rating": 4.6, "description": "Ingredients from local market", "neighborhood": "Market District", "signature_dish": "Market plate", "best_for": "Foodies", "reservation_needed": False},
                {"name": "Budget Bites", "cuisine": "Street Food", "price_per_person": 8, "rating": 4.4, "description": "Great value local food", "neighborhood": "Local Area", "signature_dish": "Street specialties", "best_for": "Budget travelers", "reservation_needed": False}
            ],
            "dinner": [
                {"name": f"{city_name} Fine Dining", "cuisine": "Fine Dining", "price_per_person": 55, "rating": 4.8, "description": "Upscale culinary experience", "neighborhood": "City Center", "signature_dish": "Tasting menu", "best_for": "Special occasions", "reservation_needed": True},
                {"name": "Evening Table", "cuisine": "Traditional", "price_per_person": 35, "rating": 4.7, "description": "Classic local dishes", "neighborhood": "Old Town", "signature_dish": "Regional specialties", "best_for": "Traditional experience", "reservation_needed": True},
                {"name": "Night Kitchen", "cuisine": "Contemporary", "price_per_person": 40, "rating": 4.6, "description": "Modern creative cuisine", "neighborhood": "Arts District", "signature_dish": "Chef's selection", "best_for": "Adventurous eaters", "reservation_needed": True},
                {"name": "Romantic Corner", "cuisine": "French", "price_per_person": 50, "rating": 4.8, "description": "Intimate atmosphere", "neighborhood": "Historic Quarter", "signature_dish": "Duck confit", "best_for": "Date night", "reservation_needed": True},
                {"name": "Family Feast", "cuisine": "Italian", "price_per_person": 28, "rating": 4.5, "description": "Family-style sharing plates", "neighborhood": "Residential", "signature_dish": "Pasta selection", "best_for": "Groups and families", "reservation_needed": False},
                {"name": "Late Night Eats", "cuisine": "Tapas", "price_per_person": 25, "rating": 4.4, "description": "Open late, great atmosphere", "neighborhood": "Nightlife Area", "signature_dish": "Tapas selection", "best_for": "Late dinner", "reservation_needed": False}
            ],
            "street_food": [
                {"name": "Central Food Market", "specialty": "Various local specialties", "price_range": "5-15", "location": "City Center", "hours": "8am-8pm"},
                {"name": "Night Market", "specialty": "Evening street food", "price_range": "5-12", "location": "Old Town Square", "hours": "6pm-midnight"},
                {"name": "Local Food Stalls", "specialty": "Traditional snacks", "price_range": "3-8", "location": "Near main station", "hours": "All day"}
            ],
            "cafes_bars": [
                {"name": "Historic Café", "type": "Traditional café", "vibe": "Classic atmosphere with history", "must_try": "Local coffee specialty", "neighborhood": "Old Town"},
                {"name": "Rooftop Bar", "type": "Cocktail bar", "vibe": "Stunning city views", "must_try": "Signature cocktail", "neighborhood": "City Center"},
                {"name": "Wine Corner", "type": "Wine bar", "vibe": "Cozy and sophisticated", "must_try": "Local wine selection", "neighborhood": "Arts District"},
                {"name": "Craft Beer House", "type": "Beer bar", "vibe": "Casual and friendly", "must_try": "Local craft beers", "neighborhood": "Trendy Area"}
            ]
        }
    
    def _get_default_itinerary(self, city_name, days):
        """Fallback daily itinerary with enhanced options"""
        itinerary = []
        themes = ["Cultural Discovery", "Historic Exploration", "Food & Markets", "Art & Museums", "Nature & Parks", "Shopping & Leisure", "Local Experience"]
        hidden_gems = [
            {"activity": "Local neighborhood walk", "description": "Explore where locals live", "location": "Residential area", "best_time": "Morning"},
            {"activity": "Secret viewpoint", "description": "Amazing views without crowds", "location": "Hilltop area", "best_time": "Sunset"},
            {"activity": "Local market", "description": "Authentic food market", "location": "Market district", "best_time": "Early morning"},
            {"activity": "Street art tour", "description": "Discover urban art scene", "location": "Arts district", "best_time": "Afternoon"},
            {"activity": "Vintage shopping", "description": "Unique finds and antiques", "location": "Old town", "best_time": "Midday"},
            {"activity": "Local park", "description": "Relax with the locals", "location": "City park", "best_time": "Late afternoon"},
            {"activity": "Traditional workshop", "description": "Learn local crafts", "location": "Artisan quarter", "best_time": "Morning"}
        ]

        for day in range(1, days + 1):
            theme = themes[(day - 1) % len(themes)]
            gem = hidden_gems[(day - 1) % len(hidden_gems)]
            itinerary.append({
                "day": day,
                "theme": theme,
                "weather_tip": "Check local forecast and dress in layers",
                "early_morning": {
                    "time": "7:00 AM",
                    "activity": f"Early morning in {city_name}",
                    "description": "For early risers - catch the city waking up",
                    "cost": 0,
                    "duration": "1-2 hours",
                    "location": "City Center",
                    "is_optional": True
                },
                "morning": {
                    "time": "9:00 AM",
                    "activity": f"Morning exploration - {theme}",
                    "description": f"Start your day exploring the best of {city_name}",
                    "cost": 15,
                    "duration": "2-3 hours",
                    "location": "City Center",
                    "insider_tip": "Arrive early to avoid crowds"
                },
                "morning_alternative": {
                    "time": "9:00 AM",
                    "activity": "Alternative morning activity",
                    "description": "Great backup if main attraction is busy",
                    "cost": 12,
                    "duration": "2 hours",
                    "location": "Nearby area"
                },
                "lunch_break": {
                    "time": "12:30 PM",
                    "suggested_area": "City Center dining area",
                    "budget_option": "Local market or street food (£8-12)",
                    "splurge_option": "Recommended restaurant nearby (£25-35)"
                },
                "afternoon": {
                    "time": "2:00 PM",
                    "activity": "Afternoon Exploration",
                    "description": "Visit main attractions and local spots",
                    "cost": 25,
                    "duration": "3-4 hours",
                    "location": "Main District",
                    "insider_tip": "Best time for photos in afternoon light"
                },
                "afternoon_alternative": {
                    "time": "2:00 PM",
                    "activity": "Indoor alternative (rainy day option)",
                    "description": "Museum or gallery visit",
                    "cost": 18,
                    "duration": "2-3 hours",
                    "location": "Museum District"
                },
                "evening": {
                    "time": "6:00 PM",
                    "activity": "Evening Activity",
                    "description": "Sunset views and pre-dinner drinks",
                    "cost": 20,
                    "duration": "2 hours",
                    "location": "Scenic viewpoint"
                },
                "night": {
                    "time": "9:00 PM",
                    "activity": "Nightlife experience",
                    "description": "Experience the local nightlife scene",
                    "cost": 35,
                    "duration": "2-3 hours",
                    "location": "Entertainment Area",
                    "is_optional": True
                },
                "hidden_gem": gem,
                "daily_total": 95
            })
        return itinerary
    
    def _get_fallback_itinerary(self, city_name, duration_days):
        """Complete fallback structure with enhanced options"""
        return {
            "overview": {
                "destination": city_name,
                "best_time_to_visit": "Year-round destination with peak season in summer months",
                "getting_around": "Public transport (metro/bus), walking in center, taxis/ride-share available",
                "money_saving_tips": [
                    "Use public transport instead of taxis",
                    "Book attractions online in advance for discounts",
                    "Eat at local spots away from tourist areas",
                    "Look for free walking tours (tip-based)",
                    "Visit museums on free entry days"
                ],
                "local_customs": "Respect local customs and traditions. Learn a few basic phrases in the local language.",
                "emergency_info": "Emergency: 112 (Europe) or local equivalent. Keep hotel address written down.",
                "best_neighborhoods": ["City Center", "Old Town", "Arts District"]
            },
            "daily_itinerary": self._get_default_itinerary(city_name, duration_days),
            "restaurants": self._get_default_restaurants(city_name),
            "must_see_attractions": [
                {"name": "Main Historic Site", "why": "The most iconic landmark", "time_needed": "2-3 hours", "best_time": "Early morning", "cost": 20, "skip_if": "Very crowded days"},
                {"name": "Famous Museum", "why": "World-class collection", "time_needed": "3-4 hours", "best_time": "Weekday afternoon", "cost": 15, "skip_if": "Limited time"},
                {"name": "Scenic Viewpoint", "why": "Best panoramic views", "time_needed": "1-2 hours", "best_time": "Sunset", "cost": 0, "skip_if": "Bad weather"}
            ],
            "day_trips": [
                {"destination": "Nearby Town", "distance": "1-2 hours by train", "highlights": "Historic center, local cuisine", "cost": 50, "best_for": "Extra day to explore"},
                {"destination": "Natural Area", "distance": "1 hour by bus", "highlights": "Scenic landscapes, hiking", "cost": 30, "best_for": "Nature lovers"}
            ],
            "budget_summary": {
                "activities": 250,
                "food": 350,
                "transport": 75,
                "accommodation_estimate": 450,
                "total_estimate": 1125,
                "budget_version": 650,
                "comfort_version": 1125,
                "luxury_version": 2000
            }
        }
    
    def find_best_value_flights(self, flight_results):
        """Sort and filter flights by value - returns more options"""
        if not flight_results:
            return []

        # Remove duplicates based on price and times
        seen = set()
        unique_flights = []
        for f in flight_results:
            key = (f.get("price"), f.get("outbound_departure_time"), f.get("outbound_date"))
            if key not in seen:
                seen.add(key)
                unique_flights.append(f)

        sorted_flights = sorted(unique_flights, key=lambda x: x.get("price", float('inf')))

        # Return more flights for better user choice (up to 20)
        return sorted_flights[:20]

agent = TravelPlanningAgent()

@app.route('/')
def home():
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        return jsonify({"message": "Travel Planning AI Agent", "error": str(e)})

@app.route('/itinerary', methods=['POST'])
def create_itinerary():
    data = request.json
    
    destination = data.get('destination')
    keywords = data.get('keywords', [])
    budget = data.get('budget', 1000)
    origin = data.get('origin')
    outbound_date = data.get('outbound_date')
    return_date = data.get('return_date')
    accommodation_type = data.get('accommodation_type', 'hotel')
    
    destination_city = get_city_name(destination)
    
    print(f"\n{'='*50}")
    print(f"NEW REQUEST")
    print(f"{'='*50}")
    print(f"Destination: {destination_city}")
    print(f"Budget: £{budget}")
    
    if not all([destination, origin, outbound_date]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Calculate duration
    if return_date:
        start = datetime.strptime(outbound_date, "%Y-%m-%d")
        end = datetime.strptime(return_date, "%Y-%m-%d")
        duration_days = (end - start).days
    else:
        duration_days = data.get('duration_days', 5)
        return_date = (datetime.strptime(outbound_date, "%Y-%m-%d") + timedelta(days=duration_days)).strftime("%Y-%m-%d")
    
    print(f"Duration: {duration_days} days")
    
    # Search flights
    all_flights = agent.analyze_flexible_dates(origin, destination, outbound_date, return_date, 7)
    best_flights = agent.find_best_value_flights(all_flights)
    print(f"Flights: {len(best_flights)} options")
    
    # Search accommodations
    hotel_options = []
    airbnb_options = []
    
    if accommodation_type in ['hotel', 'mixed']:
        hotels = agent.search_hotels(destination, outbound_date, return_date)
        if hotels and "properties" in hotels:
            for hotel in hotels.get("properties", [])[:10]:
                hotel_options.append({
                    "name": hotel.get("name", "N/A"),
                    "price_per_night": hotel.get("rate_per_night", {}).get("lowest", "N/A"),
                    "total_price": hotel.get("total_rate", {}).get("lowest", "N/A"),
                    "rating": hotel.get("overall_rating", "N/A"),
                    "reviews": hotel.get("reviews", 0),
                    "link": hotel.get("link", "#"),
                    "description": hotel.get("description", "")[:200],
                    "images": hotel.get("images", [])[:3],
                    "amenities": hotel.get("amenities", [])[:5],
                    "type": "hotel"
                })
        print(f"Hotels: {len(hotel_options)} found")
    
    if accommodation_type in ['airbnb', 'mixed']:
        airbnb_listings = agent.search_airbnb(destination, outbound_date, return_date)
        for listing in airbnb_listings:
            airbnb_options.append({
                "name": listing.get("name"),
                "price_per_night": listing.get("price_per_night"),
                "total_price": listing.get("total_price"),
                "description": listing.get("description"),
                "link": listing.get("link"),
                "type": "airbnb",
                "property_type": listing.get("type")
            })
        print(f"Airbnb: {len(airbnb_options)} found")
    
    # Calculate costs
    flight_cost = best_flights[0].get('price', 0) if best_flights else 0
    remaining_budget = budget - flight_cost
    
    # Create itinerary - GUARANTEED
    itinerary = agent.create_structured_itinerary(
        destination, 
        keywords, 
        remaining_budget, 
        duration_days, 
        hotels if accommodation_type in ['hotel', 'mixed'] else None
    )
    
    print(f"\n{'='*50}")
    print(f"RESPONSE READY")
    print(f"{'='*50}\n")
    
    return jsonify({
        "destination": destination_city,
        "keywords": keywords,
        "total_budget": budget,
        "trip_duration": duration_days,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "flight_options": best_flights,
        "recommended_flight_cost": flight_cost,
        "hotel_options": hotel_options,
        "airbnb_options": airbnb_options,
        "accommodation_type": accommodation_type,
        "remaining_budget": remaining_budget,
        "itinerary": itinerary
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

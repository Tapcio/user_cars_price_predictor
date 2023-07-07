# Functions to later move to other file
from calendar import c
import re
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def dealer_distance_regex(dealer_distance):
    # removing text from "dealer distance" column and converting to integer
    pattern = r"[^0-9.]+"
    result = re.sub(pattern, "", str(dealer_distance))[:-1]
    if result:
        return int(float(result))
    else:
        return 0

def convert_to_integer(number_as_string):
    # changes price from string that contains a coma (e.g. 100,000) to int
    number = str(number_as_string).replace(",", "")
    if number == "nan":
        return 0
    else:
        return int(number)

def extract_year(text):

    year = re.search(r"\b\d{4}\b", text).group()
    
    return year

def fuel_consumption_to_litres_per_100km(fuel_consumption):
    """
    string in following format: 20 City / 28 Highway that shows miles per gallon
    calculates to average of both and calculates it to litres per 100km
    """
    numbers = re.findall(r'\d+', fuel_consumption)
    city = int(numbers[0]) if numbers else 0
    highway = int(numbers[1]) if len(numbers) > 1 else 0
    
    # L/100km = 235.214/mpg
    if city != 0 and highway !=0:
        city_litres_per_100km = 235.214/city
        highway_litres_per_100km = 235.214/highway
    
        return round(((city_litres_per_100km + highway_litres_per_100km)/2), 2)
    
    else:
        return 0
    
def engine_description_cleanup(car):
    unwanted_rows = car["engine_description"].str.contains("Cylinder") | car["engine_description"].str.contains("Hybrid") | \
    car["engine_description"].str.contains("Plug-in") | car["engine_description"].str.contains("Electric")
    car = car[~unwanted_rows]
    return car

def convert_car_color(car_color):
    """
    conversion of atypical car colours to the usual ones
    e.g. to black, blue, green etc. 
    """
    color_map = {
        "Black Exterior": "black",
        "Black Stone Exterior": "black",
        "Black Sapphire Metallic Exterior": "black",
        "Alpine White Exterior": "white",
        "White Exterior": "white",
        "Jet Black Exterior": "black",
        "Imperial Blue Metallic Exterior": "blue",
        "Carbon Black Metallic Exterior": "black",
        "Space Gray Metallic Exterior": "gray",
        "Silver Exterior": "silver",
        "Blue Exterior": "blue",
        "Deep Sea Blue Metallic Exterior": "blue",
        "Melbourne Red Metallic Exterior": "red",
        "Mineral Gray Metallic Exterior": "gray",
        "White Metallic Exterior": "white",
        "Orion Silver Metallic Exterior": "silver",
        "Whi Exterior": "white",
        "Glacier Silver Metallic Exterior": "silver",
        "Gray Exterior": "gray",
        "Titanium Silver Metallic Exterior": "silver",
        "Red Exterior": "red",
        "Gray Metallic Exterior": "gray",
        "Platinum Gray Metallic Exterior": "gray",
        "Dark Graphite Metallic Exterior": "gray",
        "Callisto Gray Metallic Exterior": "gray",
        "Burgundy Exterior": "burgundy",
        "Citrin Black Metallic Exterior": "black",
        "Capparis White W/Bmw I Frozen Blue Accent Exterior": "white",
        "Blu Exterior": "blue",
        "Neptune Blue Metallic Exterior": "blue",
        "Spruce Green Exterior": "green",
        "Mineral Grey Metallic Exterior": "gray",
        "Ibis White Exterior": "white",
        "Brilliant Black Exterior": "black",
        "Glacier White Metallic Exterior": "white",
        "Phantom Black Pearl Effect Exterior": "black",
        "Quartz Gray Metallic Exterior": "gray",
        "Moonlight Blue Metallic Exterior": "blue",
        "Brown Exterior": "brown",
        "Ice Silver Metallic Exterior": "silver",
        "Orca Black Metallic Exterior": "black",
        "Monsoon Gray Metallic Exterior": "gray",
        "Florett Silver Metallic Exterior": "silver",
        "Charcoal Exterior": "charcoal",
        "Iridium Silver Metallic Exterior": "silver",
        "Palladium Silver Metallic Exterior": "silver",
        "Diamond White Metallic Exterior": "white",
        "Arctic White Exterior": "white",
        "Lunar Blue Metallic Exterior": "blue",
        "Obsidian Black Metallic Exterior": "black",
        "Capri Blue Metallic Exterior": "blue",
        "Polar White Exterior": "white",
        "Steel Gray Metallic Exterior": "gray",
        "Mars Red Exterior": "red",
        "Diamond Silver Metallic Exterior": "silver",
        "Steel Grey Metallic Exterior": "gray",
        "Cardinal Red Metallic Exterior": "red",
        "Beige Exterior": "beige",
        "Magnetite Black Metallic Exterior": "black",
        "Matte Black Wrap Exterior": "black",
        "Designo Mountain Gray Magno Exterior": "gray",
        "Electric Silver Metallic Exterior": "silver",
        "Ice White Exterior": "white",
        "Silver Metallic Exterior": "silver",
        "Savile Gray Metallic Exterior": "gray",
        "Tan Exterior": "beige",
        "Barents Blue Metallic Exterior": "blue",
        "Caspian Blue Metallic Exterior": "blue",
        "Ember Black Metallic Exterior": "black",
        "Crystal White Pearl Exterior": "white"
    }

    return color_map.get(car_color, "unknown")

def assigning_segment(car):
    
    segments = {
        "C": ["A3", "S3", "TT", "TTS", "1-Series", "Z4", "A-Class"],
        "D": ["A4", "A5", "S4", "S5", "3-Series", "C-Class", "CLA-Class", "SLC-Class", "SLK-Class"],
        "E": ["CL-Class", "A6", "S6", "5-Series", "E-Class", "R-Class"],
        "F": ["A7", "S7", "A8", "S8", "7-Series", "S-Class", "R8", "CLS-Class", "G-Class"],
        "S": ["RS-3", "RS-5", "RS-7", "TT-RS", "SL-Class"],
        "J-low": ["Q3", "Q5", "SQ5", "X1", "X2", "X3", "X4", "GLA-Class", "GLB-Class", "GLC-Class", "GLK-Class"],
        "J-High": ["SQ7", "SQ8", "X6", "Q7", "Q8", "X7", "X5", "M-Class", "GL-Class", "GLE-Class", "GLS-Class"]
    }
    
    car["segment"] = car["model"].map(lambda x: next((k for k, v in segments.items() if x in v), None))
    
    return car

def car_df_cleanup(car):
    """
    Cleaning DataFrame built from a scrapped data for a specific car brand. Dropping unnecessary columns,
    making numerical values from strings where necessary, finding generic colour numbers from
    'fancy car colours', and dropping rows with values that will interfere with training model later.
    (Colour == 'unknown', price == 0, and mileage == 0 are dropped.)
    """
    car["dealer distance"] = car["dealer distance"].map(dealer_distance_regex)
    car["year"] = car["year"].apply(extract_year)
    car["price"] = car["price"].map(convert_to_integer)
    car["mileage_x"] = car["mileage_x"].map(convert_to_integer)
    car["engine_description"] = car["engine_description"].str.split().str[0]
    car["exterior_colour"] = car["exterior_colour"].map(convert_car_color)

    car = car.drop(["link", "mileage_y", "name"], axis=1)

    car = car[car["price"] != 0]
    car = car[car["mileage_x"] != 0]
    car = car[car["exterior_colour"] != "unknown"]
    car = engine_description_cleanup(car)
    car = assigning_segment(car)
    car["dealer distance"] = car["dealer distance"].replace(0, int(car["dealer distance"].mean()))
    

    car.reset_index(drop=True, inplace=True)
        
    return car

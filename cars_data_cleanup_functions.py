# Functions to later move to other file
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

def extract_year_make_model(text):
    """
    Splits a string containing multiple values into columns: year, make, and model.
    Example: "Used 2007 Volvo S40 2.3T" will create new columns: year=2007, make="Volvo", model="S40".
    """
    year = re.search(r"\b\d{4}\b", text).group()
    name_temp = re.sub(r"<[^>]+>", "", text).strip()
    name_parts = name_temp.split()[2:4]
    make = name_parts[0]
    model = name_parts[1]
    
    return pd.Series([year, make, model], index=["year", "make", "model"])

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
    
def convert_car_color(car_color):
    """
    conversion of atypical car colours to the usual ones
    e.g. to black, blue, green etc. 
    """
    color_map = {
        "Black Exterior": "black",
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
        "Designo Mountain Gray Magno Exterior": "gray"
    }

    return color_map.get(car_color, "unknown")

def bmw_model_assignment(model_name):
    if model_name[0].isdigit():
        digit = re.search(r"\d", model_name)
        if digit:
            return int(digit.group())
    return model_name

def car_df_cleanup(car):
    """
    Cleaning DataFrame built from a scrapped data for a specific car brand. Dropping unnecessary columns,
    making numerical values from strings where necessary, finding generic colour numbers from
    'fancy car colours', and dropping rows with values that will interfere with training model later.
    (Colour == 'unknown', price == 0, and mileage == 0 are dropped.)
    """
    car["dealer distance"] = car["dealer distance"].map(dealer_distance_regex)
    car[["year", "make", "model"]] = car["name"].apply(extract_year_make_model)
    car["price"] = car["price"].map(convert_to_integer)
    car["mileage_x"] = car["mileage_x"].map(convert_to_integer)
    car["engine_description"] = car["engine_description"].str.split().str[0]
    car["exterior_colour"] = car["exterior_colour"].map(convert_car_color)

    car = car.drop(["link", "Unnamed: 0", "mileage_y", "name"], axis=1)

    car = car[car["price"] != 0]
    car = car[car["mileage_x"] != 0]
    car = car[car["exterior_colour"] != "unknown"]
    car["dealer distance"] = car["dealer distance"].replace(0, int(car["dealer distance"].mean()))

    # below is specific for BMW, as model names come as 535i or 335i instead of 3, or 5. (3 series, 5 series...)
    if car["make"][0] == "BMW":
        car["model"] = car["model"].map(bmw_model_assignment)
        car = car[~car["model"].apply(lambda x: car["model"].value_counts().get(x, 0) < 50)]

    return car

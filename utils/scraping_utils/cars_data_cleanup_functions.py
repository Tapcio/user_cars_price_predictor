# Functions to later move to other file
import re
import pandas as pd
from utils.scraping_utils.dictionaries_and_lists import color_map, segments


def pre_eda_car_df():
    audi = car_df_cleanup(pd.read_csv("data/audi_full.csv")).reset_index(drop=True)
    bmw = car_df_cleanup(pd.read_csv("data/bmw_full.csv")).reset_index(drop=True)
    mercedes = car_df_cleanup(pd.read_csv("data/mercedes_full.csv")).reset_index(
        drop=True
    )
    cars = pd.concat([audi, bmw, mercedes], axis=0, ignore_index=True)
    cars = cars.drop_duplicates(ignore_index=True).reset_index(drop=True)
    cars = cars.drop("Unnamed: 0", axis=1)
    return cars


def dealer_distance_regex(dealer_distance):
    # removing text from "dealer distance" column and converting to integer
    pattern = r"[^0-9.]+"
    result = re.sub(pattern, "", str(dealer_distance))[:-1]
    if result:
        return int(float(result))
    else:
        return 0


def engine_litres_to_number(engine_description):
    engine = engine_description[:-1]
    return float(engine)


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
    numbers = re.findall(r"\d+", fuel_consumption)
    city = int(numbers[0]) if numbers else 0
    highway = int(numbers[1]) if len(numbers) > 1 else 0

    # L/100km = 235.214/mpg
    if city != 0 and highway != 0:
        city_litres_per_100km = 235.214 / city
        highway_litres_per_100km = 235.214 / highway

        return round(((city_litres_per_100km + highway_litres_per_100km) / 2), 2)

    else:
        return 0


def engine_description_cleanup(car):
    unwanted_rows = (
        car["engine_description"].str.contains("Cylinder")
        | car["engine_description"].str.contains("Hybrid")
        | car["engine_description"].str.contains("Plug-in")
        | car["engine_description"].str.contains("Electric")
    )
    car = car[~unwanted_rows]
    return car


def convert_car_color(car_color):
    """
    conversion of atypical car colours to the usual ones
    e.g. to black, blue, green etc.
    """
    return color_map.get(car_color, "unknown")


def assigning_segment(car):
    car["segment"] = car["model"].map(
        lambda x: next((k for k, v in segments.items() if x in v), None)
    )

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

    car = car.drop(["link", "mileage_y"], axis=1)

    car = car[car["price"] != 0]
    car = car[car["mileage_x"] != 0]
    car = car[car["exterior_colour"] != "unknown"]
    car = engine_description_cleanup(car)
    car["engine_description"] = car["engine_description"].map(engine_litres_to_number)
    car = assigning_segment(car)
    car["dealer distance"] = car["dealer distance"].replace(
        0, int(car["dealer distance"].mean())
    )

    car.reset_index(drop=True, inplace=True)

    return car

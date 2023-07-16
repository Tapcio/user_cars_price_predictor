import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def extract_cars_autotrader_first_page(make, model):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    url = f"https://www.autotrader.com/cars-for-sale/{make}/{model}/roselle-nj?endYear=2020&isNewSearch=true&marketExtension=include&numRecords=100&searchRadius=0&sellerTypes=d&showAccelerateBanner=false&sortBy=relevance&startYear=2010&zip=07203"
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def extract_cars_autotrader_continuous_pages(make, model, page_number):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    url = f"https://www.autotrader.com/cars-for-sale/{make}/{model}/roselle-nj?endYear=2020&firstRecord={page_number}00&isNewSearch=false&marketExtension=include&numRecords=100&searchRadius=0&sellerTypes=d&showAccelerateBanner=false&sortBy=relevance&startYear=2010&zip=07203"
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def select_models_list(make):
    bmw_models = [
        "X1",
        "X2",
        "X3",
        "X4",
        "X5",
        "X6",
        "X7",
        "Z3",
        "Z4",
        "Z8",
        "1-Series",
        "3-Series",
        "5-Series",
        "7-Series",
    ]
    audi_models = [
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
        "A8",
        "Q3",
        "Q5",
        "Q7",
        "Q8",
        "R8",
        "RS-3",
        "RS-4",
        "RS-5",
        "RS-6",
        "RS-7",
        "S3",
        "S4",
        "S5",
        "S6",
        "S7",
        "S8",
        "SQ5",
        "SQ7",
        "SQ8",
        "TT",
        "TT-RS",
        "TTS",
    ]
    mercedes_benz_models = [
        "A-Class",
        "B-Class",
        "C-Class",
        "CL-Class",
        "CLA-Class",
        "CLK-Class",
        "CLS-Class",
        "E-Class",
        "EQB-Class",
        "EQE-Class",
        "EQS-Class",
        "G-Class",
        "GL-Class",
        "GLA-Class",
        "GLB-Class",
        "GLC-Class",
        "GLE-Class",
        "GLK-Class",
        "GLS-Class",
        "M-Class",
        "R-Class",
        "S-Class",
        "SL-Class",
        "SLC-Class",
        "SLK-Class",
    ]

    if make == "BMW":
        return bmw_models
    elif make == "Audi":
        return audi_models
    else:
        return mercedes_benz_models


def transform_car_soup(soup, make, model):
    car_info_list = []

    car_info = soup.find_all("div", class_="padding-0 panel-body")

    for car in car_info:
        car_name = car.find("h3")
        try:
            car_price = car.find("span", class_="first-price").text
        except:
            car_price = 0
        car_mileage_list = car.find_all("span", class_="text-bold")
        car_mileage_string_list = [str(x) for x in car_mileage_list]
        car_mileage = get_number_from_car_mileage_list(car_mileage_string_list)
        try:
            dealer_distance = car.find("span", class_="text-normal").text
        except:
            dealer_distance = "null"
        link = "https://www.autotrader.com" + car.find("a", {"rel": "nofollow"}).get(
            "href"
        )

        car_info = {
            "name": make,
            "model": model,
            "year": car_name,
            "price": car_price,
            "mileage": car_mileage,
            "dealer distance": dealer_distance,
            "link": link,
        }
        car_info_list.append(car_info)

    return car_info_list


def get_number_from_car_mileage_list(car_mileage):
    """
    The input car_mileage is an output from find_all() function of BeautifulSoup package.
    Autotrader has 2 classes with the same name and sometimes it doesn't return mileage.
    This is to pick only the mileage.
    """
    pattern = r"(\d[\d,]*) miles"

    for element in car_mileage:
        match = re.search(pattern, element)
        if match:
            string_before_miles = match.group(1)
            return string_before_miles


def autotrader_scrape_all_cars(make):
    ### Creating dataframe with all records below

    models_list = select_models_list(make)
    scraped_list = []

    for model in models_list:
        try:
            soup = extract_cars_autotrader_first_page(make, model)
            ### getting and counting amount of pages that we need to scrape through
            div_element = soup.find("div", class_="padding-top-3").text
            number = int(re.sub(r"\D", "", div_element))
            if (number / 100) > 1:
                num_of_pages = int(number / 100)
            else:
                num_of_pages = 0

            scraped_list.extend(transform_car_soup(soup, make, model))

            # Autotrader only allows to scrape 1000 records
            # Anything above that scrapes as duplicates of (900-1000)
            if num_of_pages > 9:
                num_of_pages = 9

            for page_number in range(1, num_of_pages + 1):
                soup = extract_cars_autotrader_continuous_pages(
                    make, model, page_number
                )
                scraped_list.extend(transform_car_soup(soup, make, model))
            print(f"{model} Scraped.")
        except Exception as e:
            error_message = f"Error scraping {model}: {str(e)}"
            print(error_message)
    df = pd.DataFrame(scraped_list)

    return df


def scrape_car_details(df):
    car_details_list = []

    print(f"Scraping details of each car. Total cars to scrape: {df.shape[0]}")

    for index, row in df.iterrows():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        r = requests.get(row["link"], headers)
        soup = BeautifulSoup(r.content, "html.parser")

        try:
            engine_description = (
                soup.find("div", {"aria-label": "ENGINE_DESCRIPTION"})
                .find_next("div", class_="col-xs-10")
                .text
            )
            mileage = (
                soup.find("div", {"aria-label": "MILEAGE"})
                .find_next("div", class_="col-xs-10")
                .text
            )
            drive_type = (
                soup.find("div", {"aria-label": "DRIVE TYPE"})
                .find_next("div", class_="col-xs-10")
                .text
            )
            exterior_colour = (
                soup.find("div", {"data-cmp": "colorSwatch"})
                .find_next("div", class_="col-xs-10")
                .text
            )
        except AttributeError:
            pass
        (
            electronic_steering,
            wheels,
            premium_interior,
            interior_technology,
            navigation,
            driving_assist,
            lights,
            roof,
            sound_system,
        ) = premium_components_finder(soup)

        car_details = {
            "engine_description": engine_description,
            "mileage": mileage,
            "drive_type": drive_type,
            "exterior_colour": exterior_colour,
            "electronic_steering": electronic_steering,
            "wheels": wheels,
            "premium_interior": premium_interior,
            "interior_technology": interior_technology,
            "navigation": navigation,
            "driving_assist": driving_assist,
            "lights": lights,
            "roof": roof,
            "sound_system": sound_system,
        }
        car_details_list.append(car_details)

    # Creating DataFrame from the List and merging it with the input DataFrame.
    car_details_list_df = pd.DataFrame(car_details_list)
    merged_df = pd.merge(df, car_details_list_df, left_index=True, right_index=True)

    return merged_df


def premium_components_finder(soup):
    premium_components = {
        "electronic_steering": [
            "heater door",
            "power door",
            "power folding",
            "power steering",
            "steering wheel memory",
            "keyless entry",
            "keyless start",
            "keyless",
        ],
        "wheels": ["alloy", "aluminum"],
        "premium_interior": ["wood", "leather", "ceramic", "premium seats", "heated"],
        "interior_technology": [
            "power driver seat",
            "power passenger seat",
            "power seat",
            "power adjustments",
            "memory",
            "garage door",
        ],
        "navigation": [
            "navigation",
            "trip computer",
            "computer",
            "touchscreen" "display",
        ],
        "driving_assist": [
            "speed control",
            "active lane",
            "active cruise",
            "control",
            "assistant",
            "blind spot",
            "parking camera",
            "parking assistant",
            "traffic jam",
        ],
        "lights": ["led", "high-beam", "automatic headlights"],
        "roof": ["generic sun/moonroof", "sunroof", "moonroof"],
        "sound_system": [
            "sirius",
            "apple",
            "harman",
            "kardon",
            "surround",
            "sound system",
            "sound",
        ],
    }

    premium_variables_booleans = []

    for key, values in premium_components.items():
        variable_value = 0  # if it is 0 at the end of iterating through values it appends 0 to the list
        for value in values:
            if value in str(soup):
                premium_variables_booleans.append(1)
                variable_value = 1
                break
        if variable_value == 0:
            premium_variables_booleans.append(0)

    return premium_variables_booleans


def autotrader_car_scraper(make):
    """
    Main Function that scrapes all details of specific make that are at the moment on the website.
    """
    df = scrape_car_details(autotrader_scrape_all_cars(make))
    return df

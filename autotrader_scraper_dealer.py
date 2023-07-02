from hmac import new
from tkinter import N
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def extract_cars_autotrader_first_page_dealer(make):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    url = f"https://www.autotrader.com/cars-for-sale/{make}/roselle-nj?endYear=2015&isNewSearch=true&marketExtension=include&numRecords=100&searchRadius=0&sellerTypes=d&showAccelerateBanner=false&sortBy=relevance&startYear=2005&zip=07203"
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

def extract_cars_autotrader_continuous_pages_dealer(make, num_of_pages):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    url = f"https://www.autotrader.com/cars-for-sale/{make}/roselle-nj?endYear=2015&firstRecord={num_of_pages}00&isNewSearch=false&marketExtension=include&numRecords=100&searchRadius=0&sellerTypes=d&showAccelerateBanner=false&sortBy=relevance&startYear=2005&zip=07203"
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

def transform_dealer(soup):
    car_info_list = []
    car_info = soup.find_all("div", class_ = "padding-0 panel-body")
    for car in car_info:
        car_name = car.find("h3")
        try: 
            car_price = car.find("span", class_ = "first-price").text
        except:
            car_price = 0
        car_mileage_list = car.find_all("span", class_ = "text-bold")
        car_mileage_string_list = [str(x) for x in car_mileage_list]
        car_mileage = get_number_from_car_mileage_list(car_mileage_string_list)
        try:
            dealer_distance = car.find("span", class_ = "text-normal").text
        except:
            dealer_distance = "null"
        link = "https://www.autotrader.com" + car.find("a", {"rel":"nofollow"}).get("href")
        
        car_info = {
                    "name": car_name,
                    "price": car_price,
                    "mileage": car_mileage,
                    "dealer distance": dealer_distance,
                    "link": link
                    }
        car_info_list.append(car_info)
        
    return car_info_list

def get_number_from_car_mileage_list(car_mileage):
    """
    The input car_mileage is an output from find_all() function of BeautifulSoup package.
    Autotrader has 2 classes with the same name and sometimes it doesn't return mileage.
    This is to pick only the mileage.
    """
    pattern = r'(\d[\d,]*) miles'

    for element in car_mileage:
        match = re.search(pattern, element)
        if match:
            string_before_miles = match.group(1)
            return string_before_miles

def autotrader_scrape_dealer(make):
    ### Creating dataframe with all records below
    soup = extract_cars_autotrader_first_page_dealer(make)

    ### counting amount of pages that we need to scrape through
    div_element = soup.find("div", class_ = "padding-top-3").text
    number = int(re.sub(r"\D", "", div_element))
    if (number/100) > 1:
        num_of_pages = int(number/100)
    else:
        num_of_pages = 0

    df = pd.DataFrame(transform_dealer(soup))
    total_scraping_time = num_of_pages * 1.17 # adjusted time to scrape one item
    print(f"Estimated scraping time: {total_scraping_time}min" )
    for page_number in range(1, num_of_pages+1):
        soup = extract_cars_autotrader_continuous_pages_dealer(make, page_number)
        car_list = transform_dealer(soup)
        df_car_list = pd.DataFrame(car_list)
        df_car_list.set_index(df_car_list.index + len(df), inplace=True)  
        df = pd.concat([df, df_car_list])

    # Reset the index
    df.reset_index(drop=True, inplace=True)
    return df

def scrape_details_dealer(df):
    car_details_list = []
    for index, row in df.iterrows():
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
        r = requests.get(row.link, headers)
        soup = BeautifulSoup(r.content, "html.parser")
        
        try:
            engine_description = soup.find("div", {"aria-label": "ENGINE_DESCRIPTION"}).find_next("div", class_ = "col-xs-10").text
            mileage = soup.find("div", {"aria-label": "MILEAGE"}).find_next("div", class_ = "col-xs-10").text
            drive_type = soup.find("div", {"aria-label": "DRIVE TYPE"}).find_next("div", class_ = "col-xs-10").text
            exterior_colour = soup.find("div", {"data-cmp": "colorSwatch"}).find_next("div", class_ = "col-xs-10").text
        except AttributeError:
            pass
            
        car_details = {
            "engine_description": engine_description,
            "mileage": mileage,
            "drive_type": drive_type,
            "exterior_colour": exterior_colour
        }
        car_details_list.append(car_details)
        
    # Creating DataFrame from the List and merging it with the input DataFrame.
    car_details_list_df = pd.DataFrame(car_details_list)    
    merged_df = pd.merge(df, car_details_list_df, left_index=True, right_index=True)
    
    return merged_df

def autotrader_car_scraper(make):
    """
    Main Function that scrapes all details of specific make that are at the moment on the website.
    """
    complete_dataframe = scrape_details_dealer(autotrader_scrape_dealer(make))
    return complete_dataframe
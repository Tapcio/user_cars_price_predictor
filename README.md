# Under Construction #

# Car Price Predictor #

This is a Learning Project for me, as I have never really created any app before, or worked on a dirty data to fit to the Machine Learning model.

This app contains following functions:

1. Autotrader.com scraper. It will scrape from the website details of all models from the seleted make. (So far it is only adjusted to work on Audi, BMW and Mercedes-Benz, but I will add an option to select more car makes.
2. Machine Learning Price Prediction. Once you have scraped date this will clean the data and fit the model. After my analysis I have selected XGBoost, as it made the best predictions.
3. You can select multiple features about your car: Make, Model, Year, Mileage, Engine Size, Drive Type and Equipment. Based on the information it will predict the price of the car.

Future enhancements:
1. I want add an option to compare with car prices in Poland (As I am Polish) and check whether it will be worth buying the car in the US and transport to Poland.
2. On the 2nd page I will add the links with offers, or maybe pictures to the adds with cars that are close to the selected options.

# requirements # 
`plotly` `dash` `requests` `bs4` `re` `sklearn` `xgboost` `joblib`

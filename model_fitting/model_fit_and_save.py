# Internal Function Files
import utils.scraping_utils.autotrader_scraper_dealer as a
import utils.scraping_utils.cars_data_cleanup_functions as c

# Typical libraries :-)
import pandas as pd

# Pipe For Sequential Function Running
from toolz import pipe

# Data pre-processing
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# Model
from xgboost import XGBRegressor

# Hyperparameter tuning
from sklearn.model_selection import GridSearchCV

# Saving model
import joblib

import warnings

warnings.filterwarnings("ignore")


def loading_cars_dataframe_for_fitting():
    # getting data from csv and merging to one DataFrame

    audi = c.car_df_cleanup(pd.read_csv("data/audi_full.csv")).reset_index(drop=True)
    bmw = c.car_df_cleanup(pd.read_csv("data/bmw_full.csv")).reset_index(drop=True)
    mercedes = c.car_df_cleanup(pd.read_csv("data/mercedes_full.csv")).reset_index(
        drop=True
    )
    cars = pd.concat([audi, bmw, mercedes], axis=0, ignore_index=True)
    cars = cars.drop_duplicates(ignore_index=True).reset_index(drop=True)
    cars = cars.drop(["Unnamed: 0", "exterior_colour", "name"], axis=1)

    return cars


def removing_potentially_unnecessary_data(cars):
    # Removing potentially unnecessary data

    if cars["navigation"].mean() == 1:
        cars = cars.drop("navigation", axis=1)

    if cars["lights"].mean() == 1:
        cars = cars.drop("lights", axis=1)

    drive_type_value_counts = cars["drive_type"].value_counts()
    drive_types_to_keep = drive_type_value_counts[
        drive_type_value_counts >= 100
    ].index.tolist()
    cars = cars[cars["drive_type"].isin(drive_types_to_keep)]

    return cars


def remove_outliers(cars):
    """
    Outliers calcualtion using Interquartile Range method (IQR).
    Removing all outliers based on the IQR results.
    """

    segments = cars["segment"].unique()
    outliers_min_values = {}
    for segment in segments:
        segment_data = cars[cars["segment"] == segment]
        price = segment_data["price"]

        q1 = price.quantile(0.25)
        q3 = price.quantile(0.75)
        iqr = q3 - q1
        threshold = 1.5

        outliers = price[
            (price < q1 - threshold * iqr) | (price > q3 + threshold * iqr)
        ]

        outliers_min_values.update({segment: min(outliers)})

    for segment, prices in outliers_min_values.items():
        rows_to_remove = cars[
            (cars["segment"] == segment) & (cars["price"] >= prices)
        ].index
        cars = cars.drop(rows_to_remove)

    return cars


def transform_to_categorical_and_numerical(cars):
    """
    Data transformation for model fitting
    """

    cars_categorical = cars.select_dtypes("object").columns
    cars_categorical = cars_categorical.drop(
        "model"
    )  # dropping since we already have "segment" column

    scaler = MinMaxScaler()
    cars["year"] = scaler.fit_transform(cars["year"].values.reshape(-1, 1))

    dummy_variables = pd.get_dummies(cars[cars_categorical])
    cars = pd.concat([cars, dummy_variables], axis=1)

    return cars


def fit_theXGBoost_model_and_save_model(cars):
    """
    Split the dataset, fit the model, save the model.
    """
    cars = cars.loc[:, ~cars.columns.duplicated()]
    X = cars.drop(
        ["model", "price", "drive_type", "segment", "dealer distance"], axis=1
    )  # I do not want "model" as I already have "segment"
    y = cars["price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    input_model = XGBRegressor()

    param_grid = {
        "nthread": [4],
        "learning_rate": [0.03],
        "max_depth": [7, 10],
        "min_child_weight": [4],
        "subsample": [0.7],
        "colsample_bytree": [0.7],
        "n_estimators": [500],
    }

    grid_search = GridSearchCV(
        estimator=input_model, param_grid=param_grid, cv=2, n_jobs=-1, verbose=True
    )

    grid_search.fit(X_train, y_train)

    joblib.dump(
        grid_search.best_estimator_,
        "model_fitting/final_car_price_prediction_model.pkl",
    )
    joblib.dump(list(X.columns), "model_fitting/column_names.pkl")


def download_data_fit_model_save_model():
    cars = loading_cars_dataframe_for_fitting()

    pipe(
        cars,
        removing_potentially_unnecessary_data,
        remove_outliers,
        transform_to_categorical_and_numerical,
        fit_theXGBoost_model_and_save_model,
    )
    print("Model Saved in the Project Folder")

import pandas as pd
import joblib
from utils.scraping_utils import cars_data_cleanup_functions

cars = cars_data_cleanup_functions.pre_eda_car_df()
loaded_model = joblib.load("model_fitting/final_car_price_prediction_model.pkl")
columns = joblib.load("model_fitting/column_names.pkl")


def update_output(
    n_clicks, mileage, year, engine_size, drive_type, equipment, make, model
):
    if None in [mileage, year, engine_size, drive_type, equipment, make, model]:
        return ""

    values_for_prediction = []

    values_for_prediction.append(int(year))
    values_for_prediction.append(mileage)
    values_for_prediction.append(engine_size)

    if equipment == "Luxury":
        values_for_prediction.extend([1, 1, 1, 1, 1, 1, 1])
    elif equipment == "Good":
        values_for_prediction.extend([1, 1, 0, 0, 1, 1, 1])
    elif equipment == "Medium":
        values_for_prediction.extend([0, 1, 0, 0, 1, 0, 1])
    else:
        values_for_prediction.extend([0, 0, 0, 0, 0, 0, 0])

    if drive_type == "4WD":
        values_for_prediction.extend([0, 0, 1])
    elif drive_type == "FWD":
        values_for_prediction.extend([1, 0, 0])
    else:
        values_for_prediction.extend([0, 1, 0])

    segment = cars.loc[cars["model"] == model, "segment"].values[0]

    if segment == "C":
        values_for_prediction.extend([1, 0, 0, 0, 0, 0, 0])
    elif segment == "D":
        values_for_prediction.extend([0, 1, 0, 0, 0, 0, 0])
    elif segment == "E":
        values_for_prediction.extend([0, 0, 1, 0, 0, 0, 0])
    elif segment == "F":
        values_for_prediction.extend([0, 0, 0, 1, 0, 0, 0])
    elif segment == "J-High":
        values_for_prediction.extend([0, 0, 0, 0, 1, 0, 0])
    elif segment == "J-Low":
        values_for_prediction.extend([0, 0, 0, 0, 0, 1, 0])
    else:
        values_for_prediction.extend([0, 0, 0, 0, 0, 0, 1])

    df = pd.DataFrame(data=[values_for_prediction], columns=columns)
    prediction = loaded_model.predict(df)
    price = round((prediction[0] * 1), 2)
    return f"Car Price: ${price}"

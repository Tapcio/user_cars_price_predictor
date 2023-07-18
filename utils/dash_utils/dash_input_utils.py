import numpy as np
import dash_bootstrap_components as dbc
from dash import dcc, html
from utils.scraping_utils import cars_data_cleanup_functions

cars = cars_data_cleanup_functions.pre_eda_car_df()

dash_row_one = dbc.Row(
    [
        dbc.Col(
            [
                html.H6("Make"),
                dcc.Dropdown(
                    id="make-dropdown",
                    options=[
                        {"label": make, "value": make} for make in cars["name"].unique()
                    ],
                    style={"margin-bottom": "10px"},
                ),
            ],
            className="col-sm",
        ),
        dbc.Col(
            [
                html.H6("Model"),
                dcc.Dropdown(
                    id="model-dropdown",
                    className="dropdown-class",
                    style={"margin-bottom": "10px"},
                ),
            ]
        ),
    ],
    class_name="row sm-2",
)

dash_row_two = dbc.Row(
    [
        dbc.Col(
            [
                html.H6("Year"),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=[
                        {"label": str(year), "value": year}
                        for year in np.sort(cars["year"].unique())
                    ],
                    style={"margin-bottom": "10px"},
                ),
            ]
        ),
        dbc.Col(
            [
                html.H6("Mileage"),
                dcc.Slider(
                    id="mileage-slider",
                    min=0,
                    max=300000,
                    value=0,
                ),
            ]
        ),
    ],
    className="mb-2",
)

dash_row_three = dbc.Row(
    [
        dbc.Col(
            [
                html.H6("Engine"),
                dcc.Dropdown(
                    id="engine-dropdown",
                    options=[
                        {"label": str(engine_size), "value": engine_size}
                        for engine_size in np.sort(cars["engine_description"].unique())
                    ],
                    style={"margin-bottom": "10px"},
                ),
            ]
        ),
        dbc.Col(
            [
                html.H6("Drive Type"),
                dcc.Dropdown(
                    id="drive-type-dropdown",
                    options=[
                        {"label": drive_type, "value": drive_type}
                        for drive_type in ["4WD", "FWD", "RWD"]
                    ],
                    style={"margin-bottom": "10px"},
                ),
            ]
        ),
    ]
)

dash_row_four = dbc.Row(
    [
        dbc.Col(
            [
                html.H6("Equipment"),
                dcc.Dropdown(
                    id="equipment-level-dropdown",
                    options=[
                        {"label": equipment, "value": equipment}
                        for equipment in ["Luxury", "Good", "Medium", "Low"]
                    ],
                    style={"margin-bottom": "10px"},
                ),
            ]
        ),
        dbc.Col(
            [
                html.Div(
                    dbc.Button(
                        "Predict Price",
                        className="me-1",
                        id="submit-button-state",
                        color="dark",
                        style={"width": "250px"},
                    ),
                    className="d-flex justify-content-center",
                    style={
                        "display": "inline-block",
                        "margin-top": "25px",
                        "margin-left": "200px",
                        "verticalAlign": "middle",
                    },
                ),
            ],
            className="d-flex align-items-center",
        ),
    ]
)

import dash_bootstrap_components as dbc
from utils.scraping_utils import cars_data_cleanup_functions

from dash import Dash, html, Input, Output, State

from utils.dash_utils.dash_input_utils import (
    dash_row_one,
    dash_row_two,
    dash_row_three,
    dash_row_four,
)
from utils.dash_utils.dash_output_utils import dash_row_five, navbar
from utils.dash_utils.dash_functions import update_output

cars = cars_data_cleanup_functions.pre_eda_car_df()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX, "styles.css"],
    suppress_callback_exceptions=True,
)

app.layout = html.Div(
    [
        html.Link(href="/assets/styles.css", rel="stylesheet"),
        navbar,
        html.Div(
            [
                dash_row_one,
                dash_row_two,
                dash_row_three,
                dash_row_four,
            ],
            className="container",
            style={"padding-top": "25px", "padding-bottom": "25px", "color": "black"},
        ),
        html.Div(
            [
                dash_row_five,
                html.Div(id="prediction", style={"font-size": "50px"}),
            ],
            className="container",
        ),
    ]
)


@app.callback(
    Output("model-dropdown", "options"),
    Input("make-dropdown", "value"),
)
def update_model_dropdown(make):
    if make:
        models = cars.loc[cars["name"] == make, "model"].unique()
        options = [{"label": model, "value": model} for model in models]
        return options
    else:
        return []


@app.callback(
    Output("prediction", "children"),
    Input("submit-button-state", "n_clicks"),
    State("mileage-slider", "value"),
    State("year-dropdown", "value"),
    State("engine-dropdown", "value"),
    State("drive-type-dropdown", "value"),
    State("equipment-level-dropdown", "value"),
    State("make-dropdown", "value"),
    State("model-dropdown", "value"),
)
def callback_update_output(
    n_clicks, mileage, year, engine_size, drive_type, equipment, make, model
):
    if None in [mileage, year, engine_size, drive_type, equipment, make, model]:
        return ""

    return update_output(
        n_clicks, mileage, year, engine_size, drive_type, equipment, make, model
    )


@app.callback(Output("mileage-gauge", "value"), Input("mileage-slider", "value"))
def mileage_update(mileage):
    return mileage / 1000


@app.callback(Output("engine-size-output", "value"), Input("engine-dropdown", "value"))
def engine_update(engine_size):
    return engine_size


@app.callback(
    Output("make-dropdown-output", "children"),
    [Input("make-dropdown", "value"), Input("model-dropdown", "value")],
)
def make_and_model_update(make, model):
    if make and model:
        make_model = f"{make} {model}"
        return make_model
    else:
        return ""


@app.callback(
    Output("year-dropdown-output", "children"), Input("year-dropdown", "value")
)
def year_update(year):
    return year


@app.callback(
    Output("drive-type-dropdown-output", "children"),
    Input("drive-type-dropdown", "value"),
)
def drive_type_update(drive_type):
    return drive_type


@app.callback(
    Output("equipment-dropdown-output", "children"),
    Input("equipment-level-dropdown", "value"),
)
def equipment_update(equipment):
    return equipment


if __name__ == "__main__":
    app.run_server(debug=True)

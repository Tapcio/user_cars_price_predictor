import dash_bootstrap_components as dbc
import dash_daq as daq
from utils.scraping_utils import cars_data_cleanup_functions
from dash import html

cars = cars_data_cleanup_functions.pre_eda_car_df()

card_content = []

dash_row_five = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                [
                                    dbc.CardHeader("Make and Model"),
                                    dbc.CardBody(html.Div(id="make-dropdown-output")),
                                ],
                                id="make-dropdown-output-card",
                                className="card-class",
                            ),
                            width=6,
                            align="center",
                        ),
                        dbc.Col(
                            dbc.Card(
                                [
                                    dbc.CardHeader("Year"),
                                    dbc.CardBody(html.Div(id="year-dropdown-output")),
                                ],
                                id="year-dropdown-output-card",
                            ),
                            width=6,
                            align="center",
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                [
                                    dbc.CardHeader("Drive Type"),
                                    dbc.CardBody(
                                        html.Div(id="drive-type-dropdown-output")
                                    ),
                                ],
                                id="drive-type-dropdown-output-card",
                            ),
                            width=6,
                            align="center",
                        ),
                        dbc.Col(
                            dbc.Card(
                                [
                                    dbc.CardHeader("Equipment"),
                                    dbc.CardBody(
                                        html.Div(id="equipment-dropdown-output")
                                    ),
                                ],
                                id="equipment-dropdown-output-card",
                            ),
                            width=6,
                            align="center",
                        ),
                    ],
                    className="mb-2",
                ),
            ],
            width=6,
            align="center",
        ),
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            daq.Gauge(
                                id="mileage-gauge",
                                label="Mileage",
                                min=0,
                                max=300,
                                value=0,
                                showCurrentValue=True,
                                units="k mi.",
                            ),
                            width=6,
                            align="center",
                        ),
                        dbc.Col(
                            daq.Tank(
                                id="engine-size-output",
                                label="Engine Size",
                                min=0,
                                max=(cars["engine_description"].max()),
                                value=0,
                                showCurrentValue=True,
                                units="L",
                            ),
                            width=6,
                            align="center",
                        ),
                    ],
                    className="mb-2",
                ),
            ],
            width=6,
            align="center",
        ),
    ],
    style={"border-style": "solid"},
    align="center",
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Car Price Prediction Dashboard",
    brand_href="#",
)

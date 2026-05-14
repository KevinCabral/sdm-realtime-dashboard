import dash_bootstrap_components as dbc
from dash import html


def metric_card(title: str, value: str, color: str = "primary") -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(title, className="metric-title"),
                html.H3(value, className="metric-value"),
            ]
        ),
        color=color,
        outline=True,
        class_name="h-100",
    )

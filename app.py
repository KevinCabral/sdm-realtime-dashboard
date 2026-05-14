from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dash_table, dcc, html

from components.dashboard_components import metric_card
from services.audit import setup_audit_logging
from services.config import APP_HOST, APP_PORT, DEBUG, REFRESH_INTERVAL_MS
from services.data_service import TurnoutService, get_display_status
from services.security import authenticate_request, authorize_access

setup_audit_logging()
turnout_service = TurnoutService()

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = dbc.Container(
    [
        dcc.Interval(id="refresh-interval", interval=REFRESH_INTERVAL_MS, n_intervals=0),
        html.H2("Election Turnout Operations Dashboard", className="mt-3 mb-1"),
        html.P("Operational monitoring only: voted, not voted, pending validation."),
        dbc.Alert(
            "Authentication and role-based access are placeholders for secure integration.",
            color="warning",
            class_name="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Input(id="search-input", placeholder="Search voter name or ID", className="form-control"), md=3),
                dbc.Col(dcc.Dropdown(id="station-filter", placeholder="Filter by polling station"), md=3),
                dbc.Col(dcc.Dropdown(id="region-filter", placeholder="Filter by region"), md=3),
                dbc.Col(
                    dcc.Dropdown(
                        id="status-filter",
                        placeholder="Filter by voting status",
                        options=[
                            {"label": "Voted", "value": "voted"},
                            {"label": "Not Voted", "value": "not voted"},
                            {"label": "Pending Validation", "value": "pending validation"},
                        ],
                    ),
                    md=3,
                ),
            ],
            class_name="g-2 mb-3",
        ),
        html.Div(id="error-container"),
        dcc.Loading(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Div(id="total-registered"), md=3),
                        dbc.Col(html.Div(id="total-voted"), md=3),
                        dbc.Col(html.Div(id="total-not-voted"), md=3),
                        dbc.Col(html.Div(id="turnout-percentage"), md=3),
                    ],
                    class_name="g-2 mb-3",
                ),
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id="votes-by-station"), lg=6),
                        dbc.Col(dcc.Graph(id="votes-by-region"), lg=6),
                    ],
                    class_name="g-2",
                ),
                dbc.Row([dbc.Col(dcc.Graph(id="hourly-trend"), md=12)], class_name="g-2 mt-1"),
                dash_table.DataTable(
                    id="voter-table",
                    page_size=10,
                    sort_action="native",
                    filter_action="none",
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left"},
                    columns=[
                        {"name": "voter_id", "id": "voter_id"},
                        {"name": "full_name", "id": "full_name"},
                        {"name": "polling_station", "id": "polling_station"},
                        {"name": "region", "id": "region"},
                        {"name": "has_voted", "id": "has_voted"},
                        {"name": "voted_at", "id": "voted_at"},
                        {"name": "validation_status", "id": "validation_status"},
                    ],
                ),
                html.Div(id="last-updated", className="last-updated mt-2 mb-4"),
            ],
            type="default",
        ),
    ],
    fluid=True,
)


@callback(
    Output("station-filter", "options"),
    Output("region-filter", "options"),
    Input("refresh-interval", "n_intervals"),
)
def set_filter_options(_: int):
    user = authenticate_request()
    data, _ = turnout_service.get_turnout_data(actor=user.username)
    stations = sorted(data["polling_station"].dropna().unique())
    regions = sorted(data["region"].dropna().unique())
    return (
        [{"label": station, "value": station} for station in stations],
        [{"label": region, "value": region} for region in regions],
    )


@callback(
    Output("error-container", "children"),
    Output("total-registered", "children"),
    Output("total-voted", "children"),
    Output("total-not-voted", "children"),
    Output("turnout-percentage", "children"),
    Output("votes-by-station", "figure"),
    Output("votes-by-region", "figure"),
    Output("hourly-trend", "figure"),
    Output("voter-table", "data"),
    Output("last-updated", "children"),
    Input("refresh-interval", "n_intervals"),
    Input("search-input", "value"),
    Input("station-filter", "value"),
    Input("region-filter", "value"),
    Input("status-filter", "value"),
)
def refresh_dashboard(
    _: int,
    search: str | None,
    station: str | None,
    region: str | None,
    status_filter: str | None,
):
    try:
        user = authenticate_request()
        if not authorize_access(user, "election_operator"):
            raise PermissionError("Access denied for current role")

        data, last_updated = turnout_service.get_turnout_data(actor=user.username)
        data["display_status"] = get_display_status(data)
        filtered = data.copy()

        if search:
            term = search.strip().lower()
            filtered = filtered[
                filtered["voter_id"].str.lower().str.contains(term)
                | filtered["full_name"].str.lower().str.contains(term)
            ]
        if station:
            filtered = filtered[filtered["polling_station"] == station]
        if region:
            filtered = filtered[filtered["region"] == region]
        if status_filter:
            filtered = filtered[filtered["display_status"] == status_filter]

        total_registered = len(data)
        total_voted = int(data["has_voted"].sum())
        total_not_voted = int((~data["has_voted"]).sum())
        turnout = (total_voted / total_registered * 100) if total_registered else 0

        station_counts = (
            data[data["has_voted"]]
            .groupby("polling_station", as_index=False)
            .size()
            .rename(columns={"size": "votes"})
        )
        region_counts = (
            data[data["has_voted"]]
            .groupby("region", as_index=False)
            .size()
            .rename(columns={"size": "votes"})
        )

        trend_source = data[data["has_voted"] & data["voted_at"].notna()].copy()
        if not trend_source.empty:
            trend_source["hour"] = trend_source["voted_at"].dt.strftime("%Y-%m-%d %H:00")
            trend = trend_source.groupby("hour", as_index=False).size().rename(columns={"size": "votes"})
        else:
            trend = pd.DataFrame({"hour": [], "votes": []})

        station_fig = px.bar(station_counts, x="polling_station", y="votes", title="Votes by Polling Station")
        region_fig = px.bar(region_counts, x="region", y="votes", title="Votes by Region / Municipality")
        trend_fig = px.line(trend, x="hour", y="votes", markers=True, title="Hourly Voting Trend")

        table_data = filtered[
            [
                "voter_id",
                "full_name",
                "polling_station",
                "region",
                "has_voted",
                "voted_at",
                "validation_status",
            ]
        ].copy()
        table_data["voted_at"] = table_data["voted_at"].apply(
            lambda value: value.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(value) else ""
        )

        last_update_text = f"Last update: {last_updated.strftime('%Y-%m-%d %H:%M:%S UTC')}"

        return (
            None,
            metric_card("Total registered voters", str(total_registered)),
            metric_card("Total voted", str(total_voted), "success"),
            metric_card("Total not voted", str(total_not_voted), "danger"),
            metric_card("Turnout percentage", f"{turnout:.2f}%", "info"),
            station_fig,
            region_fig,
            trend_fig,
            table_data.to_dict("records"),
            last_update_text,
        )
    except Exception as exc:
        return (
            dbc.Alert(f"Unable to refresh dashboard data: {exc}", color="danger"),
            metric_card("Total registered voters", "N/A"),
            metric_card("Total voted", "N/A"),
            metric_card("Total not voted", "N/A"),
            metric_card("Turnout percentage", "N/A"),
            px.bar(title="Votes by Polling Station"),
            px.bar(title="Votes by Region / Municipality"),
            px.line(title="Hourly Voting Trend"),
            [],
            f"Last update attempt: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        )


if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG)

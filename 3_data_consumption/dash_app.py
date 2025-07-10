import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import requests

# Load your data
df = pd.read_csv("sentiment_analysis.csv")
company_options = [{"label": c, "value": c} for c in df["company"].dropna().unique()]

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Sentiment Dashboard"

# Pre-build graphs with improved styles
rating_fig = px.histogram(
    df, x="actual_sentiment_score", nbins=5, title="Rating Distribution",
    color_discrete_sequence=["#636EFA"]
)
rating_fig.update_traces(
    marker_line_color="black", marker_line_width=1.5, opacity=0.75
)
rating_fig.update_layout(
    bargap=0.2,
    xaxis_title="Actual Sentiment Score",
    yaxis_title="Count",
    template="plotly_white"
)

vader_fig = px.histogram(
    df, x="vader_compound", nbins=20, title="VADER Score Distribution",
    color_discrete_sequence=["#EF553B"]
)
vader_fig.update_traces(
    marker_line_color="black", marker_line_width=1.5, opacity=0.75
)
vader_fig.update_layout(
    bargap=0.1,
    xaxis_title="VADER Compound Score",
    yaxis_title="Count",
    template="plotly_white"
)

textblob_fig = px.histogram(
    df, x="textblob_polarity", nbins=20, title="TextBlob Score Distribution",
    color_discrete_sequence=["#00CC96"]
)
textblob_fig.update_traces(
    marker_line_color="black", marker_line_width=1.5, opacity=0.75
)
textblob_fig.update_layout(
    bargap=0.1,
    xaxis_title="TextBlob Polarity",
    yaxis_title="Count",
    template="plotly_white"
)

# Define layout with Tabs
app.layout = html.Div([
    html.H1("Company Sentiment Analysis", style={"textAlign": "center"}),
    dcc.Tabs([
        dcc.Tab(label="Dashboard Overview", children=[
            html.Div([
                dcc.Graph(figure=rating_fig),
                dcc.Graph(figure=vader_fig),
                dcc.Graph(figure=textblob_fig)
            ])
        ]),
        dcc.Tab(label="Live Sentiment API", children=[
            html.Div([
                html.H3("Analyze New Feedback"),
                dcc.Input(id="input-text", type="text", placeholder="Enter feedback...", style={"width": "60%"}),
                html.Button("Analyze", id="analyze-btn", n_clicks=0),
                html.Div(id="sentiment-output", style={"marginTop": "20px"})
            ])
        ]),
        dcc.Tab(label="Company Filter", children=[
            html.Div([
                html.H3("Filter Sentiment by Company"),
                dcc.Dropdown(id="company-dropdown", options=company_options, placeholder="Select company"),
                dcc.Graph(id="company-vader-graph"),
                dcc.Graph(id="company-textblob-graph")
            ])
        ])
    ])
])

# Callback for live sentiment API
@app.callback(
    Output("sentiment-output", "children"),
    Input("analyze-btn", "n_clicks"),
    State("input-text", "value")
)
def analyze_text(n_clicks, text):
    if not text:
        return ""
    try:
        response = requests.post("http://sentiment_api:8081/predict", json={"text": text})
        result = response.json()
        return html.Div([
            html.P(f"Compound: {result['compound']:.3f}"),
            html.P(f"Positive: {result['positive']:.3f}"),
            html.P(f"Neutral: {result['neutral']:.3f}"),
            html.P(f"Negative: {result['negative']:.3f}"),
        ])
    except Exception as e:
        return f"API Error: {str(e)}"

@app.callback(
    [Output("company-vader-graph", "figure"),
     Output("company-textblob-graph", "figure")],
    Input("company-dropdown", "value")
)
def update_company_graphs(selected_company):
    if not selected_company:
        return {}, {}
    filtered = df[df["company"] == selected_company]

    fig_vader = px.histogram(
        filtered, x="vader_compound", nbins=20,
        title=f"VADER Sentiment - {selected_company}",
        color_discrete_sequence=["#EF553B"]
    )
    fig_vader.update_traces(marker_line_color="black", marker_line_width=1.5, opacity=0.75)
    fig_vader.update_layout(bargap=0.1, template="plotly_white")

    fig_rating = px.histogram(
        filtered, x="actual_sentiment_score", nbins=20,
        title=f"Rating - {selected_company}",
        color_discrete_sequence=["#636EFA"]
    )
    fig_rating.update_traces(marker_line_color="black", marker_line_width=1.5, opacity=0.75)
    fig_rating.update_layout(bargap=0.1, template="plotly_white")

    return fig_vader, fig_rating

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)


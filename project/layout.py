import dash_core_components as dcc
import plotly.express as px


def create_flood_graph(observed_df, forecast_df):
    
    x=forecast_df['Time'],
    y=forecast_df['Level'],
    print(x, y)
    x=observed_df['Time'],
    y=observed_df['Level'],
    print(x, y)
    return dcc.Graph(
        figure=dict(
            data=[
                dict(
                    x=observed_df['Time'],
                    y=observed_df['Level'],
                    name='Observed',
                    marker=dict(
                        color='rgb(55, 83, 109)'
                    ),
                ),
                dict(
                    x=forecast_df['Time'],
                    y=forecast_df['Level'],
                    name='Forecast',
                    marker=dict(
                        color='rgb(26, 118, 255)'
                    )
                )
            ],
            layout=dict(
                title='US Export of Plastic Scrap',
                showlegend=True,
                legend=dict(
                    x=0,
                    y=1.0
                ),
                margin=dict(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 300},
        id='my-graph'
    )  


def create_flood_interval(frequency_secs):
    return dcc.Interval(
            id='interval-component',
            interval= frequency_secs * 1000,
            n_intervals= 0
        )
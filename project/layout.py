import dash_core_components as dcc
import dash_html_components as html




def create_flood_graph():
    return  html.Div(className='row', children=[html.Div(dcc.Graph(id='flood-graph', animate=False), className='')])


def create_flood_interval(frequency_secs):
    return dcc.Interval(
            id='flood-update-interval',
            interval= frequency_secs * 1000,
            n_intervals= 0
        )
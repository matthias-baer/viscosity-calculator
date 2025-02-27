import numpy as np

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State


# Initialise the app
app = dash.Dash(__name__)

server = app.server

# Design the dashboard
app.layout = html.Div(children=[
                  html.Div(className='row',  # Define the row element
                           children=[
                           # Add max planck logo
                           html.Img(src="assets/logo.svg",  width=300,
                                    style={'display' : 'inline-block',
                                           'padding-top': '20px',
                                           'padding-left': '40px'
                                            }),
                           # Add reference github link
                           html.A("Edit on GitHub",
                                  href='https://github.com/bbueyue/viscosity'
                                       '-calculator',
                                  target="_blank",
                                  style={'display' : 'inline-block',
                                         'float' : 'right',
                                         'font-size': '15px',
                                         'color' : '#017b70',
                                         'padding-top': '30px',
                                         'padding-right': '40px'
                                         }),
                           html.Div(style={'text-align':'center'},
                                    children=[
                                        # App title
                                        html.P('RT-DC Buffers Viscosity '
                                               'Calculator',
                                               style={'font-size': '22px',
                                                      'text-align':'center',
                                                      'padding-bottom': '10px'
                                                     }),
                                        # html.Br(), Dropdown menu component
                                        # (title and design)
                                        html.Div([
                                              html.H2('Medium',
                                                      style={'font-size': '14px'
                                                             }),
                                              dcc.Dropdown(id="medium",
                                                           searchable=True,
                                                           placeholder='Select a medium',
                                                           options=[
                                                           {'label': '0.5% MC-PBS', 'value': '1'},
                                                           {'label': '0.6% MC-PBS', 'value': '2'},
                                                           {'label': '0.84% MC-PBS', 'value': '3'}
                                                                    ],
                                                           style={'width': '250px',
                                                                  'height' : '35px',
                                                                  'color': 'blue',
                                                                  'display' : 'inline-block'
                                                                  })
                                                  ]),
                                        # Temperature input box component
                                        # (title and design)
                                        html.Div([
                                              html.H2('Temperature [°C]',
                                                      style={'font-size': '14px'
                                                            }),
                                              dcc.Input(id="temperature",
                                                        type='text',
                                                        persistence = False,
                                                        placeholder='Enter the temperature...',
                                                        style={'width': '250px',
                                                               'height' : '35px'
                                                               })
                                                 ]),
                                        # Channel size input box component
                                        # (title and design)
                                        html.Div([
                                              html.H2('Channel size [μm]',
                                                      style={'font-size': '14px'
                                                               }),
                                              dcc.Input(id="channel_size",
                                                        type='text',
                                                        persistence = False,
                                                        placeholder='Enter the channel size...',
                                                        style={'width': '250px',
                                                               'height' : '35px'
                                                               })
                                                 ]),
                                        # Flow rate input box component
                                        # (title and design)
                                        html.Div([
                                              html.H2('Flowrate [μl/s]',
                                                      style={'font-size': '14px'
                                                               }),
                                              dcc.Input(id="flow_rate",
                                                        type='text',
                                                        persistence = False,
                                                        placeholder='Enter the flow-rate...',
                                                        style={'width': '250px',
                                                               'height' : '35px'
                                                               })
                                                 ]),
                                        html.Br(), 
                                        # Store component for input storage
                                        dcc.Store(id='store_viscosity'),
                                        # Submit button design 
                                        html.Button('Submit',
                                                    id='submit_button',
                                                    n_clicks=0, disabled=False,
                                                    style={'font-size': '12px',
                                                           'cursor': 'pointer',
                                                           'text-align': 'center',
                                                           'color': 'white',
                                                            }),
                                        html.Br(), html.Br(), 
                                        # Output component to display viscosity
                                        html.Div(id='show_viscosity',
                                                 style={'whiteSpace': 'pre-line',
                                                        'font-size': '20px'
                                                        })
                                  ]),
                          ]) # row Div
                    ]) # main Div


# Function to compute the viscosity value
# based on user given input
def compute_viscosity(float_feats):
    medium, temp, chsize, flwrate = float_feats
    if medium == 1.0:
        n_MC0X = 0.0026*temp + 0.590
        k_MC0X = 0.05*np.exp(35*(1/temp))
    if medium == 2.0:
        n_MC0X = 0.0024*temp + 0.529
        k_MC0X = 0.15*np.exp(27.8*(1/temp))
    if medium == 3.0:
        n_MC0X = 0.0021*temp + 0.467
        k_MC0X = 0.40*np.exp(30.6*(1/temp))
    shear_rate = 8*flwrate/((chsize*1e-3)**3)*(0.6671+0.2121/n_MC0X)
    viscosity = k_MC0X*(shear_rate**(n_MC0X - 1))*1000
    viscosity = round(viscosity, 3)
    return viscosity


# This callback function takes the inputs from
# the html components (see the id's), compute 
# the viscosity and store it in dcc.Store 
# component as s dictionary.
@app.callback(
    Output("store_viscosity", "data"),
   [Input("medium", "value"),
    Input("temperature", "value"),
    Input("channel_size", "value"),
    Input("flow_rate", "value")])
def store_viscosity(medium, temperature, channel_size, flow_rate):
    # dashboard inputs from users are of string type
    string_feats = [medium, temperature, channel_size, flow_rate]
    if len(string_feats) != 4 or None in string_feats or '' in string_feats:
        return None
    # Convert string inputs into float
    float_feats = list(map(float, string_feats))
    viscosity = compute_viscosity(float_feats)
    return {'viscosity' : viscosity}


# This call back function is activated when 
# user click on submit button. When do so, stored
# viscosity value will be displayed in the output
# component
@app.callback(
    Output('show_viscosity', 'children'),
    Input('submit_button', 'n_clicks'),
    State('store_viscosity', 'data'))
def display_output(n_clicks, stored_viscosity):
    trigger = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if stored_viscosity is not None:
        viscosity = stored_viscosity['viscosity']
        if 'submit_button' in trigger:
            return 'Computed viscosity [mPa.s]: \n{}'.format(viscosity)
        else:
            return dash.no_update
    else:
        return dash.no_update
    

# This call back function will reset the input boxes
# as soon as user click on the submit button
@app.callback(
   [Output("temperature", "value"),
    Output("channel_size", "value"),
    Output("flow_rate", "value")],
     Input('submit_button', 'n_clicks'))
def reset_inputs(click):
    trigger = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'submit_button' in trigger:
        return ['']*3
    else:
        return dash.no_update


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)

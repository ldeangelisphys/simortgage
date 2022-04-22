from msilib.schema import Complus
from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input,Output

app = Dash(__name__)

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options


def visualize_mortgages(capital,ir,years):
    n = years*12
    mir = ir/12

    M = {'FR':{},'IT':{}}
    k = 'FR'
    r = capital*mir/(1- (1/(1+mir)**n))
    M[k]['R'] = np.ones(n)*r
    M[k]['C'],M[k]['P'],M[k]['I'] = [],[],[]
    left = capital
    for i in range(n):    
        interest = left*mir
        payment  = r - interest
        left = left - payment
        
        M[k]['P'].append(payment)
        M[k]['I'].append(interest)
        M[k]['C'].append(left)
        
    M[k]['P'] = np.array(M[k]['P'])
    M[k]['I'] = np.array(M[k]['I'])
    M[k]['C'] = np.array(M[k]['C'])

    k = 'IT'
    p = capital / n
    M[k]['P'] = np.ones(n)*p
    M[k]['C'],M[k]['R'],M[k]['I'] = [],[],[]
    left = capital
    for i in range(n):    
        interest = left*mir
        left = left - p
        
        M[k]['R'].append(p + interest)
        M[k]['I'].append(interest)
        M[k]['C'].append(left)
        
    M[k]['R'] = np.array(M[k]['R'])
    M[k]['I'] = np.array(M[k]['I'])
    M[k]['C'] = np.array(M[k]['C'])


    df = pd.DataFrame(M['FR']).merge(pd.DataFrame(M['IT']),left_index=True,right_index=True,suffixes=('_FR','_IT'))
    df['Month'] = np.arange(len(df))+1
    M = (int((df['I_IT']+df['P_IT'])[0]/100)+1)*100


    figs = {}

    for k in ['FR','IT']:

        fig = px.area(df, x="Month", y=f"P_{k}",color_discrete_sequence=['blue'],
                    labels={f"P_{k}": "Total monthly payment (€)", "Month": "# Month"}, title=f'{k} Mortgage')
        temp_fig = px.area(df, x="Month", y=f"I_{k}",color_discrete_sequence=['orange']) 
        fig.add_trace(temp_fig.data[0])
        fig['data'][0]['showlegend']=True
        fig['data'][0]['name']='Repayments'
        fig['data'][1]['showlegend']=True
        fig['data'][1]['name']='Interest costs'
        fig.update_layout(yaxis_range=[0,M])

        figs[k] = fig

    return figs

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Dash: A web application framework for your data.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.Div([
        dcc.Input(
            type='number',
            id='capital',
            value=60000
        ),
        dcc.Input(
            type='number',
            id='interest-rate',
            value=2.3
        ),
        dcc.Slider(
            6,40,1,
            marks={n:str(n) for n in [6]+[i for i in range(10,41,5)]},
            value=20,
            id='years',
        )
    ],
        style={'width': '49%', 'display': 'inline-block'}
    ),

    html.Div(id='data-summary', style={'margin-top': 20}),



    html.Div(children=[
        dcc.Graph(
            id='vis-annuity',
            style={'display': 'inline-block','width': '90vh', 'height': '60vh'}
        ),
        dcc.Graph(
            id='vis-linear',
            style={'display': 'inline-block','width': '90vh', 'height': '60vh'}
        )
    ])

])



@app.callback(
    [Output('data-summary', 'children'),Output('vis-annuity','figure'),Output('vis-linear','figure')],
    Input('capital', 'value'),
    Input('interest-rate', 'value'),
    Input('years', 'value'))
def update_output(capital,ir,years):

    text =  f'Results for a {years} years mortgage ({12*years} months) for capital of {capital} euros, with a {ir:.2f}% interest rate.'
    figs = visualize_mortgages(capital,ir/100,years)

    return text,figs['FR'],figs['IT']

if __name__ == '__main__':
    app.run_server(debug=True)
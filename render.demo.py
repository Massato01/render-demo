import pandas as pd
import pandas_gbq
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# ---------------------- PEGA DADOS DO BIGQUERY ----------------------
def get_query():
    return """
    # select * from `snowflake.tbl_pedidos`;
    select nk_order_id, creation_time, payment.paid_value, status.normalized.code from `fact_layer.order` where creation_time >= '2024-01-01'
    # select nk_order_id, creation_time, payment.paid_value, status.normalized.code from `fact_layer.order` where creation_time >= '2024-01-01' and payment.is_paid and status.normalized.code = 'CANCELADO';
    """

df = pd.DataFrame(
    pandas_gbq.read_gbq(query_or_table=get_query(), project_id='bi-bbrands', dialect='standard')
    )

# ---------------------- INICIALIZA DASHBOARD ----------------------
# Inicializar o app Dash
app = dash.Dash(__name__)

# Layout do dashboard
app.layout = html.Div(children=[
    html.H1(children='TESTE DASH PYTHON'),
    html.Div(children='''Dados do fact_layer.orer'''),

    dcc.Graph(
        id='graph1'
    ),

    dcc.Graph(
        id='graph2'
    ),

    dash_table.DataTable(
        id='data-table',
        columns=[
            {'name': i, 'id': i} for i in df.columns
        ],
        data=df.to_dict('records'),
        export_format='xlsx',
        page_size=10,
    )
])

df_vendas = df.copy()
df_vendas['creation_time'] = pd.to_datetime(df_vendas['creation_time'])
df_vendas['nome_mes'] = df_vendas['creation_time'].dt.strftime('%B')
df_vendas_soma = pd.DataFrame(df_vendas.groupby('nome_mes')['paid_value'].sum()).reset_index()
df_vendas_soma.columns = ['nome_mes', 'soma_paga']

df_status = df.copy()
df_status = pd.DataFrame(df_status.groupby('code')['nk_order_id'].count()).reset_index()
df_status.columns = ['status', 'quantidade']

# Função para atualizar os gráficos
@app.callback(
    Output('graph1', 'figure'),
    Output('graph2', 'figure'),
    Input('graph1', 'id')
)
def update_graphs(_):
    fig1 = px.line(df_vendas_soma, x='nome_mes', y='soma_paga', title='Evolução pedidos')
    fig2 = px.bar(df_status, x='status', y='quantidade', title='Qtd. status')
    return fig1, fig2

# Executar o servidor do Dash
if __name__ == '__main__':
    app.run_server(debug=True)
import dash
from dash.dependencies import Input, Output, State, ALL
from dash import dcc 
from dash import html
import os
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from random import randint
import dash_daq as daq
from dash.exceptions import PreventUpdate


#Adresy
typ_nr = {1: '1_Główny', 2: '2_Podrzędny', 4: '4_LEP old', 5: '5_LEP new', 6: '6_LEP indigo', 8: '8_Lasy_Państwowe',
          9: '9_Nie do AM'}
relacja_pe = {0: "0_nieznane", 25: "Relacja z pesel", 23: "relacja z pesel - adres zmieniony",
              1: "1_budynek mieszkalny_pesel", 2: "2_budynek_usługowy_inne_zrodlo",
              3: "3_budynek mieszany_pesel", 4: "4_budynek_mieszkalny_inne_źródło",
              5: "5_budynek_mieszany_inne_źródło", 6: "6_budynek_mieszkalny_operator",
              7: "7_budynek_usługowy_operator", 8: "8_budynek_mieszany_operator"}
#Drogi
opis = {1:'01_Główna',2:'02_Główna_2',3:'03_Drugorzędna',4:'04_Drugorzędna_2',5:'05_Utwardzona',6:'06_Utwardzona2',7:'07_Miejska',8:'08_Miejska_gorsza', 9:'09_Gruntowa_utrzymana', 10:'10_Gruntowa_nieutrzymana(wiejska)',11:'11_Terenowa',
        12:'12_Wewnętrzna', 13: '13_Piesza', 14:'14_ścieżka_rowerowa', 15: '15_Ciąg_pieszo-rowerowy'}
oneway = {0:'0', 1: 'jednokierunkowa', 3:'jednokierunkowa nie dot. rowerów'}
zakazy = {0:'0', 3: '3_Zakaz_B1', 4: '4_Blokada_fizyczna', 6:'6_Blokada_przejazdu', 7: '7_Droga_prywatna', 97:'97_Droga_w_budowie', 98: '98_Droga_projektowana',
           9: '9_Blokada_końca_nawigacji'}
przejazdy =  {0:'0', 1: "01_podw.ciągła + początek",2: "02_podw.ciągła + koniec",3: "03_podw.ciągła + oba końce",4: "04_podw.ciągła tylko segment",
    11: "11_ciągła zgodnie + początek",12: "12_ciągła zgodnie + koniec",13: "13_ciągła zgodnie + oba końce",14: "14_ciągła zgodnie tylko segment",
    21: "21_ciągła odwrotnie + początek",22: "22_ciągła odwrotnie + koniec",23: "23_ciągła odwrotnie + oba końce",24: "24_ciągła odwrotnie tylko segment",
    31: "31_blokada_fizyczna + początek",32: "32_blokada_fizyczna + koniec",33: "33_blokada_fizyczna + oba końce",34: "34_blokada_fizyczna tylko segment"}

lights = {0: '0', 1: '1_na_początku_wektora', 2: '2_na_końcu_wektora', 3: '3_na_obu_końcach_wektora'}
lep = {0: "0",1: "1_LEP old",2: "2_LEP new",3: "3_LEP indigo",4: "4_LEP indigo 2110",9: "9_drogi leśne"}

#entry_points
_type = {"All": "Dojazd dla wszystkich","Dostawcy": "Dojazd dla dostawców","Kurierzy": "Dojazd dla kurierów","Uprzywilejowane": "Dojazd tylko dla pojazdów uprzywilejowanych (np. dojazd dla karetek)",
"Taxi": "Dojazd dla taxi","Vip": "Dojazd tylko dla pojazdów z przepustką/zezwoleniem/abonamentem"}

#konce
status = {0: "0_Nowy_koniec",1: "1_Zatwierdzony_koniec",2: "2_Przestał_być_końcem"}
end_type = { 0: "0_międzynarodowe",1: "1_główne_i_autostrady",2: "2_drugorzędne",3: "3_numerowane",4: "4_koniec_eski_lub_autostrady"}

#miejscowowsci
typ_gus = {0: "Część miejscowości",98: "Delegatura",99: "Część miasta",95: "Dzielnica m. st. Warszawy",2: "Kolonia",96: "Miasto",4: "Osada",5: "Osada leśna",
    6: "Osiedle",3: "Przysiółek",7: "Schronisko turystyczne",1: "Wieś",100: "Miejscowość historyczna"}

#crossing_road
status_road = {0: "0_nowe_przecięcie",1: "1_zatwierdzone_przecięcie",2: "2_było_kiedyś_przecięciem",3: "3_do_usunięcia",4: "4_weryfikacja_tymczasowa"}
poziom = {0: "0_ten_sam_poziom",1: "1_różny_poziom"}




slowniki = {'typ_nr': typ_nr, 'relacja_pe': relacja_pe, 'opis': opis, 'oneway': oneway, 'zakazy':zakazy, 'przejazdy':przejazdy, 'lights':lights, 'lep':lep, '_type':_type,
            'end_type':end_type, 'typ_gus': typ_gus, 'poziom':poziom}

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

container_style = {
    'margin': '10px',
    'display': 'flex',
    'flex-direction': 'column'
}

color_mapping = {}
gdf = None
full_path = None  

app.layout = html.Div(style={'backgroundColor': '#f2f2f2'}, children=[
    html.Div([
        dcc.Input(
            id='folder-path-input',
            type='text',
            placeholder='Wprowadź ścieżkę do folderu',
            style={'width': '100%', 'margin': '10px'}
        ),
        dcc.Upload(
            id='upload-shp',
            children=html.Div([
                'Przeciągnij plik SHP lub ',
                html.A('kliknij tutaj')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'inset',
                'borderRadius': '5px',
                'textAlign': 'center',
                'font-family': 'Lucida Sans Unicode, sans-serif',
                'margin': '10px',
                'backgroundColor': 'white',
                'color': 'black',
                'borderColor': '#cccccc',
            },
            accept='.shp'
        ),
        html.Div(id='output-data-upload')
    ], style=container_style),
    html.Div([
        dcc.Dropdown(
            id='column-dropdown',
            options=[],
            placeholder="Wybierz atrybut",
            style={'width': '300px', 'margin': '10px'}
        ),
        html.Div(id='selected-column-values', style={'margin': '10px'}),
    ], style=container_style),
    html.Div([
        html.Div(id='map-output-container', style={'position': 'relative'}),
        html.Div([
            html.Button('Zmiana koloru', id='change-button', n_clicks=0,
                        style={'margin': '5px', 'width': '500px', 'height': '60px', 'border-radius': '40%',
                               'background-color': '#800020', 'color': 'white', 'border': 'none',
                               'display': 'inline-block', 'font-weight': 'bold'}),
            html.A(html.Button('Reset',id='reset-button', n_clicks=0, style={'margin': '5px', 'width': '60px', 'height': '60px',
                                                'border-radius': '40%', 'background-color': '#800020', 'color': 'white',
                                                'border': 'none', 'display': 'inline-block', 'font-weight': 'bold'}),
                   href='/'),
            html.Div(id='new-content',
                     style={'backgroundColor': 'white', 'position': 'relative', 'width': '250px', 'zIndex': '1000'}),
            html.Button("Zamknij", id="close-change-color-button", n_clicks=0,
                        style={'position': 'absolute', 'top': '90px', 'right': '10px', 'display': 'none'})
        ], style={'position': 'absolute', 'right': '300px', 'top': '150px', 'width': '140px', 'display': 'flex',
                  'align-items': 'center', 'justify-content': 'space-between'})
    ], style=container_style)
])


def display_selected_column_values(selected_column):
    global gdf
    if selected_column and gdf is not None:
        values = gdf[selected_column].unique()
        return values.tolist() if values is not None else []
    else:
        return []


@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-shp', 'contents')],
    [State('upload-shp', 'filename'),
     State('folder-path-input', 'value')]
)
def display_shp(contents, filename, folder_path):
    global full_path
    if contents is not None:
        file_name = os.path.basename(filename)
        print("Nazwa pliku SHP:", file_name)
        full_path = os.path.join(folder_path, file_name)
        return html.Div(
            f'Załadowano plik: {file_name}',
            style={
                'position': 'absolute',
                'top': '80px',
                'left': '50px',
                'font-family': 'Verdana, sans-serif',
                'font-size': '11px',
                'font-style': 'italic',
                'color': '#6699ff',
            }
        )
    else:
        return None


@app.callback(
    Output('map-output-container', 'children'),
    [Input('upload-shp', 'contents'),
     Input('column-dropdown', 'value'),
     Input({'type': 'color-picker', 'index': ALL}, 'value')],
    [State('upload-shp', 'filename'),
     State({'type': 'color-picker', 'index': ALL}, 'id'),
     State('map-output-container', 'children'),
     State('folder-path-input', 'value')]
)
def update_map(contents, selected_column, color_hex_values, filename, color_picker_ids, current_map_children,
               folder_path):
    global color_mapping
    global gdf
    global full_path

    etykieta = None

    if contents is not None and selected_column is not None:
        full_path = os.path.join(folder_path, filename)
        if gdf is None:
            gdf = gpd.read_file(full_path)
            gdf = gdf.to_crs(epsg=4326)

        center_lat = gdf.geometry.centroid.y.mean()
        center_lon = gdf.geometry.centroid.x.mean()

        m = folium.Map(location=[center_lat, center_lon], zoom_start=16, tiles='Cartodb Positron')

        marker_cluster = MarkerCluster(disable_clustering_at_zoom=11).add_to(m)

        if color_hex_values is not None:
            color_hex_values = [color['hex'] for color in color_hex_values if color is not None]

        if color_hex_values:
            for color, picker_id in zip(color_hex_values, color_picker_ids):
                value = picker_id['index']
                color_mapping[value] = color
        else:
            color_mapping = {value: f'#{randint(0, 0xFFFFFF):06x}' for value in gdf[selected_column].unique()}

        for idx, row in gdf.iterrows():
            geom = row.geometry
            value = row[selected_column] if selected_column else None

            if selected_column in slowniki:
                etykieta = slowniki[selected_column]
                if 'crossing' in filename and etykieta == status:
                    etykieta = status_road

            color = color_mapping.get(row[selected_column], 'blue')
            if geom.geom_type == 'MultiPoint':
                for point in geom.geoms:
                    folium.CircleMarker(location=[point.y, point.x], radius=5, color=color, fill=True,
                                        fill_color=color,
                                        name=str(value)).add_to(marker_cluster)
            elif geom.geom_type == 'Point':
                folium.CircleMarker(location=[geom.y, geom.x], radius=5, color=color, fill=True,
                                    fill_color=color,
                                    name=str(value)).add_to(marker_cluster)
            elif geom.geom_type == 'LineString':
                folium.PolyLine(locations=[(point[1], point[0]) for point in geom.coords], color=color).add_to(m)

        legend_table_rows = []
        if etykieta:
            legend_table_rows.extend([html.Tr([html.Th("Legenda")])])
            legend_table_rows.extend(
                [html.Tr([html.Td(etykieta.get(value, value)),
                          html.Td(style={"background-color": color, "width": "30px", "height": "20px"})]) for
                 value, color in color_mapping.items()])
        else:
            legend_table_rows.extend([html.Tr([html.Th("Legenda")])])
            legend_table_rows.extend(
                [html.Tr([html.Td(value),
                          html.Td(style={"background-color": color, "width": "30px", "height": "20px"})]) for
                 value, color in color_mapping.items()])
        legend_table = html.Table(legend_table_rows,
                                  style={"background-color": "white", "border": "1px solid black", "padding": "10px",
                                         "border-radius": "5px"})
        legend_div = html.Div(legend_table,
                              style={'position': 'absolute', 'top': '10px', 'right': '10px', 'zIndex': 1000})
        map_with_legend = html.Div(
            [html.Iframe(id='map', srcDoc=m.get_root().render(), style={'width': '100%', 'height': '650px'}),
             legend_div])

        return map_with_legend
    elif current_map_children:
        return current_map_children
    else:
        return None


@app.callback(
    Output('column-dropdown', 'options'),
    [Input('upload-shp', 'contents'),
     Input('reset-button', 'n_clicks')],  
    [State('upload-shp', 'filename'),
     State('folder-path-input', 'value'),
     State('column-dropdown', 'options'),
     State('upload-shp', 'last_modified')]  
)
def update_column_dropdown(contents, reset_clicks, filename, folder_path, previous_options, last_modified):
    global gdf
    global full_path

    changed_shp = False
    if filename and last_modified:
        current_full_path = os.path.join(folder_path, filename)
        if current_full_path != full_path:
            changed_shp = True
            full_path = current_full_path

    if contents is not None:
        if gdf is None or reset_clicks or changed_shp:  
            gdf = gpd.read_file(full_path)
            print(full_path)
            gdf = gdf.to_crs(epsg=4326)

        columns = gdf.columns.tolist()
        return [{'label': col, 'value': col} for col in columns]
    else:
        return previous_options or []



@app.callback(
    Output('new-content', 'children'),
    [Input('change-button', 'n_clicks'),
     Input({'type': 'color-picker', 'index': ALL}, 'value'),
     Input('close-change-color-button', 'n_clicks')],
    [State('column-dropdown', 'value'),
     State('upload-shp', 'filename'),
     State({'type': 'color-square', 'index': ALL}, 'id'),
     State('new-content', 'children'),
     State('folder-path-input', 'value')]
)
def update_content_and_color(n_clicks, color_values, close_clicks, selected_column, filename, square_ids,
                             current_children, folder_path):
    global color_mapping
    global gdf
    global full_path

    if color_values is not None and dash.callback_context.triggered[0]['prop_id'] != 'change-button.n_clicks':
        color_hex_values = [color['hex'] for color in color_values]
        for color, picker_id in zip(color_hex_values, square_ids):
            value = picker_id['index']
            color_mapping[value] = color

    if close_clicks:
        return None

    if n_clicks:
        if selected_column and filename:
            if gdf is None:
                full_path = os.path.join(folder_path, filename)
                gdf = gpd.read_file(full_path)
                gdf = gdf.to_crs(epsg=4326)

            selected_column_values = display_selected_column_values(selected_column)
            unique_values_html = []

            for value in selected_column_values:
                color_square = html.Div(
                    style={
                        'background-color': color_mapping.get(value, '#000000'),
                        'width': '20px',
                        'height': '20px',
                        'border': '1px solid black',
                        'margin-right': '10px',
                        'margin-bottom': '10px',
                        'margin-left': '10px'
                    },
                    id={'type': 'color-square', 'index': value}
                )
                color_picker = daq.ColorPicker(
                    id={'type': 'color-picker', 'index': value},
                    value=dict(hex=color_mapping.get(value, '#000000')),
                    style={'height': '200px', 'margin-left': '0px', 'margin-right': '50px', 'margin-bottom': '50px'}
                )
                value_with_square = html.Div(
                    [color_square, value, color_picker],
                    style={'margin-left': '10px'}
                )
                unique_values_html.append(value_with_square)

            return html.Div(
                [html.Button("Zamknij", id="close-change-color-button", n_clicks=0,
                             style={'position': 'absolute', 'top': '10px', 'right': '10px'}),
                 *unique_values_html])
    raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1', port = 8050)

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
import zipfile
import tempfile
from io import BytesIO
import base64

def display_selected_column_values(selected_column):
    global gdf
    if selected_column and gdf is not None:
        values = gdf[selected_column].unique()
        return values.tolist() if values is not None else []
    else:
        return []
    
def load_data_from_zip(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            with zipfile.ZipFile(BytesIO(decoded)) as zip_file:
                temp_dir = tempfile.mkdtemp()
                zip_file.extractall(temp_dir)
                shp_files = [file for file in os.listdir(temp_dir) if file.endswith('.shp')]
                if shp_files:
                    gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
                    return gdf
        except Exception as e:
            return None
    else:
        return None

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

# Inicjalizacja aplikacji Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Styl kontenera
container_style = {
    'margin': '10px',
    'display': 'flex',
    'flex-direction': 'column'
}

color_mapping = {}
gdf = None
full_path = None  

# Rozkład interfejsu użytkownika
app.layout = html.Div(style={'backgroundColor': '#f2f2f2'}, children=[
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Przeciągnij i upuść lub ',
                html.A('wybierz plik ZIP z SHP')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Wielokrotne przesyłanie plików jest dozwolone
            multiple=False
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
                     style={'backgroundColor': 'white', 'position': 'relative', 'width': '250px', 'zIndex': '1000','display': 'None'}),
            html.Button("Zamknij", id="close-change-color-button", n_clicks=0,
                        style={'position': 'absolute', 'top': '90px', 'right': '10px', 'display': 'none'})
        ], style={'position': 'absolute', 'right': '300px', 'top': '90px', 'width': '140px', 'display': 'flex',
                  'align-items': 'center', 'justify-content': 'space-between'})
    ], style=container_style)
])


@app.callback(
    Output('new-content', 'style'),
    [Input('change-button', 'n_clicks')],
    [State('new-content', 'style')]
)
def update_content_visibility(n_clicks, current_style):
    if n_clicks:
        current_style['display'] = 'block'
    else:
        current_style['display'] = 'none'
    return current_style

@app.callback(
    Output('column-dropdown', 'options'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_column_dropdown_options(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            with zipfile.ZipFile(BytesIO(decoded)) as zip_file:
                temp_dir = tempfile.mkdtemp()
                zip_file.extractall(temp_dir)
                shp_files = [file for file in os.listdir(temp_dir) if file.endswith('.shp')]
                if shp_files:
                    gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
                    column_names = gdf.columns.tolist()
                    # Zwróć opcje dla listy rozwijanej, gdzie label i value będą takie same (nazwy kolumn)
                    return [{'label': col, 'value': col} for col in column_names]
                else:
                    return [{'label': 'Brak pliku SHP w archiwum ZIP', 'value': ''}]
        except Exception as e:
            return [{'label': 'Wystąpił błąd podczas przetwarzania pliku', 'value': ''}]
    else:
        return []

    
@app.callback(
    Output('map-output-container', 'children'),
    [Input('upload-data', 'contents'),
     Input('column-dropdown', 'value'),
     Input({'type': 'color-picker', 'index': ALL}, 'value')],
    [State('upload-data', 'filename'),
     State({'type': 'color-picker', 'index': ALL}, 'id'),
     State('map-output-container', 'children')]
)
def update_map(contents, selected_column, color_hex_values, filename, color_picker_ids, current_map_children):
    global color_mapping
    global gdf

    etykieta = None

    if contents is not None and selected_column is not None:
        gdf = load_data_from_zip(contents, filename)

        if gdf is not None:
            gdf = gdf.to_crs(epsg=4326)  # Konwersja do odwzorowania EPSG 3857

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
    Output('new-content', 'children'),
    [Input('change-button', 'n_clicks'),
     Input({'type': 'color-picker', 'index': ALL}, 'value'),
     Input('close-change-color-button', 'n_clicks')],
    [State('column-dropdown', 'value'),
     State('upload-data', 'contents'),
     State('upload-data', 'filename'),
     State({'type': 'color-square', 'index': ALL}, 'id'),
     State({'type': 'color-picker', 'index': ALL}, 'id'),
     State('new-content', 'children')]
)
def update_content_and_color(n_clicks, color_values, close_clicks, selected_column, contents, filename, square_ids,
                             color_picker_ids, current_children):
    global color_mapping
    global gdf

    if color_values is not None and dash.callback_context.triggered[0]['prop_id'] != 'change-button.n_clicks':
        color_hex_values = [color['hex'] for color in color_values]
        for color, picker_id in zip(color_hex_values, color_picker_ids):
            value = picker_id['index']
            color_mapping[value] = color

    if close_clicks:
        return None

    if n_clicks:
        if selected_column and contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            try:
                with zipfile.ZipFile(BytesIO(decoded)) as zip_file:
                    temp_dir = tempfile.mkdtemp()
                    zip_file.extractall(temp_dir)
                    shp_files = [file for file in os.listdir(temp_dir) if file.endswith('.shp')]
                    if shp_files:
                        gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
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
            except Exception as e:
                return html.Div([
                    'Wystąpił błąd podczas przetwarzania tego pliku.'
                ])
    raise PreventUpdate



if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8050)

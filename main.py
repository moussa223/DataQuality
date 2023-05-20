import folium
import pandas as pd
from flask import Flask
from folium.plugins import MarkerCluster

app = Flask(__name__)

@app.route("/")
def tan_map():
    # Importation des différents csv avec uniquement les colonnes intéréssantes.
    stops = pd.read_csv("data/stops.csv", sep = ',')
    shapes = pd.read_csv('data/shapes.csv', usecols=['shape_id', 'shape_pt_lat', 'shape_pt_lon'])
    trips = pd.read_csv("data/trips.csv", sep=',', usecols=['trip_id', 'route_id', 'shape_id', 'direction_id'])
    routes = pd.read_csv("data/routes.csv", sep=',', usecols=['route_id', 'route_type', 'route_color'])
    stop_times = pd.read_csv("data/stop_times.csv", sep=',', usecols=['stop_id', 'trip_id'])
    direction_ids = dict(zip(trips['shape_id'].astype(str), trips['direction_id']))
    route_colors = dict(zip(routes['route_id'].astype(str), routes['route_color']))
    route_id_type = routes.loc[:, ['route_id', 'route_type']]

    map = folium.Map(location=[47.2184, -1.5536], zoom_start=12, tiles='cartodbdark_matter')

    marker_cluster = MarkerCluster(name='Markers').add_to(map)
    line_cluster = MarkerCluster(name='Lines').add_to(map)

    
    # Jointure des données pour obtenir les informations nécessaires sur les arrêts enfants et parents
    merged_stops = pd.merge(stop_times, stops, on='stop_id', how='right')
    merged_stops = pd.merge(merged_stops, trips, on='trip_id', how='left')
    merged_stops = pd.merge(merged_stops, routes, on='route_id', how='left')

    # Création d'une nouvelle colonne pour stocker les IDs des arrêts parents correspondants aux arrêts enfants
    merged_stops['parent_station'] = merged_stops['stop_id'].map(stops.set_index('stop_id')['parent_station'])

    # Filtrage des lignes représentant les arrêts parents
    parent_stops_merged = merged_stops[merged_stops['parent_station'].notnull()]

    # Supprimer les doublons en conservant uniquement la première occurrence de chaque arrêt
    unique_stops = parent_stops_merged.drop_duplicates(subset='parent_station', keep='first')

    for index, stop in unique_stops.iterrows():
        if stop['route_type'] in [0, 3, 4]:
            icon = 'train' if stop['route_type'] == 0 else 'bus' if stop['route_type'] == 3 else 'ship'
            color = 'red' if icon == 'train' else 'lightgray' if icon == 'bus' else 'blue'

            if stop['wheelchair_boarding'] == 1:
                html = "<b>"+stop['stop_name']+"</b><br>Accessible aux personnes Handicapées"
            else:
                html = "<b>"+stop['stop_name']+"</b><br>"
            iframe = folium.IFrame(html=html, width=200, height=100)
            folium.Marker(location=[stop['stop_lat'], stop['stop_lon']],
                        popup=folium.Popup(iframe),
                        icon=folium.Icon(color=color, icon=icon, prefix='fa')
                        ).add_to(marker_cluster)

    for shape_id, group in shapes.groupby('shape_id'):
        points = group[['shape_pt_lat', 'shape_pt_lon']].values.tolist()

        if str(shape_id) in direction_ids and direction_ids[str(shape_id)] == 0:
            if str(shape_id) in trips['shape_id'].astype(str).values:
                trip = trips.loc[trips['shape_id'].astype(str) == str(shape_id)].iloc[0]
                route_id = trip['route_id']
                if str(route_id) in route_colors:
                    route_color = route_colors[str(route_id)]



                    folium.PolyLine(locations=points, color="#"+route_color).add_to(line_cluster)
    
    folium.LayerControl().add_to(map)

    map.save('index.html')
    return map.get_root().render()



if __name__ == "__main__":
    app.run()

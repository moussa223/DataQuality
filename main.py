import json
import folium
import pandas as pd
from flask import Flask
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster


app = Flask(__name__)

@app.route("/")
def home():

    #Lectures du fichier JSON 
    with open('clear_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    map = folium.Map(location=[47.2184, -1.5536], zoom_start=12, tiles='cartodbdark_matter')
    
    #Lectures des fichiers CSV 
    routes = pd.read_csv("data/routes.csv", sep=',', usecols=['route_id', 'route_type', 'route_color', 'route_short_name', "route_text_color"])
    route_colors = dict(zip(routes['route_id'].astype(str), routes['route_color']))
    trips = pd.read_csv("data/trips.csv", sep=',', usecols=['trip_id', 'route_id', 'shape_id', 'direction_id'])
    shapes = pd.read_csv('data/shapes.csv', usecols=['shape_id', 'shape_pt_lat', 'shape_pt_lon'])
    direction_ids = dict(zip(trips['shape_id'].astype(str), trips['direction_id']))
    
    #Definition des clusters (groupes de lignes ou de points)
    #Markers
    marker_default_cluster = FastMarkerCluster(name='Markers', data=[], control=False).add_to(map)
    marker_train_cluster = FastMarkerCluster(name='Markers - Tram', data=[], options={"disableClusteringAtZoom":13}).add_to(map)
    marker_bus_cluster = FastMarkerCluster(name='Markers - Bus', data=[], options={"disableClusteringAtZoom":15}).add_to(map)
    marker_navibus_cluster = FastMarkerCluster(name='Markers - Navibus', data=[], options={"disableClusteringAtZoom":12 }).add_to(map)
    
    #Lignes
    default_cluster = MarkerCluster(name='Lines', control=False).add_to(map)
    train_cluster = MarkerCluster(name='Ligne - Tram').add_to(map)
    bus_cluster = MarkerCluster(name='Ligne - Bus').add_to(map)
    navibus_cluster = MarkerCluster(name='Ligne - Navibus').add_to(map)

    for stop_id, stop in data.items():
        
        icons = {'0': 'train', '3': 'bus', '4': 'ship'}
        colors = {'0': 'red', '3': 'lightgray', '4': 'blue'}
       
        #Génération du HTML pour chaque arret
        route_html = "<body style='background-color:rgb(228,228,228);'>"
        html = ""
        for route in stop['routes'].values():
            # Construction de la div pour chaque route
            html += "<div style='width: 50px; height: 50px; background-color:"+ route['route_color'] +"; color: "+ route['route_text_color'] +"; text-align: center; line-height: 50px; font-size: 20px;'>"+ route['route_short_name'] + "</div>"

            # Construction de l'HTML pour le point
            html += "<b>"+ stop['stop_name'] +"</b><br>"
            if route['wheelchair_boarding'] == 1:
                html += "Accessible aux personnes handicapées"
            else:
                html += "PAS Accessible aux personnes handicapées"

            html += "</div><br><br>"

            # Ajout de l'image pour l'arrêt "Haluchère"
            if stop['stop_name'] == "Haluchère-Batignolles":
                # Chemin vers l'image PNG pour l'arrêt "Haluchère"
                image_path = "https://lh5.googleusercontent.com/p/AF1QipPWkomnBlyVrIP1dwKaAqHZs2FIM02S-gBrLUda=w500-h500-k-no"

                # Construction de l'HTML pour le point avec l'image
                html += "<img src='{}' width='100' height='100'><br>".format(image_path)

        route_html += html + "</body>"
        iframe = folium.IFrame(html=route_html, width=300, height=200)

        #Détéction des différents type de points, affichage d'un point pour chaque type de route, bus, tram, navibus, si existant
        route_type_dict = {}
        for route in stop['routes'].values():
            route_type = route['route_type']

            # Vérification s'il y a d'autres route_type
            if route_type not in route_type_dict:
                icon = icons.get(str(route_type), 'question')
                color = colors.get(str(route_type), 'black')
                route_type_dict[route_type] = True  # Marquer le route_type comme déjà ajouté
                if route_type == 0:
                    marker_cluster = marker_train_cluster
                elif route_type == 3:
                    marker_cluster = marker_bus_cluster
                elif route_type == 4:
                    marker_cluster = marker_navibus_cluster
                else:
                    marker_cluster = marker_default_cluster
                folium.Marker(
                        popup=folium.Popup(iframe),
                        location=[route['stop_lat'], route['stop_lon']],
                        icon=folium.Icon(color=color, icon=icon, prefix='fa')
                    ).add_to(marker_cluster)
                
        
    #Affichage des lignes
    for shape_id, group in shapes.groupby('shape_id'):
        points = group[['shape_pt_lat', 'shape_pt_lon']].values.tolist()

        if str(shape_id) in direction_ids and direction_ids[str(shape_id)] == 0:
            if str(shape_id) in trips['shape_id'].astype(str).values:
                trip = trips.loc[trips['shape_id'].astype(str) == str(shape_id)].iloc[0]
                route_id = trip['route_id']
                if str(route_id) in route_colors:
                    route_color = route_colors[str(route_id)]

                    route_type = routes.loc[routes['route_id'] == str(route_id), 'route_type'].values[0]
                    if route_type == 0:
                        line_cluster = train_cluster
                    elif route_type == 3:
                        line_cluster = bus_cluster
                    elif route_type == 4:
                        line_cluster = navibus_cluster
                    else:
                        line_cluster = default_cluster

                    folium.PolyLine(locations=points, color="#"+route_color).add_to(line_cluster)

    #Ajout d'un controller pour tous les clusters
    folium.LayerControl().add_to(map)
    map.save('index.html')
    return map.get_root().render()



if __name__ == "__main__":
    app.run()

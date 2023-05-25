import json
import folium
import pandas as pd
import os
from flask import Flask
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

@app.route("/")
def home():
    #Lectures du fichier JSON 
    with open('clear_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    map = folium.Map(location=[47.2184, -1.5536], zoom_start=12, tiles='cartodbdark_matter')
    
    #Lectures des fichiers CSV 
    routes = pd.read_csv("data/routes.csv", sep=',', usecols=['route_id', 'route_type', 'route_color', 'route_long_name', 'route_short_name', "route_text_color"])
    route_colors = dict(zip(routes['route_id'].astype(str), routes['route_color']))
    trips = pd.read_csv("data/trips.csv", sep=',', usecols=['trip_id', 'route_id', 'shape_id', 'direction_id'])
    shapes = pd.read_csv('data/shapes.csv', usecols=['shape_id', 'shape_pt_lat', 'shape_pt_lon'])
    direction_ids = dict(zip(trips['shape_id'].astype(str), trips['direction_id']))
    
    #Definition des clusters (groupes de lignes ou de points)
    #Markers
    marker_default_cluster = FastMarkerCluster(name='Markers', data=[], control=False).add_to(map)
    marker_train_cluster = FastMarkerCluster(name='Markers - Tram', data=[], options={"disableClusteringAtZoom":13}, show=False).add_to(map)
    marker_bus_cluster = FastMarkerCluster(name='Markers - Bus', data=[], options={"disableClusteringAtZoom":15}, show=False).add_to(map)
    marker_navibus_cluster = FastMarkerCluster(name='Markers - Navibus', data=[], options={"disableClusteringAtZoom":12 }, show=False).add_to(map)
        
    #Lignes
    default_cluster = MarkerCluster(name='Lines', control=False).add_to(map)
    train_cluster = MarkerCluster(name='Ligne - Tram', show=False).add_to(map)
    bus_cluster = MarkerCluster(name='Ligne - Bus', show=False).add_to(map)
    navibus_cluster = MarkerCluster(name='Ligne - Navibus', show=False).add_to(map)

    for stop_id, stop in data.items():
        route_html = "<body style='background-color:rgb(228,228,228);'>"
        html = ""
        icons = {'0': 'train', '3': 'bus', '4': 'ship'}
        colors = {'0': 'red', '3': 'lightgray', '4': 'blue'}
       
        #Nom de l'arret
        html += "<b>" + stop['stop_name'] + "</b><br>"

        # Ajout de l'image pour l'arrêt "Haluchère"
        if stop['stop_name'] == "Haluchère-Batignolles":
            image_path = "https://lh5.googleusercontent.com/p/AF1QipPWkomnBlyVrIP1dwKaAqHZs2FIM02S-gBrLUda=w500-h500-k-no"
            html += "<img src='{}' width='100' height='100'>".format(image_path)

        html += "<h3>Correspondances :</h3>"

        #Add StreetView Image
        # if stop['stop_name'] == "Beaulieu" or stop['stop_name'] == "Ile de Nantes":
            # route_html += "<div>"
            
            # street_view_url = StreetViewService(stop['stop_lat'], stop['stop_lon'], 200, 200)
            # street_view_image = "<img style='width = 100%; height= auto;' class='fit-picture' src='"+street_view_url+"' alt='Photo de l arret de "+stop['stop_name']+"'>" 
            
            # route_html += street_view_image + "</div>"   
        
        for route in stop['routes'].values():

            # Construction de la div pour chaque route
            html += "<br><span><strong>"+route['route_name']+\
                "</strong></span><br><div style='width: 50px; height: 50px; background-color:"+ route['route_color'] +\
                    "; color: "+ route['route_text_color'] +\
                        "; text-align: center; line-height: 50px; font-size: 20px;'>" + route['route_short_name'] +\
                              "</div><span>Wheelchair Boarding : "+str(route['wheelchair_boarding'])+"</span><br>"


        route_html += html + "</body>"
        iframe = folium.IFrame(html=route_html, width=400, height=300)

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
                    route_long_name = routes.loc[routes['route_id'] == str(route_id), 'route_long_name'].values[0]   
                    route_short_name = routes.loc[routes['route_id'] == str(route_id), 'route_short_name'].values[0]    
                    route_text_color = routes.loc[routes['route_id'] == str(route_id), 'route_text_color'].values[0]
                    
                    route_type = routes.loc[routes['route_id'] == str(route_id), 'route_type'].values[0]
                    if route_type == 0:
                        route_type_name = "Tram"
                        line_cluster = train_cluster
                    elif route_type == 3:
                        route_type_name = "Bus"
                        line_cluster = bus_cluster
                    elif route_type == 4:
                        route_type_name = "Navibus"
                        line_cluster = navibus_cluster
                    else:
                        route_type_name = "Aucune idée"
                        line_cluster = default_cluster

                    route_html = "<body style='background-color:rgb(228,228,228);'>"
                    html = ""
                  
                    # Construction de la div pour chaque route
                    html += "<div style='width: 50px; height: 50px; background-color: #"+ str(route_color) +"; color: #"+ str(route_text_color) +"; text-align: center; line-height: 50px; font-size: 20px;'>"+ str(route_short_name) + "</div>"
                    html += "<div><strong>"+str(route_long_name)+"</strong></div>"
                    html += "<div>C'est une ligne de : <strong>"+str(route_type_name)+"</strong></div>"

                    #Popup pour les lignes
                    html += "</div><br><br>"

                    route_html += html + "</body>"
                    iframe = folium.IFrame(html=route_html, width=400, height=100)
                    folium.PolyLine(locations=points, popup=folium.Popup(iframe),color="#"+route_color).add_to(line_cluster)

    #Ajout d'un controller pour tous les clusters
    folium.LayerControl().add_to(map)

    map.get_root().add_child(legend())
    map.save('index.html')
    return map.get_root().render()


def legend():
    from branca.element import Template, MacroElement
    template = """
        {% macro html(this, kwargs) %}

        <!doctype html>
        <html lang="en">
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>TAN</title>
        <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

        <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
        
        <script>
        $( function() {
            $( "#maplegend" ).draggable({
                            start: function (event, ui) {
                                $(this).css({
                                    right: "auto",
                                    top: "auto",
                                    bottom: "auto"
                                });
                            }
                        });
        });

        </script>
        </head>
        <body>

        
        <div id='maplegend' class='maplegend' 
            style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
            border-radius:6px; padding: 10px; font-size:25px; right: 20px; bottom: 20px;'>
            
        <div class='legend-title'><i class="fa-sharp fa-solid fa-location-pin"></i> Légende (draggable)</div>
        <div class='legend-scale'>
        <ul class='legend-labels'>
            <li><i class="fa-solid fa-bus" style="color: #a3a3a3;"></i> Bus</li>
            <li><i class="fa-solid fa-train" style="color: #d33d29;"></i> Tram</li>
            <li><i class="fa-solid fa-ship" style="color: #37a7da;"></i> Navibus</li>
            

        </ul>
        </div>
        </div>
        
        </body>
        </html>

        <style type='text/css'>
        .maplegend .legend-title {
            text-align: left;
            margin-bottom: 5px;
            font-weight: bold;
            font-size: 90%;
            }
        .maplegend .legend-scale ul {
            margin: 0;
            margin-bottom: 5px;
            padding: 0;
            float: left;
            list-style: none;
            }
        .maplegend .legend-scale ul li {
            font-size: 80%;
            list-style: none;
            margin-left: 0;
            line-height: 18px;
            margin-bottom: 2px;
            }
        .maplegend ul.legend-labels li span {
            display: block;
            float: left;
            height: 16px;
            width: 30px;
            margin-right: 5px;
            margin-left: 0;
            border: 1px solid #999;
            }
        .maplegend .legend-source {
            font-size: 80%;
            color: #777;
            clear: both;
            }
        .maplegend a {
            color: #777;
            }
        </style>
        {% endmacro %}"""
  
    macro = MacroElement()
    macro._template = Template(template)
    return macro


def StreetViewService(lat, lng, width, height):
    
    url_image = f"https://maps.googleapis.com/maps/api/streetview?location={lat},{lng}&size={width}x{height}&key={os.getenv('API_KEY')}"
    return url_image

    

if __name__ == "__main__":
    app.run()

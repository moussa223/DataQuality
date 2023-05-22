import pandas as pd
import json

# Charger les fichiers CSV dans des DataFrames
stops_df = pd.read_csv('data/stops.csv')
stop_times_df = pd.read_csv('data/stop_times.csv', dtype={'wheelchair_boarding': str})
trips_df = pd.read_csv('data/trips.csv', dtype={'route_id': str})
routes_df = pd.read_csv('data/routes.csv')
shapes_df = pd.read_csv('data/shapes.csv')

# Créer un DataFrame pour les stops parents en filtrant le DataFrame stops_df
parent_stops_df = stops_df[stops_df['location_type'] == 1]

# Créer un DataFrame pour les stops enfants en filtrant le DataFrame stops_df
child_stops_df = stops_df[stops_df['location_type'] == 0]

# Créer l'objet JSON correspondant à la structure demandée
result = {}

# Parcourir les stops parents
for index, parent_stop_row in parent_stops_df.iterrows():
    parent_stop_id = parent_stop_row['stop_id']
    stop_name = parent_stop_row['stop_name']
    stop_lat = parent_stop_row['stop_lat']
    stop_lon = parent_stop_row['stop_lon']

    result[parent_stop_id] = {
        'stop_id': parent_stop_id,
        'stop_name': stop_name,
        'stop_lat': stop_lat,
        'stop_lon': stop_lon,
        'routes': {}
    }

# Parcourir les stops enfants
for index, child_stop_row in child_stops_df.iterrows():
    stop_id = child_stop_row['stop_id']
    parent_stop_id = child_stop_row['parent_station']

    # Trouver les shape_id correspondant aux coordonnées du stop enfant
    matching_shapes = shapes_df[(shapes_df['shape_pt_lat'] == child_stop_row['stop_lat']) & (shapes_df['shape_pt_lon'] == child_stop_row['stop_lon'])]
    matching_shape_ids = matching_shapes['shape_id'].unique()

    # Trouver les route_id correspondants dans routes_df
    matching_routes = routes_df[routes_df['route_id'].isin(trips_df[trips_df['shape_id'].isin(matching_shape_ids)]['route_id'].unique())]

    # Parcourir les routes correspondantes
    for _, route_row in matching_routes.iterrows():
        route_id = route_row['route_id']
        route_type = route_row['route_type']
        route_name = route_row['route_long_name']
        route_short_name = route_row['route_short_name']
        route_color = route_row['route_color']
        route_text_color = route_row['route_text_color']

        # Trouver la valeur wheelchair_boarding dans stops_df
        stop_info = stops_df[stops_df['stop_id'] == stop_id]
        wheelchair_boarding = stop_info['wheelchair_boarding'].values[0]
        stop_lon = stop_info['stop_lon'].values[0]
        stop_lat = stop_info['stop_lat'].values[0]

        # Ajouter les informations de la route à l'objet JSON
        result[parent_stop_id]['routes'][route_id] = {
            'route_name': route_name,
            'route_type': route_type,
            'route_short_name': "" if str(route_short_name) == "nan" else route_short_name,
            'route_color': "#" + route_color,
            'route_text_color': "#" + route_text_color,
            'wheelchair_boarding': int(wheelchair_boarding),
            'stop_lat': stop_lat,
            'stop_lon': stop_lon
        }

# Trier les routes dans chaque arrêt selon l'ordre de route_type (0, 4, 3)
#Fonction de tri en utilisant l'ordre spécifié
def trier_routes(routes):
    order = [0, 4, 3]
    return sorted(routes.items(), key=lambda x: order.index(x[1]["route_type"]))

# Tri des routes pour chaque élément "BOGE"
for key, value in result.items():
    if "routes" in value:
        value["routes"] = dict(trier_routes(value["routes"]))

# Enregistrer l'objet JSON trié dans un fichier
with open('clear_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(result, json_file, ensure_ascii=False, indent=2, sort_keys=False)

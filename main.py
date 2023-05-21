import folium
import pandas as pd
import haversine as hs
from flask import Flask
from folium.plugins import MarkerCluster

app = Flask(__name__)
def find_connections(stop_tuple, shapes_csv, trips_csv, routes_csv) {
    stop_lat = stop_tuple[1].loc['stop_lat']
    stop_lon = stop_tuple[1].loc['stop_lon']
    stop_coordinates = (stop_lat,stop_lon)
    
    for shape_id, group in shapes.groupby('shape_id'):
        points = group[['shape_pt_lat', 'shape_pt_lon']].values.tolist()
        for (point in points):
            distance_between_stop_and_point = hs.haversine(point_coordinates,stop_coordinates,unit=Unit.METERS)
            if (distance_between_stop_and_point <= 3):
                #On regarde la ligne qui correspond au shape_id
                line_attached_to_shape_id = trips[trips['shape_id'] == shape_id].iloc
                break
}

@app.route("/")
def tan_map():
    stops = pd.read_csv("data/stops.csv", sep = ',')
    shapes = pd.read_csv('data/shapes.csv')
    trips = pd.read_csv('data/trips.csv')
    routes = pd.read_csv('data/routes.csv')
    direction_ids = dict(zip(trips['shape_id'].astype(str), trips['direction_id']))
    route_colors = dict(zip(routes['route_id'].astype(str), routes['route_color']))
    
    map = folium.Map(location=[47.2184, -1.5536], zoom_start=12, tiles='cartodbdark_matter')

    marker_cluster = MarkerCluster(name='Markers').add_to(map)
    line_cluster = MarkerCluster(name='Lines').add_to(map)

    for index, stop in stops.iterrows():
        if stop['location_type']:
            marker_popup = '''<h1>{stop_name}</h1>\n'''
            folium.Marker(location=[stop['stop_lat'], stop['stop_lon']],
                      popup=stop['stop_name'],
                      icon=folium.Icon(color='blue', icon='bus', prefix='fa')
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

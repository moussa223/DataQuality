import folium
import pandas as pd
from flask import Flask
from folium.plugins import MarkerCluster

app = Flask(__name__)

@app.route("/")
def tan_map():
    stops = pd.read_csv("data/stops.csv", sep = ',')
    shapes = pd.read_csv('data/shapes.csv')
    trips = pd.read_csv('data/trips.csv')
    direction_ids = dict(zip(trips['shape_id'].astype(str), trips['direction_id']))

    map = folium.Map(location=[47.2184, -1.5536], zoom_start=12)
    
    marker_cluster = MarkerCluster(name='Markers').add_to(map)

    for index, stop in stops.iterrows():
        if stop['location_type']:
            folium.Marker(location=[stop['stop_lat'], stop['stop_lon']],
                      popup=stop['stop_name'],
                      icon=folium.Icon(color='blue', icon='bus', prefix='fa')
                    ).add_to(marker_cluster)

    for shape_id, group in shapes.groupby('shape_id'):
        points = group[['shape_pt_lat', 'shape_pt_lon']].values.tolist()

        if str(shape_id) in direction_ids and direction_ids[str(shape_id)] == 0:
            folium.PolyLine(locations=points, color='red').add_to(map)

    folium.LayerControl().add_to(map)
    map.save('index.html')
    return map.get_root().render()

if __name__ == "__main__":
    app.run()

import folium
import pandas as pd
from flask import Flask
from folium.plugins import MarkerCluster


app = Flask(__name__)

@app.route("/")
def tan_map():
    # Chargement des données Opendata de la ville de Nantes pour les arrêts de bus
    arrets_bus = pd.read_csv("data/stops.csv", sep = ',')


    # création d'une carte follium centrée sur Nantes
    map = folium.Map(location=[47.2184, -1.5536], zoom_start=12)
    
    marker_cluster = MarkerCluster(name='Markers').add_to(map)

    for index, row in arrets_bus.iterrows():
        if row['location_type']:
            folium.Marker(location=[row['stop_lat'], row['stop_lon']],
                      popup=row['stop_name'],
                      icon=folium.Icon(color='blue', icon='bus', prefix='fa')
                    ).add_to(marker_cluster)

    folium.LayerControl().add_to(map)
    map.save('index.html')
    return map.get_root().render()


if __name__ == "__main__":
    app.run()

import folium
import pandas as pd

# Chargement des données Opendata de la ville de Nantes pour les arrêts de bus
arrets_bus = pd.read_csv("C:/Users/mm682/Downloads/stopsCsvTest.csv", sep = ',')

# création d'une carte follium centrée sur Nantes
m = folium.Map(location=[47.2184, -1.5536], zoom_start=12)

for index, row in arrets_bus.iterrows():
    folium.Marker(location=[row['stop_lat'], row['stop_lon']],
                  popup=row['stop_name'],
                  icon=folium.Icon(color='blue', icon='bus', prefix='fa')
                 ).add_to(m)

m.save('C:/Users/mm682/Downloads/carte_arrets.html')


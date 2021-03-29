import folium
from geojson import Feature, FeatureCollection, LineString
import os
import requests
import json
from dotenv import load_dotenv


load_dotenv('./.env')
key = os.getenv('api_key')
endpoints = []  # contains the start and endpoint of a route (maps call)
routes = []  # contains n geo-values which describe the route in detail (maps response)
with open('data/bike_routes.csv', 'r') as file:
    for line in file:
        endpoints.append(line.split(','))

len(endpoints)

routes = []
for endpoint in endpoints[:15]:
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={endpoint[2]},{endpoint[1]}&destination={endpoint[5]},{endpoint[4]}&avoid=highways&mode=bicycling&key={key}'
    resp = requests.get(url)
    # # TODO: if status_code == 200 oder sowas hier einbauen
    json_text = resp.json()
    steps = json_text['routes'][0]['legs'][0]['steps']
    route = []
    route.append([float(endpoint[1]), float(endpoint[2])])
    for step in steps:
        lat = step['end_location']['lat']
        lng = step['end_location']['lng']
        coord = [lng, lat]
        route.append(coord)

    routes.append(route)

# %%
feature_list = []
for route in routes:
    feature = Feature(geometry=LineString(route))
    feature_list.append(feature)

feature_collection = FeatureCollection(feature_list)
feature_collection

map = folium.Map(
    location=[50.9411228, 6.9409058],
    zoom_start=11.5,
    tiles='Stamen Toner',
)
folium.GeoJson(feature_collection, name='pew').add_to(map)
map

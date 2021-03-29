import os
import requests
import json
from dotenv import load_dotenv
from geojson import Feature, FeatureCollection, LineString


def call_directions_api(start_lat, start_lng, end_lat, end_lng):
    """
    Calls the Google Maps Directions API with longitude and latitude values
    for the starting location and destination.

    Returns a list of every waypoint of the calculated route including passed
    start_lng and start_lat as first values of that list. end_lng and end_lat
    might differ as the last values of the route are taken from the response.

    The Directions API might respond with more than one route, if there are
    alternative routes available. In this care the first will be returned.

    Also, since this function is used to calucate bike routes, additional
    paramenters are set. Those are:
    - avoid: highways and ferries (duh!)
    - mode: bicycling

    :start_lng: float
    :start_lat: float
    :end_lng: float
    :end_lat: float
    :resp_form: Accepted values xml and json. Default is json.
    """

    # set defaults. TODO: ist das mit dem API key hier richtig, oder pass?
    load_dotenv('./.env')
    key = os.getenv('api_key')
    avoid = 'highways|ferries'
    mode = 'bicycling'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lng}&destination={end_lat},{end_lng}&avoid={avoid}&mode={mode}&key={key}'
    resp = requests.get(url)
    # # TODO: if status_code == 200 oder sowas hier einbauen
    json_text = resp.json()
    route = []
    # Kinda confusing: API Calls expects (lat,lng). GeoJSON does [lng,lat] :(
    route.append([start_lng, start_lat])
    steps = json_text['routes'][0]['legs'][0]['steps']
    for step in steps:
        lat = step['end_location']['lat']
        lng = step['end_location']['lng']
        coord = [lng, lat]
        route.append(coord)

    return route


def read_routes_csv(path):
    file = []
    with open(path, 'r') as f:
        for line in f:
            file.append(line.split(','))
    return file


def create_geojson_line(route):
    """
    Converts a list of coordinates into a geoJSON Feature
    """
    return Feature(geometry=LineString(route))


def create_feature_collection(feature_list):
    return FeatureCollection(feature_list)


if __name__ == '__main__':
    load_dotenv('./.env')
    key = os.getenv('api_key')

    # this file contains starting and destination coordinates
    bike_routes = read_routes_csv('data/bike_routes.csv')
    routes_with_waypoints = []
    for bike_route in bike_routes[:15]:  # safety net for not calling 55k times
        routes_with_waypoints.append(call_directions_api(
            start_lat=float(bike_route[2]),
            start_lng=float(bike_route[1]),
            end_lat=float(bike_route[5]),
            end_lng=float(bike_route[4])
        ))

    feature_list = []
    for route_with_waypoints in routes_with_waypoints:
        feature_list.append(create_geojson_line(route_with_waypoints))

    feature_collection = create_feature_collection(feature_list)

    with open('data/feature_collection.json', 'w') as f:
        f.write(json.dumps(feature_collection))

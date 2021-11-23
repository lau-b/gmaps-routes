import os
import requests
import json
from tqdm import tqdm
from dotenv import load_dotenv
from geojson import Feature, FeatureCollection, LineString, Point, MultiLineString


def call_directions_api(start_lat: float, start_lng: float, end_lat: float, end_lng: float):
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
    """

    # set defaults.
    load_dotenv('./.env')
    key = os.getenv('api_key')
    avoid = 'highways|ferries'
    mode = 'bicycling'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lng}&destination={end_lat},{end_lng}&avoid={avoid}&mode={mode}&key={key}'
    resp = requests.get(url)

    if resp.status_code == 200:
        json_text = resp.json()
        route = []
        route.append([start_lng, start_lat])
        steps = json_text['routes'][0]['legs'][0]['steps']
        for step in steps:
            lat = step['end_location']['lat']
            lng = step['end_location']['lng']
            coord = [lng, lat]
            route.append(coord)
            # return route # TODO: do not return here but after the route list is complete. Put return after the else statement
    else:
        print(f'Something went wrong: {resp.status_code}')
        # TODO: Add emegency safe if something goes wrong
        return 'the api didnt answer'# return nothing here because otherwise an empty list would be returned

    return route

def read_csv(path):
    file = []
    with open(path, 'r') as f:
        for line in f:
            file.append(line.split(','))
    return file


def create_geojson_line(route, properties):
    """
    Converts a list of coordinates into a geoJSON Feature
    """
    return Feature(geometry=LineString(route), properties=properties)

def create_geojson_multiline(route, properties):
    return Feature(geometry=MultiLineString(route), properties=properties)

def create_geojson_point(lat, lng):
    return Feature(geometry=Point((lng, lat)))


def create_feature_collection(feature_list):
    return FeatureCollection(feature_list)


if __name__ == '__main__':
    load_dotenv('./.env')
    key = os.getenv('api_key')

    bike_routes = read_csv('data/bike_routes_20210301_20210314.csv')
    routes_with_waypoints = []
    for bike_route in tqdm(bike_routes):
        route_with_waypoints = call_directions_api(
            start_lat=float(bike_route[2]),
            start_lng=float(bike_route[1]),
            end_lat=float(bike_route[5]),
            end_lng=float(bike_route[4])
        )
        if type(route_with_waypoints) == list:
            routes_with_waypoints.append(
                [route_with_waypoints,
                {'bike_name': bike_route[0], 'tour_start_at': bike_route[3]}
            ])
        else:
            # I should probably include logging at this point
            pass

    feature_list = []
    for route_with_waypoints in routes_with_waypoints:
        coords = route_with_waypoints[0]
        props = route_with_waypoints[1]
        feature_list.append(create_geojson_line(coords, props))
        # feature_list.append(create_geojson_multiline(coords, props))

    feature_collection = create_feature_collection(feature_list)

    with open('data/routes_20210301_20210314.json', 'w') as f:
        f.write(json.dumps(feature_collection))


    # bike_parking_spots = read_csv('data/coords_heatmap.csv')
    # points_list = []
    # for spot in bike_parking_spots[:1000]:
    #     points_list.append(create_geojson_point(float(spot[0]), float(spot[1])))

    # feature_coll_points = create_feature_collection(points_list)
    # with open('data/feature_collection_points.json', 'w') as f:
    #     f.write(json.dumps(feature_coll_points))

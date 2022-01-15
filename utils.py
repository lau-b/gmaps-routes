# This file contains some self defined functions used by routes.py

import os
import random
import requests
#from tqdm import tqdm
from dotenv import load_dotenv
from geojson import (Feature, FeatureCollection, LineString,
                     Point, MultiLineString)
from sqlalchemy import create_engine
import psycopg2

def call_directions_api(start_lat: float, start_lng: float,end_lat: float,
                        end_lng: float, iteration):
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
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin=\
        {start_lat},{start_lng}\
            &destination={end_lat},{end_lng}\
                &avoid={avoid}\
                    &mode={mode}\
                        &key={key}'
    resp = requests.get(url)

    if resp.status_code == 200:
        print('OK status 200. Iteration num', iteration)
        json_text = resp.json()
        print(json_text)
        route = []
        route.append([start_lng, start_lat])
        steps = json_text['routes'][0]['legs'][0]['steps']
        for step in steps:
            lat = step['end_location']['lat']
            lng = step['end_location']['lng']
            coord = [lng, lat]
            route.append(coord)
    else:
        print(f'Something went wrong: {resp.status_code}')
        #TODO: Add emegency safe if something goes wrong

    return route

def read_csv(path: str) -> list:
    """ reads a csv file and returns a list of lists in which the
        each element is a data point
    """
    file = []
    with open(path, 'r') as docu:
        for line in docu:
            file.append(line.split(','))
    return file


def create_geojson_line(route, properties):
    """
    Converts a list of coordinates into a geoJSON Feature
    """
    return Feature(geometry=LineString(route), properties=properties)

def create_geojson_multiline(route, properties):
    '''Wrapper function. route is a list of coordinates and properties is a dict.
       Returns a geojson Feature object'''
    return Feature(geometry=MultiLineString(route), properties=properties)

def create_geojson_point(lat, lng):
    """wrapper function. lat and lng are floats. Return geojson object"""
    return Feature(geometry=Point((lng, lat)))


def create_feature_collection(feature_list: list):
    """wrapper function. feature_list is a list of Features.
        Return geojson object"""
    return FeatureCollection(feature_list)

def random_locations (start_lat: float, start_lng: float, end_lat: float,
                      end_lng: float, number_of_steps) -> list:
    ''' randomize a int number of waypoints (steps) between 3 and 10.
        For each int number generate a pair [lng lat] where lng between start_lng and end_lng;
        and lat is between start_lat and end_lat.
        Returns route which is a list of lists
    '''
    route = []
    route.append([start_lng, start_lat])
    for step in range(number_of_steps):
        rand_lng = round(random.uniform(start_lng, end_lng), 6)
        rand_lat = round(random.uniform(start_lat, end_lat), 6)
        coords = [rand_lng, rand_lat]
        route.append(coords)
    return route

def insert_json_routes(json_features: list, conn_string):
    """insert in table json_routes a row with json file of the route"""
    sql = '''   INSERT INTO json_routes(bike_name, start_at, route)
                VALUES(%s, %s, %s);'''
    try:
        eng = create_engine(conn_string)
        with eng.connect() as con:
            print('engine connected')
            for json_feature in json_features:
                bike_name = json_feature['properties']['bike_name']
                start_at = json_feature['properties']['tour_start_at']
                con.execute(sql, bike_name, start_at, str(json_feature))
        print('executed engine')
    except (Exception, psycopg2.DatabaseError) as error:
        print('Attention!', error)


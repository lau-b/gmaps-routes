import os
import random
import requests
#from tqdm import tqdm
from dotenv import load_dotenv
from geojson import (Feature, FeatureCollection, LineString,
                     Point, MultiLineString)
from sqlalchemy import create_engine
import psycopg2

# import utility files
from utils import random_locations
from utils import create_geojson_line
from utils import insert_json_routes
from utils import call_directions_api

# SQL queries
routes_query = """  SELECT  bike_number,
                            starting_lng,
                            starting_lat,
                            route_started_at,
                            destination_lng,
                            destination_lat,
                            destination_time
                    FROM "./models/kvb/schema".bike_routes
                    WHERE bike_routes IS NOT NULL
                    LIMIT 10;
               """

if __name__ == '__main__':

    # load environmental variables for api and postgres
    load_dotenv('./.env')
    key = os.getenv('api_key')

    host = os.getenv('host')
    user = os.getenv('user')
    port = os.getenv('port')
    db = os.getenv('db')
    password = os.getenv('password')

    # connect to postgreSQL
    connection_string = f'postgresql://{user}:{password}@{host}:{port}/{db}'

    engine = create_engine(connection_string)

    # populate sqlalchemy engine cursor
    with engine.connect() as con:
        rs = con.execute(routes_query)

    # transfer information of cursor in python list of dictionaries
    bike_routes = []
    routes_with_waypoints = []

    for row in rs:
        routes_dict = {}
        routes_dict = {
                'bike_number': row[0],
                'starting_lng': row[1],
                'starting_lat': row[2],
                'starting_time': row[3].strftime("%Y-%m-%d %H:%M:%S.%f"),
                'destination_lng': row[4],
                'destination_lat': row[5],
                'destination_time': row[6].strftime("%Y-%m-%d %H:%M:%S.%f")
        }
        bike_routes.append(routes_dict) #bike_routes is a list of dicts

        # create routes with random waypoints
        number_of_steps = random.randint(3, 10)
        route_with_waypoints = random_locations(
                                start_lat = float(routes_dict['starting_lat']),
                                start_lng = float(routes_dict['starting_lng']),
                                end_lat = float(routes_dict['destination_lat']),
                                end_lng = float(routes_dict['destination_lng']),
                                number_of_steps = number_of_steps
        )

        # create routes with api waypoints
        #route_with_waypoints = call_directions_api(
                  # start_lat = float(routes_dict['starting_lat']),
                  # start_lng = float(routes_dict['starting_lng']),
                  # end_lat = float(routes_dict['destination_lat']),
                  # end_lng = float(routes_dict['destination_lng']),
                  # iteration = iteration
        #)

        if isinstance(route_with_waypoints, list):
            # append all routes with waypoints on a list
            routes_with_waypoints.append([route_with_waypoints,
                        {'bike_name': routes_dict['bike_number'],
                        'tour_start_at': routes_dict['starting_time']}])
        else:
            print("Is not list")

    features = []
    for route_with_waypoints in routes_with_waypoints:
        coords = route_with_waypoints[0]
        props = route_with_waypoints[1]
        # populate a list with json features
        features.append(create_geojson_line(coords, props))

    #print('\n\n',features[0])
    # append json features in a table (called json_routes)
    insert_json_routes(features, connection_string)

